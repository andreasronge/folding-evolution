"""Overnight queue runner — phase 2.

Sweeps done/failed/timeout/suspicious runs without a summary.json, calls
`claude -p ... --output-format json` with metadata + log tails, writes
summary.json into each run directory. Failures to call Claude CLI are
logged and skipped — summaries are re-generable at any time and must
never block phase 1 data collection.

Design: Plans/overnight-queue-runner.md.

Typical usage (morning):
    python scripts/summarize_runs.py

Optional:
    python scripts/summarize_runs.py --date 2026-04-15   # a specific night
    python scripts/summarize_runs.py --regenerate        # overwrite existing summaries
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "experiments" / "output"
LOG_TAIL_LINES = 80
SUMMARIZE_TIMEOUT_SECONDS = 180
# Gap threshold above which a seed is flagged as "likely overfit"
# (train accuracy minus holdout accuracy on the same genotype).
# 0.05 is a working default — conservative enough that balanced-binary
# tasks with gap > 5pp are suspicious, loose enough not to fire on noise.
OVERFIT_GAP_THRESHOLD = 0.05
SUMMARY_PROMPT_TEMPLATE = """\
You are a research lab assistant briefing the PI at 7am on one overnight \
experiment run. Project context is in CLAUDE.md (already loaded). The run's \
track has its own architecture.md and experiments.md under `docs/<track>/` — \
read whichever sections help you situate the run (the entry's `notes` field \
often points at a specific §). Stick to this run's track; don't wander into \
other tracks' docs.

Write like a lab assistant, not a paper abstract: terse, grounded, honest \
about what one run does and doesn't tell us. If it's routine, say so \
briefly. Prefer an empty field over a weak guess.

Phrasing: a single run aligning with a hypothesis is "consistent with" — \
not "supports." Contradicting is "contradicts pending replication" — not \
"falsifies." One run is a data point.

If the run's `notes` or sweep name matches a file under `Plans/prereg_*.md`, \
read it and check whether the observed result falls in one of the \
pre-registered outcome rows. Report the match (or absence of a matching row) \
in `prereg_outcome` and the path in `prereg_path`. Don't invent a prereg if \
none exists — leave both fields at their "no-prereg-found" defaults.

Input — metadata (run config + timing + rusage profile):
```
{metadata}
```

Input — last {tail_lines} lines of stdout:
```
{stdout_tail}
```

Input — last {tail_lines} lines of stderr:
```
{stderr_tail}
```

Input — result file (result.json or sweep_index.json, whichever is present):
```
{result_snippet}
```

Input — deterministic overfit metrics (pre-computed from result file; \
absent when the run has no holdout data):
```
{overfit_metrics_snippet}
```

Return ONLY a JSON object:

{{
  "hypothesis_under_test": "what this run was probing, per the track's docs. If you can't locate the run in experiments.md, say so plainly.",
  "prereg_outcome": "one of: PASS-clean | PASS-partial | INCONCLUSIVE | FAIL | SWAMPED | no-matching-row | no-prereg-found",
  "prereg_path": "Plans/prereg_<slug>.md or empty string",
  "one_line": "what ran, how it ended, the single most important number if applicable.",
  "headline_numbers": {{}},
  "anomalies": [],
  "attention_required": false,
  "attention_reason": "",
  "next_step_suggestion": "",
  "falsification_candidate": ""
}}

`headline_numbers`: real metrics from result.json or logs. Skip \
wall_seconds / exit_code / cpu_efficiency (already in metadata).

`anomalies`: things that would make you raise an eyebrow — stderr warnings, \
unusually low cpu_efficiency, peak_rss far outside peers, truncated \
result.json, result shape that contradicts the run's intent. Skip routine \
completion.

`attention_required`: true only if the PI should look at this *before* \
tonight's queue starts — silent data corruption, environment issues that \
will recur, resource exhaustion, OR a non-trivial overfit signal (>= 25%% \
of seeds with gap > 0.05, or any single gap > 0.15). Routine failures and \
isolated overfit don't qualify.

If the deterministic overfit metrics block shows any overfit_seeds or \
max_gap above threshold, mention that in `anomalies` with the concrete \
numbers.

