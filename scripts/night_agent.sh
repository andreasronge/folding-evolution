#!/usr/bin/env bash
# Start a headless coding agent on a night hand-off plan, at a given time, with a hard
# wall-clock limit. Run inside a persistent session (Herdr, tmux) from the repo root.
#
#   AGENT_CMD='<agent command taking the prompt as its last argument>' \
#     scripts/night_agent.sh [--at HH:MM] [--max-hours N] Plans/<hand-off>.md
#
# AGENT_CMD must run non-interactively and be allowed to edit, run commands, commit and push.
set -euo pipefail

at="" max_hours=9
while [[ $# -gt 1 ]]; do
  case "$1" in
    --at) at="$2"; shift 2 ;;
    --max-hours) max_hours="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
plan="${1:?usage: night_agent.sh [--at HH:MM] [--max-hours N] PLAN.md}"
: "${AGENT_CMD:?set AGENT_CMD to the headless agent command}"
[[ -f "$plan" ]] || { echo "no such plan: $plan" >&2; exit 2; }
[[ "$max_hours" =~ ^[0-9]+$ && "$max_hours" -gt 0 ]] || { echo "--max-hours must be a positive integer" >&2; exit 2; }

timeout_bin="$(command -v gtimeout || command -v timeout || true)"
[[ -n "$timeout_bin" ]] || { echo "need GNU timeout (brew install coreutils)" >&2; exit 2; }

if [[ -n "$at" ]]; then
  [[ "$at" =~ ^([01][0-9]|2[0-3]):[0-5][0-9]$ ]] || { echo "--at must be HH:MM" >&2; exit 2; }
  now=$(date +%s)
  target=$(date -j -f "%Y-%m-%d %H:%M:%S" "$(date +%Y-%m-%d) $at:00" +%s)
  (( target > now )) || target=$(( target + 86400 ))
  echo "waiting $(( target - now )) s until $at"
  caffeinate -s sleep $(( target - now ))
fi

mkdir -p experiments/output
log="experiments/output/night_agent_$(date +%Y-%m-%d_%H%M).log"
deadline=$(date -v +"${max_hours}"H "+%Y-%m-%d %H:%M")
prompt="You are running unattended. Read ${plan} in this repository and carry it out from the top. \
Nobody will answer questions. You will be killed at ${deadline} local time; the plan says what \
must be finished and pushed before then. If the plan's STATE.md already exists, resume from it."

echo "starting agent at $(date), hard stop ${deadline}, log ${log}"
git pull --ff-only
set +e
# shellcheck disable=SC2086
caffeinate -s "$timeout_bin" --kill-after=60 "${max_hours}h" $AGENT_CMD "$prompt" >"$log" 2>&1
status=$?
set -e
echo "agent exited with status ${status} at $(date)" | tee -a "$log"
exit "$status"
