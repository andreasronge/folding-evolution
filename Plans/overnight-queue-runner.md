# Overnight Queue Runner — Design

**Status:** implemented (`scripts/queue_lib.py`, `scripts/run_queue.py`, `scripts/summarize_runs.py`). Smoke-tested for done / failed / timeout / suspicious paths. SIGTERM pre-flight on the actual experiment code still pending (see below).

**Purpose:** Run a queue of experiments overnight, capture structured output + profiling data, produce a morning digest via Claude CLI. Explicitly **not** autonomous experiment design — execution only. See conversation 2026-04-14 for the scientific rationale against closed-loop auto-design.

---

## Scope

**In scope (v1):**
- Sequential execution of user-authored experiment queue.
- Per-entry timeout, crash, and interrupt handling.
- Subprocess-level profiling (wall, CPU, peak RSS) to metadata.
- Two-phase design: raw runs first, Claude CLI summarization after.
- Morning digest grouped by track.

**Out of scope (v1):**
- Dependencies between experiments.
- Parallel execution (Rayon already saturates cores; outer parallelism just contends).
- Pause/resume mid-queue (Ctrl+C + edit queue + restart is enough).
- macOS notifications / Slack webhooks.
- Autonomous experiment suggestion or iteration loops.

## File layout

```
queue.yaml                       # authored by user (spec)
queue.status.json                # runner-owned (bookkeeping)
queue.lock                       # PID lock; prevents double-launch
scripts/
├── run_queue.py                 # phase 1 — run all not-done entries
├── summarize_runs.py            # phase 2 — Claude CLI summaries
├── queue_lib.py                 # shared: atomic writes, lock, state IO
experiments/output/YYYY-MM-DD/<id>/
├── stdout.log
├── stderr.log
├── metadata.json                # git commit, seeds, timestamps, rusage
├── result.json                  # experiment's own output
└── summary.json                 # phase 2 output (absent if phase 2 failed)
```

**Why `queue.yaml` + `queue.status.json` split:** keeps the spec freely editable without runner bookkeeping corrupting it. Same pattern as Makefile + build state.

## Queue entry schema

```yaml
- id: scaffold_sweep_p0.3          # required, unique
  cmd: python -m experiments.chem_tape.run --config sweeps/scaffold_0.3.yaml
  timeout_seconds: 14400           # optional, default 14400 (4h)
  expect_outputs:                  # optional; all must exist for "done"
    - result.json
  track: chem-tape                 # optional; morning triage grouping
  notes: "P=0.3 variant of §1.11"  # optional; logged to metadata
```

## Entry state machine

```
queued → running → {done, failed, timeout, interrupted, suspicious}
```

- `done` — exit 0 AND all `expect_outputs` exist.
- `failed` — non-zero exit code.
- `timeout` — SIGTERM'd after `timeout_seconds`.
- `interrupted` — user SIGINT or process crashed while running.
- `suspicious` — exit 0 but `expect_outputs` missing.

**Selection rule (mode A):** runner runs every entry whose id is not in `queue.status.json`. To force re-run, user deletes the entry from `queue.status.json` or bumps the `id` in `queue.yaml`. User manages queue.yaml hygiene by removing entries they are done with.

## Signal handling

- **SIGINT #1:** forward to child, wait short grace period, mark `interrupted`, atomic status write, exit cleanly.
- **SIGINT #2:** SIGKILL child, best-effort status write, exit.
- Lock file written with PID; on startup, refuse if lock exists and PID alive; reclaim if stale.
- Wrap invocation in `caffeinate -s` so the Mac doesn't sleep. `caffeinate` exits with the script.

## Per-run metadata

Every run writes `metadata.json` with:
- git commit hash + dirty-state flag
- full queue entry (so you can reproduce from metadata alone)
- start/end timestamps (UTC)
- seeds actually used (if exposed by the experiment)
- Python version, platform
- Rust binary path + mtime

