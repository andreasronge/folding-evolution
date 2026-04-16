"""Overnight queue runner — phase 1.

Runs every queue.yaml entry whose id is not in queue.status.json as a
terminal status (done/failed/timeout/interrupted/suspicious). Writes
per-run output to experiments/output/YYYY-MM-DD/<id>/ including subprocess
rusage profile.

Phase 2 (Claude CLI summarization) is a separate script.

Design: Plans/overnight-queue-runner.md.

Typical usage:
    caffeinate -s python scripts/run_queue.py

Lock + signal behavior:
- Refuses to start if queue.lock held by a live PID.
- First SIGINT: forward to child, short grace period, mark 'interrupted', exit.
- Second SIGINT: SIGKILL child, best-effort status write, exit.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from queue_lib import (  # noqa: E402
    LockError,
    QueueEntry,
    acquire_lock,
    group_entries,
    load_queue,
    load_status,
    pending_entries,
    reclassify_running,
    release_lock,
    save_status,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUEUE = REPO_ROOT / "queue.yaml"
DEFAULT_STATUS = REPO_ROOT / "queue.status.json"
DEFAULT_LOCK = REPO_ROOT / "queue.lock"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "experiments" / "output"
SIGTERM_GRACE_SECONDS = 10


def _display_path(path: Path) -> str:
    """Repo-relative path when possible, absolute otherwise (e.g. under /tmp)."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


class _InterruptState:
    """Shared mutable state for signal handlers."""

    interrupts_received = 0
    current_child: subprocess.Popen | None = None


def _install_signal_handlers(state: _InterruptState) -> None:
    def handler(signum: int, _frame: Any) -> None:
        state.interrupts_received += 1
        child = state.current_child
        if child is None:
            print(f"[run_queue] signal {signum}, no active child, exiting", file=sys.stderr)
            return
        if state.interrupts_received == 1:
            print(
                f"[run_queue] signal {signum}, forwarding SIGTERM to child PID {child.pid}",
                file=sys.stderr,
            )
            try:
                child.terminate()
            except ProcessLookupError:
                pass
        else:
            print(
                f"[run_queue] second interrupt, SIGKILL child PID {child.pid}",
                file=sys.stderr,
            )
            try:
                child.kill()
            except ProcessLookupError:
                pass

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