`next_step_suggestion` / `falsification_candidate`: only fill when the run \
genuinely opens a well-defined next probe or signal worth stressing.
"""


def read_tail(path: Path, n_lines: int) -> str:
    if not path.exists():
        return ""
    try:
        with path.open("rb") as f:
            f.seek(0, 2)
            size = f.tell()
            read_size = min(size, 256 * 1024)
            f.seek(size - read_size)
            data = f.read().decode(errors="replace")
    except OSError:
        return ""
    lines = data.splitlines()
    return "\n".join(lines[-n_lines:])


def _result_path(run_dir: Path) -> Path | None:
    """Pick the best result-like artefact: single-run `result.json` if
    present, otherwise a sweep's aggregate `sweep_index.json`. Returns None
    when neither exists."""
    for name in ("result.json", "sweep_index.json"):
        p = run_dir / name
        if p.exists():
            return p
    return None


def read_result_snippet(run_dir: Path, max_chars: int = 4000) -> str:
    candidate = _result_path(run_dir)
    if candidate is None:
        return "(no result.json or sweep_index.json)"
    try:
        text = candidate.read_text()
    except OSError as e:
        return f"(could not read: {e})"
    header = f"[{candidate.name}]\n"
    if len(text) > max_chars:
        return header + text[:max_chars] + f"\n... [truncated, {len(text) - max_chars} more chars]"
    return header + text


def _per_seed_gaps(result_data) -> list[tuple[int | None, str | None, float]]:
    """Extract (seed, task_name, gap) tuples from a parsed result artefact.

    Handles three shapes:
      - single-run result.json (dict with top-level train_holdout_gap)
      - single-run result.json with cross_task_fitness (alternation)
      - sweep_index.json (list of per-seed dicts, each as above)

    Emits one tuple per (seed, task) where gap is a finite float. Entries
    without holdout data are skipped silently.
    """
    out: list[tuple[int | None, str | None, float]] = []

    def _scan_single(entry: dict) -> None:
        seed = entry.get("seed")
        ctf = entry.get("cross_task_fitness")
        if isinstance(ctf, dict) and ctf:
            for task_name, v in ctf.items():
                if not isinstance(v, dict):
                    continue
                gap = v.get("gap")
                if isinstance(gap, (int, float)):
                    out.append((seed, task_name, float(gap)))
        else:
            gap = entry.get("train_holdout_gap")
            if isinstance(gap, (int, float)):
                out.append((seed, entry.get("task"), float(gap)))

    if isinstance(result_data, list):
        for entry in result_data:
            if isinstance(entry, dict):
                _scan_single(entry)
    elif isinstance(result_data, dict):
        _scan_single(result_data)
    return out


def compute_overfit_metrics(run_dir: Path) -> dict | None:
    """Deterministic overfit signal for a sweep/run directory.

    Returns None when the run has no usable holdout data. Otherwise:
        {
          "threshold": 0.05,
          "n_observations": int,                # (seed × task) count
          "n_seeds": int,                       # distinct seeds observed
          "overfit_observations": int,          # count with gap > threshold
          "overfit_seeds": int,                 # distinct seeds with any overfit task
          "max_gap": float,
          "mean_gap": float,
          "per_task": {task_name: {"n": int, "overfit": int, "max_gap": float, "mean_gap": float}},
        }
    """
    path = _result_path(run_dir)
    if path is None:
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    rows = _per_seed_gaps(data)
    if not rows:
        return None

    seeds_all: set[int | None] = {s for s, _, _ in rows}
    overfit_rows = [(s, t, g) for (s, t, g) in rows if g > OVERFIT_GAP_THRESHOLD]
    overfit_seeds: set[int | None] = {s for s, _, _ in overfit_rows}
    gaps = [g for _, _, g in rows]

    per_task: dict[str, dict] = {}
    for s, t, g in rows:
        key = t if t is not None else "(unlabelled)"
        bucket = per_task.setdefault(key, {"n": 0, "overfit": 0, "gaps": []})
        bucket["n"] += 1
        if g > OVERFIT_GAP_THRESHOLD:
            bucket["overfit"] += 1
        bucket["gaps"].append(g)
    for key, bucket in per_task.items():
        gaps_k = bucket.pop("gaps")
        bucket["max_gap"] = round(max(gaps_k), 4)
        bucket["mean_gap"] = round(sum(gaps_k) / len(gaps_k), 4)

    return {
        "threshold": OVERFIT_GAP_THRESHOLD,
        "n_observations": len(rows),
        "n_seeds": len(seeds_all),
        "overfit_observations": len(overfit_rows),
        "overfit_seeds": len(overfit_seeds),
        "max_gap": round(max(gaps), 4),
        "mean_gap": round(sum(gaps) / len(gaps), 4),
        "per_task": per_task,
    }


def find_run_dirs(output_root: Path, date: str | None) -> list[Path]:
    """Return [output_root/YYYY-MM-DD/<id>/ ...] under the given date,
    or across all dates if date is None."""
    if not output_root.exists():
        return []
    if date:
        date_dirs = [output_root / date] if (output_root / date).exists() else []
    else:
        date_dirs = sorted(p for p in output_root.iterdir() if p.is_dir())
    runs: list[Path] = []
    for d in date_dirs:
        runs.extend(sorted(p for p in d.iterdir() if p.is_dir()))
    return runs


def needs_summary(run_dir: Path, regenerate: bool) -> bool:
    metadata_path = run_dir / "metadata.json"
    if not metadata_path.exists():
        return False
    if regenerate:
        return True
    return not (run_dir / "summary.json").exists()


def call_claude_cli(prompt: str) -> tuple[str, str | None]:
    """Invoke `claude -p ... --output-format json`. Returns (stdout, error).
    Returns (stdout, None) on success; ("", reason) on failure."""
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True,
            timeout=SUMMARIZE_TIMEOUT_SECONDS,
            text=True,
        )
    except FileNotFoundError:
        return "", "claude CLI not found on PATH"
    except subprocess.TimeoutExpired:
        return "", f"claude CLI timed out after {SUMMARIZE_TIMEOUT_SECONDS}s"
    if proc.returncode != 0:
        return "", f"claude CLI exit {proc.returncode}: {proc.stderr.strip()[:200]}"
    return proc.stdout, None


def extract_summary_payload(raw_stdout: str) -> dict:
    """`claude -p --output-format json` returns an envelope with a 'result' key
    whose value is the model's text output. That text should itself be a JSON
    object matching the prompt schema; try to parse it."""
    try:
        envelope = json.loads(raw_stdout)
    except json.JSONDecodeError:
        return {"raw": raw_stdout, "parse_error": "envelope not JSON"}
    result_text = envelope.get("result", "") if isinstance(envelope, dict) else ""
    stripped = result_text.strip()
    if stripped.startswith("```"):
        # strip ```json ... ``` fence if present
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return {"raw": result_text, "parse_error": "result not JSON"}


def summarize_one(run_dir: Path) -> dict:
    metadata = json.loads((run_dir / "metadata.json").read_text())
    overfit = compute_overfit_metrics(run_dir)
    overfit_snippet = (
        json.dumps(overfit, indent=2)
        if overfit is not None
        else "(no holdout data — overfit metrics not computed)"
    )
    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        metadata=json.dumps(metadata, indent=2),
        tail_lines=LOG_TAIL_LINES,
        stdout_tail=read_tail(run_dir / "stdout.log", LOG_TAIL_LINES) or "(empty)",
        stderr_tail=read_tail(run_dir / "stderr.log", LOG_TAIL_LINES) or "(empty)",
        result_snippet=read_result_snippet(run_dir),
        overfit_metrics_snippet=overfit_snippet,
    )
    raw, err = call_claude_cli(prompt)
    base = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "overfit_metrics": overfit,
    }
    if err is not None:
        return {"status": "failed", "error": err, **base}
    payload = extract_summary_payload(raw)
    return {"status": "ok", "summary": payload, **base}


def main() -> int:
    ap = argparse.ArgumentParser(description="Claude-CLI summarizer for overnight runs")
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    ap.add_argument("--date", type=str, default=None, help="YYYY-MM-DD; default = all dates")
    ap.add_argument("--regenerate", action="store_true", help="overwrite existing summaries")
    args = ap.parse_args()

    runs = find_run_dirs(args.output_root, args.date)
    to_summarize = [r for r in runs if needs_summary(r, args.regenerate)]
    if not to_summarize:
        print("[summarize_runs] nothing to summarize")
        return 0

    print(f"[summarize_runs] summarizing {len(to_summarize)} runs")
    n_ok = 0
    n_failed = 0
    for run_dir in to_summarize:
        print(f"[summarize_runs] {run_dir.relative_to(REPO_ROOT)}")
        result = summarize_one(run_dir)
        (run_dir / "summary.json").write_text(json.dumps(result, indent=2))
        if result["status"] == "ok":
            n_ok += 1
        else:
            n_failed += 1
            print(f"  failed: {result.get('error')}", file=sys.stderr)

    print(f"[summarize_runs] done: {n_ok} ok, {n_failed} failed")
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
