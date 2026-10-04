"""Shared state IO for the overnight queue runner.

Design: Plans/overnight-queue-runner.md.

- queue.yaml is user-authored (spec). Never written by the runner.
- queue.status.json is runner-owned bookkeeping. Status keyed by entry id.
- Atomic writes (tmp + rename) for any runner-owned file.
- queue.lock is held with flock; the OS releases it when the runner exits.
"""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_TIMEOUT_SECONDS = 14400  # 4h


@dataclass
class QueueEntry:
    id: str
    cmd: str
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    expect_outputs: list[str] = field(default_factory=list)
    track: str | None = None
    notes: str | None = None
    parallel_group: int | None = None  # entries with same group run concurrently

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "QueueEntry":
        if "id" not in d or "cmd" not in d:
            raise ValueError(f"queue entry missing required id/cmd: {d!r}")
        pg = d.get("parallel_group")
        return cls(
            id=str(d["id"]),
            cmd=str(d["cmd"]),
            timeout_seconds=int(d.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)),
            expect_outputs=list(d.get("expect_outputs", []) or []),
            track=d.get("track"),
            notes=d.get("notes"),
            parallel_group=int(pg) if pg is not None else None,
        )


def load_queue(path: Path) -> list[QueueEntry]:
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    raw_entries = data if isinstance(data, list) else data.get("runs", [])
    entries = [QueueEntry.from_dict(e) for e in raw_entries]
    seen: set[str] = set()
    for e in entries:
        if e.id in seen:
            raise ValueError(f"duplicate queue entry id: {e.id}")
        seen.add(e.id)
    return entries


def load_status(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_status(path: Path, status: dict[str, dict[str, Any]]) -> None:
    """Atomic write: tmp + rename. Never leaves the file half-updated."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(status, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def pending_entries(
    queue: list[QueueEntry], status: dict[str, dict[str, Any]]
) -> list[QueueEntry]:
    """Entries with no recorded status, or recorded status is queued/running.

    'running' in saved status means the last runner was interrupted — on
    restart we reclassify to 'interrupted' (caller's responsibility) and
    treat as not pending. Caller invokes reclassify_running() before this.
    """
    terminal = {"done", "failed", "timeout", "interrupted", "suspicious"}
    return [e for e in queue if status.get(e.id, {}).get("status") not in terminal]


def group_entries(entries: list[QueueEntry]) -> list[list[QueueEntry]]:
    """Group entries by parallel_group. Entries with no group each form a
    solo group. Consecutive entries with the same group number are batched
    together. Non-consecutive entries with the same group number form
    separate batches (preserves queue ordering intent)."""
    groups: list[list[QueueEntry]] = []
    current_group: list[QueueEntry] = []
    current_pg: int | None = None

    for entry in entries:
        if entry.parallel_group is None:
            # Solo entry — flush any current group first
            if current_group:
                groups.append(current_group)
                current_group = []
                current_pg = None
            groups.append([entry])
        elif entry.parallel_group == current_pg:
            # Same group — accumulate
            current_group.append(entry)
        else:
            # New group — flush previous
            if current_group:
                groups.append(current_group)
            current_group = [entry]
            current_pg = entry.parallel_group

    if current_group:
        groups.append(current_group)

    return groups


def reclassify_running(status: dict[str, dict[str, Any]]) -> list[str]:
    """Any 'running' in saved status means the previous runner didn't shut down
    cleanly. Reclassify to 'interrupted'. Returns list of affected ids."""
    affected = []
    for entry_id, s in status.items():
        if s.get("status") == "running":
            s["status"] = "interrupted"
            s["reclassified_from_running"] = True
            affected.append(entry_id)
    return affected


class LockError(Exception):
    pass


# Open lock files, keyed by path, so the flock outlives acquire_lock().
_LOCK_FDS: dict[Path, int] = {}


def acquire_lock(path: Path) -> None:
    """Exclusive flock on the lock file. Refuse if another process holds it.

    The OS drops the lock when the holder exits, so a lock left by a crashed
    runner never blocks the next one. The file itself is kept (unlinking a
    flock file lets two processes lock different inodes); it records the
    holder's PID for humans.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        try:
            holder = os.read(fd, 64).decode().strip() or "unknown"
        finally:
            os.close(fd)
        raise LockError(
            f"queue.lock held by live PID {holder}; "
            f"refusing to start a second runner"
        )
    os.ftruncate(fd, 0)
    os.write(fd, f"{os.getpid()}\n".encode())
    _LOCK_FDS[path] = fd


def release_lock(path: Path) -> None:
    fd = _LOCK_FDS.pop(path, None)
    if fd is None:
        return
    try:
        os.ftruncate(fd, 0)
        fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass
    finally:
        os.close(fd)
