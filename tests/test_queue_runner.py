"""scripts/run_queue.py: locking and process-group cleanup."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import queue_lib  # noqa: E402


def run_queue(tmp_path: Path, *extra: str, wait: bool = True):
    args = [sys.executable, str(SCRIPTS / "run_queue.py"), "--queue", str(tmp_path / "q.yaml"),
            "--status", str(tmp_path / "status.json"), "--lock", str(tmp_path / "q.lock"),
            "--output-root", str(tmp_path / "out"), *extra]
    if wait:
        return subprocess.run(args, capture_output=True, text=True, timeout=60)
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def test_lock_is_exclusive_and_released(tmp_path):
    lock = tmp_path / "q.lock"
    queue_lib.acquire_lock(lock)
    holder = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {str(SCRIPTS)!r}); import queue_lib\n"
         f"try:\n    queue_lib.acquire_lock(__import__('pathlib').Path({str(lock)!r}))\n"
         "except queue_lib.LockError:\n    sys.exit(3)"],
        timeout=30)
    assert holder.returncode == 3
    queue_lib.release_lock(lock)
    queue_lib.acquire_lock(lock)  # free again
    queue_lib.release_lock(lock)


def test_second_runner_leaves_live_status_alone(tmp_path):
    (tmp_path / "q.yaml").write_text("runs:\n  - id: slow\n    cmd: sleep 5\n")
    first = run_queue(tmp_path, wait=False)
    status = tmp_path / "status.json"
    for _ in range(100):
        if status.exists() and json.loads(status.read_text()).get("slow", {}).get("status") == "running":
            break
        time.sleep(0.1)
    second = run_queue(tmp_path)
    assert second.returncode == 3
    assert json.loads(status.read_text())["slow"]["status"] == "running"
    first.terminate()
    first.wait(timeout=30)


def test_timeout_kills_whole_process_group(tmp_path):
    marker = tmp_path / "survivor"
    # The background child ignores SIGTERM; only a group SIGKILL stops it.
    cmd = f"(trap '' TERM; sleep 4; touch {marker}) & sleep 60"
    (tmp_path / "q.yaml").write_text(
        f"runs:\n  - id: t\n    cmd: \"{cmd}\"\n    timeout_seconds: 1\n")
    result = run_queue(tmp_path)
    assert result.returncode == 0
    assert json.loads((tmp_path / "status.json").read_text())["t"]["status"] == "timeout"
    time.sleep(4.5)
    assert not marker.exists(), "worker outlived the timed-out entry"


def test_interrupt_kills_entry_ignoring_sigterm(tmp_path):
    import signal

    (tmp_path / "q.yaml").write_text(
        "runs:\n  - id: stubborn\n    cmd: \"trap '' TERM; sleep 120\"\n")
    proc = run_queue(tmp_path, wait=False)
    status = tmp_path / "status.json"
    for _ in range(100):
        if status.exists() and json.loads(status.read_text()).get("stubborn", {}).get("status") == "running":
            break
        time.sleep(0.1)
    time.sleep(0.5)
    start = time.monotonic()
    proc.send_signal(signal.SIGINT)
    proc.wait(timeout=60)
    assert time.monotonic() - start < 30  # grace (10 s) + SIGKILL, not the 4 h timeout
    assert json.loads(status.read_text())["stubborn"]["status"] == "interrupted"


def test_driver_timeout_stops_queue_entries_too(tmp_path):
    """The driver kills the queue runner's group; the runner must get enough
    grace to SIGKILL its entries, which live in their own process groups."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("research", SCRIPTS / "research.py")
    research = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(research)
    research.POLL_SECONDS = 0.2
    marker = tmp_path / "entry_alive"
    (tmp_path / "q.yaml").write_text(
        f"runs:\n  - id: stubborn\n    cmd: \"trap '' TERM; sleep 25; touch {marker}\"\n")
    argv = [sys.executable, str(SCRIPTS / "run_queue.py"), "--queue", str(tmp_path / "q.yaml"),
            "--status", str(tmp_path / "status.json"), "--lock", str(tmp_path / "q.lock"),
            "--output-root", str(tmp_path / "out")]
    code = research.LocalLauncher().run("queue", argv, tmp_path, tmp_path / "logs", timeout_s=2,
                                        kill_grace=research.QUEUE_KILL_GRACE_SECONDS)
    assert code is None
    time.sleep(25)
    assert not marker.exists(), "queue entry survived the driver's timeout"
    assert json.loads((tmp_path / "status.json").read_text())["stubborn"]["status"] == "interrupted"
