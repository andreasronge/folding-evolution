#!/usr/bin/env bash
set -eo pipefail

# Navigate to the project root to ensure relative paths work regardless of where the script is called from
cd "$(dirname "$0")/../.."

mkdir -p experiments/chem_tape/output/_sweep_logs
LOGFILE="experiments/chem_tape/output/_sweep_logs/v2_4_alt_v2_6_v2_4_proxy_$(date +%Y%m%d_%H%M%S).log"

SWEEPS=(
    "v2_4_alt"
    "v2_4_proxy"
    "v2_6_pair1"
    "v2_6_pair2"
    "v2_6_pair3"
)

# Allow overriding the number of workers via the first script argument, defaults to 8
WORKERS=${1:-8}

echo "Starting sweeps. Logs will be saved to: $LOGFILE" | tee -a "$LOGFILE"

for SWEEP in "${SWEEPS[@]}"; do
    echo "========================================" | tee -a "$LOGFILE"
    echo "Starting sweep $SWEEP with $WORKERS workers" | tee -a "$LOGFILE"
    echo "========================================" | tee -a "$LOGFILE"
    
    uv run python experiments/chem_tape/sweep.py "experiments/chem_tape/sweeps/v2/${SWEEP}.yaml" --workers "$WORKERS" 2>&1 | tee -a "$LOGFILE"
    
    echo "Completed sweep $SWEEP" | tee -a "$LOGFILE"
done

echo "========================================" | tee -a "$LOGFILE"
echo "All sweeps complete. Final logs at $LOGFILE" | tee -a "$LOGFILE"
