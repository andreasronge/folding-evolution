"""Shared state IO for the overnight queue runner.

Design: Plans/overnight-queue-runner.md.

- queue.yaml is user-authored (spec). Never written by the runner.
- queue.status.json is runner-owned bookkeeping. Status keyed by entry id.
- Atomic writes (tmp + rename) for any runner-owned file.
- queue.lock is a PID file; stale locks (dead PID) are reclaimed with a warning.
"""

from __future__ import annotations

import errno
import json
import os
import sys
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

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "QueueEntry":
        if "id" not in d or "cmd" not in d:
            raise ValueError(f"queue entry missing required id/cmd: {d!r}")
        return cls(
            id=str(d["id"]),
            cmd=str(d["cmd"]),
            timeout_seconds=int(d.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)),
            expect_outputs=list(d.get("expect_outputs", []) or []),
            track=d.get("track"),
            notes=d.get("notes"),
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


def acquire_lock(path: Path) -> None:
    """PID lock. Refuse if lock is held by a live process. Reclaim stale locks.

    On success, writes this process's PID to the file and does not return
    until release_lock() is called.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            existing_pid = int(path.read_text().strip())
        except (ValueError, OSError):
            existing_pid = None
        if existing_pid is not None and _pid_alive(existing_pid):
            raise LockError(
                f"queue.lock held by live PID {existing_pid}; "
                f"refusing to start a second runner"
            )
        # stale lock — reclaim
        print(
            f"[queue_lib] reclaiming stale lock (previous PID "
            f"{existing_pid} not alive)",
            file=sys.stderr,
        )
    path.write_text(f"{os.getpid()}\n")


def release_lock(path: Path) -> None:
    try:
        if path.exists():
            recorded = path.read_text().strip()
            if recorded == str(os.getpid()):
                path.unlink()
    except OSError:
        pass


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # process exists but owned by another user — treat as alive
        return True
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False
        raise
    return True