def _git_commit() -> tuple[str | None, bool]:
    try:
        rev = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
        dirty_out = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        )
        return rev, bool(dirty_out.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, False


def _rusage_snapshot(before: resource.struct_rusage) -> dict[str, float | int]:
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    user = after.ru_utime - before.ru_utime
    sysc = after.ru_stime - before.ru_stime
    # ru_maxrss is KiB on Linux, bytes on macOS; normalize to MB
    raw_maxrss = after.ru_maxrss
    if sys.platform == "darwin":
        peak_rss_mb = raw_maxrss / (1024 * 1024)
    else:
        peak_rss_mb = raw_maxrss / 1024
    return {
        "user_cpu_seconds": round(user, 3),
        "sys_cpu_seconds": round(sysc, 3),
        "peak_rss_mb": round(peak_rss_mb, 1),
        "voluntary_ctxt_switches": after.ru_nvcsw - before.ru_nvcsw,
        "involuntary_ctxt_switches": after.ru_nivcsw - before.ru_nivcsw,
    }


def _determine_status(
    returncode: int | None,
    timed_out: bool,
    interrupted: bool,
    run_dir: Path,
    expect_outputs: list[str],
) -> str:
    if interrupted:
        return "interrupted"
    if timed_out:
        return "timeout"
    if returncode != 0:
        return "failed"
    missing = [o for o in expect_outputs if not (run_dir / o).exists()]
    if missing:
        return "suspicious"
    return "done"


def _run_entry(
    entry: QueueEntry,
    run_dir: Path,
    state: _InterruptState,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    metadata_path = run_dir / "metadata.json"

    commit, dirty = _git_commit()
    start_wall = time.time()
    start_iso = dt.datetime.now(dt.timezone.utc).isoformat()

    metadata: dict[str, Any] = {
        "id": entry.id,
        "queue_entry": {
            "id": entry.id,
            "cmd": entry.cmd,
            "timeout_seconds": entry.timeout_seconds,
            "expect_outputs": entry.expect_outputs,
            "track": entry.track,
            "notes": entry.notes,
        },
        "git_commit": commit,
        "git_dirty": dirty,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "started_at": start_iso,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))

    env = dict(os.environ)
    env.setdefault("PYTHONUNBUFFERED", "1")
    # Pin Rayon to one thread per worker. With multi-worker sweeps each
    # Python worker otherwise spawns num_cpus Rayon threads, and N workers
    # × num_cpus threads oversubscribe the cores. One thread per worker
    # lets the outer Pool provide the parallelism.
    env.setdefault("RAYON_NUM_THREADS", "1")
    # Experiments should write outputs (result.json, plots, etc.) into
    # $RUN_DIR. The runner checks expect_outputs relative to run_dir.
    env["RUN_DIR"] = str(run_dir.resolve())

    rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

    returncode: int | None = None
    timed_out = False
    interrupted_before_this_run = state.interrupts_received

    with stdout_path.open("w") as out_f, stderr_path.open("w") as err_f:
        # shell=True so users can write pipe-style cmds in the queue entry.
        # The queue is user-authored and trusted.
        proc = subprocess.Popen(
            entry.cmd,
            shell=True,
            cwd=REPO_ROOT,
            stdout=out_f,
            stderr=err_f,
            env=env,
        )
        state.current_child = proc
        try:
            returncode = proc.wait(timeout=entry.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            print(
                f"[run_queue] {entry.id} exceeded {entry.timeout_seconds}s, SIGTERM",
                file=sys.stderr,
            )
            try:
                proc.terminate()
            except ProcessLookupError:
                pass
            try:
                returncode = proc.wait(timeout=SIGTERM_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                print(f"[run_queue] {entry.id} did not exit after SIGTERM, SIGKILL", file=sys.stderr)
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                try:
                    returncode = proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    returncode = None
        finally:
            state.current_child = None

    end_wall = time.time()
    rusage = _rusage_snapshot(rusage_before)
    wall_seconds = round(end_wall - start_wall, 3)
    cpu_efficiency = (
        round(rusage["user_cpu_seconds"] / wall_seconds, 2) if wall_seconds > 0 else None
    )

    interrupted = state.interrupts_received > interrupted_before_this_run and not timed_out

    status = _determine_status(
        returncode=returncode,
        timed_out=timed_out,
        interrupted=interrupted,
        run_dir=run_dir,
        expect_outputs=entry.expect_outputs,
    )

    metadata.update(
        {
            "ended_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "exit_code": returncode,
            "status": status,
            "wall_seconds": wall_seconds,
            "profile": {
                "wall_seconds": wall_seconds,
                **rusage,
                "cpu_efficiency": cpu_efficiency,
            },
        }
    )
    metadata_path.write_text(json.dumps(metadata, indent=2))
    return metadata


def _validate(queue_path: Path, status_path: Path) -> int:
    """Parse queue.yaml, check it, print a brief plan. Exit non-zero on issues."""
    try:
        queue = load_queue(queue_path)
    except Exception as e:
        print(f"[validate] FAIL: could not load {queue_path}: {e}", file=sys.stderr)
        return 1

    issues: list[str] = []
    for entry in queue:
        if not entry.cmd.strip():
            issues.append(f"{entry.id}: empty cmd")
        if entry.timeout_seconds <= 0:
            issues.append(f"{entry.id}: non-positive timeout_seconds")
        for out in entry.expect_outputs:
            if Path(out).is_absolute() or ".." in Path(out).parts:
                issues.append(
                    f"{entry.id}: expect_outputs should be relative to $RUN_DIR "
                    f"(got {out!r})"
                )

    status = load_status(status_path)
    terminal = {"done", "failed", "timeout", "interrupted", "suspicious"}
    pending = [e for e in queue if status.get(e.id, {}).get("status") not in terminal]
    done_count = sum(1 for e in queue if status.get(e.id, {}).get("status") == "done")

    print(f"[validate] {queue_path}: {len(queue)} entries, {done_count} already done, "
          f"{len(pending)} pending")
    if pending:
        groups = group_entries(pending)
        print(f"[validate] would run ({len(groups)} group(s)):")
        for group in groups:
            if len(group) == 1:
                e = group[0]
                track = f" [{e.track}]" if e.track else ""
                print(f"  - {e.id}{track}  (timeout {e.timeout_seconds}s)")
            else:
                pg = group[0].parallel_group
                print(f"  ┌ parallel_group={pg}:")
                for e in group:
                    track = f" [{e.track}]" if e.track else ""
                    print(f"  │ {e.id}{track}  (timeout {e.timeout_seconds}s)")
                print(f"  └ ({len(group)} entries run concurrently)")

    if issues:
        print(f"[validate] FAIL: {len(issues)} issue(s):", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)
        return 1

    print("[validate] OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Overnight experiment queue runner")
    ap.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    ap.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    ap.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    ap.add_argument(
        "--validate",
        action="store_true",
        help="parse queue.yaml and report issues, then exit. Runs nothing.",
    )
    args = ap.parse_args()

    if not args.queue.exists():
        print(f"[run_queue] no queue at {args.queue}", file=sys.stderr)
        return 2

    if args.validate:
        return _validate(args.queue, args.status)

    queue = load_queue(args.queue)
    status = load_status(args.status)

    reclassified = reclassify_running(status)
    if reclassified:
        print(
            f"[run_queue] reclassified stuck 'running' entries as 'interrupted': {reclassified}",
            file=sys.stderr,
        )
        save_status(args.status, status)

    pending = pending_entries(queue, status)
    if not pending:
        print("[run_queue] nothing pending")
        return 0

    try:
        acquire_lock(args.lock)
    except LockError as e:
        print(f"[run_queue] {e}", file=sys.stderr)
        return 3

    state = _InterruptState()
    _install_signal_handlers(state)

    date_dir = args.output_root / dt.date.today().isoformat()
    groups = group_entries(pending)
    parallel_count = sum(1 for g in groups if len(g) > 1)
    print(
        f"[run_queue] {len(pending)} entries in {len(groups)} group(s) "
        f"({parallel_count} parallel); output root: {date_dir}"
    )

    try:
        for group in groups:
            if state.interrupts_received > 0:
                print("[run_queue] interrupt seen, stopping queue", file=sys.stderr)
                break

            if len(group) == 1:
                # --- Sequential (single entry) ---
                entry = group[0]
                run_dir = date_dir / entry.id
                status[entry.id] = {
                    "status": "running",
                    "run_dir": _display_path(run_dir),
                    "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                }
                save_status(args.status, status)

                print(f"[run_queue] START {entry.id}  ({entry.cmd})")
                metadata = _run_entry(entry, run_dir, state)

                status[entry.id] = {
                    "status": metadata["status"],
                    "run_dir": _display_path(run_dir),
                    "started_at": metadata["started_at"],
                    "ended_at": metadata["ended_at"],
                    "wall_seconds": metadata["wall_seconds"],
                    "exit_code": metadata["exit_code"],
                }
                save_status(args.status, status)
                print(
                    f"[run_queue] END   {entry.id}  status={metadata['status']}  "
                    f"wall={metadata['wall_seconds']}s  exit={metadata['exit_code']}"
                )
            else:
                # --- Parallel (multiple entries in same group) ---
                pg = group[0].parallel_group
                ids = [e.id for e in group]
                print(
                    f"[run_queue] PARALLEL GROUP {pg}: starting {len(group)} entries "
                    f"concurrently: {ids}"
                )
                import concurrent.futures

                for entry in group:
                    status[entry.id] = {
                        "status": "running",
                        "run_dir": _display_path(date_dir / entry.id),
                        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    }
                save_status(args.status, status)

                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=len(group)
                ) as pool:
                    futures = {
                        pool.submit(
                            _run_entry, entry, date_dir / entry.id, state
                        ): entry
                        for entry in group
                    }
                    for future in concurrent.futures.as_completed(futures):
                        entry = futures[future]
                        metadata = future.result()
                        status[entry.id] = {
                            "status": metadata["status"],
                            "run_dir": _display_path(date_dir / entry.id),
                            "started_at": metadata["started_at"],
                            "ended_at": metadata["ended_at"],
                            "wall_seconds": metadata["wall_seconds"],
                            "exit_code": metadata["exit_code"],
                        }
                        save_status(args.status, status)
                        print(
                            f"[run_queue] END   {entry.id}  status={metadata['status']}  "
                            f"wall={metadata['wall_seconds']}s  exit={metadata['exit_code']}"
                        )

                print(f"[run_queue] PARALLEL GROUP {pg}: all {len(group)} entries complete")
    finally:
        release_lock(args.lock)

    return 0


if __name__ == "__main__":
    sys.exit(main())