Plus subprocess `rusage` profile (zero overhead, read from kernel after `wait()`):
```json
{
  "wall_seconds": 847.2,
  "user_cpu_seconds": 6204.1,
  "sys_cpu_seconds": 58.3,
  "peak_rss_mb": 2140,
  "cpu_efficiency": 7.31,
  "voluntary_ctxt_switches": 14221
}
```

`cpu_efficiency = user_cpu / wall`. On an 8-core M1, a well-parallelized Rayon run should hit ~6–7. Flags serial bottlenecks or contention over time.

## Two-phase execution

Phase 1 (nightly, autonomous):
```
caffeinate -s python scripts/run_queue.py
```
Runs every not-done entry. No Claude CLI dependency. Raw output is the precious thing; we never let summary generation block data collection.

Phase 2 (morning, separate):
```
python scripts/summarize_runs.py
```
Sweeps done entries without a `summary.json`, calls `claude -p ... --output-format json` per entry, writes structured summary. Failures logged and skipped, not retried in the same invocation. Summaries can be regenerated at any time.

## Child-process hygiene

- `PYTHONUNBUFFERED=1` in child env (don't lose last log lines on crash).
- `RUN_DIR` exported to child env — **experiments must write result.json and any other outputs under `$RUN_DIR`**, not into `cwd`. The runner checks `expect_outputs` relative to run_dir; writing to cwd leaves outputs in REPO_ROOT and makes the entry land `suspicious`.
- stdout/stderr streamed to files, not buffered.
- Output dirs timestamped per run; partial output from a crashed run is preserved.
- Atomic writes for status file (tmp + rename).
- Child invoked via `shell=True` so pipe-style commands in queue entries work. The queue is user-authored and trusted.

## Pre-bed smoke workflow (recommended)

Two checks before kicking off a real overnight run:

1. **Parse + lint the queue** — catches duplicate ids, empty cmds, non-positive timeouts, expect_outputs paths that escape `$RUN_DIR`:
   ```
   uv run python scripts/run_queue.py --validate
   ```
   Prints the would-run plan and exits non-zero on issues. Runs in milliseconds.

2. **Short-budget smoke run** — catches real failures (missing imports, bad config paths, experiments that crash early, SIGTERM behavior). Maintain a `smoke.yaml` that mirrors tonight's `queue.yaml` with tight budgets (e.g. `--seeds 2 --gens 10`, or a `--quick` mode on each experiment). Run against disposable state:
   ```
   uv run python scripts/run_queue.py \
     --queue smoke.yaml \
     --status /tmp/smoke.status.json \
     --lock /tmp/smoke.lock \
     --output-root /tmp/smoke_out
   ```
   Completes in minutes. If this passes, the real queue is very likely to run through cleanly overnight.

## SIGTERM pre-flight check (before first real use)

Before relying on the runner in production, verify the Rust/Python experiment path cleans up on SIGTERM:

```
timeout --signal=TERM 10 python -m experiments.chem_tape.run <some_config>
```

Check:
- Did it exit within grace period?
- Are any output files well-formed (or clearly marked as partial)?
- `ps` / `lsof` show no leftover processes or file handles?

If cleanup is broken, fix in the Rust layer (catch SIGTERM, flush + close, then exit, or write to `results.json.tmp` + atomic rename). The queue runner would mask this bug otherwise — time outs, kills, moves on, and you have a pile of half-written files.

## Open questions for implementation

- Morning digest format: one markdown file per night under `experiments/output/YYYY-MM-DD/digest.md`, grouped by track? Or appended to a long-running `experiments/digest-log.md`?
- Should phase 2 failing to call Claude CLI (network, quota) write a placeholder `summary.json` with `status: failed` so it's visible in the next morning's digest, or remain absent?
- Token budget tracking — log per-summary tokens to a running file for cost visibility. Not gating, just visibility.
