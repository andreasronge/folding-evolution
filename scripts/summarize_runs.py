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
SUMMARY_PROMPT_TEMPLATE = """\
You are producing a morning-triage summary for ONE overnight experiment run. \
Project context (developmental encodings for genetic programming) is in \
CLAUDE.md. This is one data point, not a finding.

Discipline rules (follow strictly):
- Do NOT read other files or use tools. Summarize ONLY from the data below.
- Do NOT elevate a single run to a finding. Findings live in \
docs/<track>/findings.md and require replication + commit anchoring.
- Do NOT invent numbers. If a metric is missing from the data below, leave it out.
- Prefer empty strings over speculative filler in the suggestion fields.
- Target: a human should be able to skim this at 7am in under 10 seconds.

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

Input — result file (result.json, if present):
```
{result_snippet}
```

Return ONLY a JSON object with these keys. Values are short strings (<=150 \
chars) unless otherwise noted.

{{
  "one_line": "WHAT was run, HOW it ended, the SINGLE most important number if applicable. Pure observation, no interpretation.",
  "headline_numbers": {{}},
  "anomalies": [],
  "attention_required": false,
  "attention_reason": "",
  "next_step_suggestion": "",
  "falsification_candidate": ""
}}

Field guidance:

- headline_numbers: 0-5 key numeric results extracted verbatim from \
result.json or logs. Do NOT include wall_seconds, exit_code, or \
cpu_efficiency (they are already in metadata). Empty dict if result.json \
is absent or has no meaningful metrics.

- anomalies: stderr warnings, unusual rusage (cpu_efficiency under 2.0 on \
an 8-core machine, peak_rss far outside peers), truncated/malformed \
result.json, result shape contradicting the run's apparent intent. Do NOT \
include routine progress messages, normal completion, or exit code 0.

- attention_required: true ONLY if a human must inspect this BEFORE \
tonight's queue starts. Examples that qualify: silent data corruption \
(status=done but result.json has impossible values), environment issue that \
will recur, resource exhaustion. Routine failures and expected nulls do \
NOT qualify — those go through normal triage.

- next_step_suggestion: one sentence IF this run clearly opens a \
well-defined next question. Empty string otherwise. No weak suggestions.

- falsification_candidate: one sentence proposing an experiment that \
would stress-test the apparent signal. Empty string if the run shows no \
signal worth stressing.
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


def read_result_snippet(run_dir: Path, max_chars: int = 4000) -> str:
    candidate = run_dir / "result.json"
    if not candidate.exists():
        return "(no result.json)"
    try:
        text = candidate.read_text()
    except OSError as e:
        return f"(could not read: {e})"
    if len(text) > max_chars:
        return text[:max_chars] + f"\n... [truncated, {len(text) - max_chars} more chars]"
    return text


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
    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        metadata=json.dumps(metadata, indent=2),
        tail_lines=LOG_TAIL_LINES,
        stdout_tail=read_tail(run_dir / "stdout.log", LOG_TAIL_LINES) or "(empty)",
        stderr_tail=read_tail(run_dir / "stderr.log", LOG_TAIL_LINES) or "(empty)",
        result_snippet=read_result_snippet(run_dir),
    )
    raw, err = call_claude_cli(prompt)
    if err is not None:
        return {
            "status": "failed",
            "error": err,
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
    payload = extract_summary_payload(raw)
    return {
        "status": "ok",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "summary": payload,
    }


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
