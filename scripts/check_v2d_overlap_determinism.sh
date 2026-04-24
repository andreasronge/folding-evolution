#!/usr/bin/env bash
# Post-sweep determinism check for §v2.5-plasticity-2d v7 overlap seeds.
#
# Verifies the 4 overlap seeds (20..23 at budget=40) in the 2026-04-23 partial
# sweep produce byte-identical final_population.npz and result.json in the
# 2026-04-24 re-run. Code is unchanged between ee44b1c and v7 target SHA, so
# overlap outputs MUST match exactly.
#
# Mandatory per prereg Plans/prereg_v2-5-plasticity-2d.md v7 banner +
# amendment history §"Quarantine and re-run plan" step 3. Run this script
# BEFORE invoking analyze_plasticity.py on the new sweep output; any
# divergence routes Row 6 SWAMPED (reason: determinism-failure) and halts
# the chronicle pending investigation.
#
# Usage:
#   scripts/check_v2d_overlap_determinism.sh \
#     experiments/output/2026-04-23/v2_5_plasticity_2d \
#     experiments/output/2026-04-24/v2_5_plasticity_2d_primary_b40
#
# Exit 0 if all 4 overlap seeds × 2 files byte-identical; non-zero otherwise.

set -euo pipefail

OLD_DIR="${1:?first arg: old (2026-04-23) sweep dir}"
NEW_DIR="${2:?second arg: new (2026-04-24) sweep dir}"

find_run_dir() {
    local sweep="$1" want_budget="$2" want_seed="$3" d b s
    for d in "$sweep"/*/; do
        [ -f "$d/config.yaml" ] || continue
        b=$(awk '$1 == "plasticity_budget:" { print $NF }' "$d/config.yaml")
        s=$(awk '$1 == "seed:" { print $NF }' "$d/config.yaml")
        if [ "$b" = "$want_budget" ] && [ "$s" = "$want_seed" ]; then
            printf "%s\n" "${d%/}"
            return 0
        fi
    done
    return 1
}

divergences=0
for seed in 20 21 22 23; do
    old=$(find_run_dir "$OLD_DIR" 40 "$seed") || {
        echo "MISSING old run: budget=40 seed=$seed"
        divergences=$((divergences + 1))
        continue
    }
    new=$(find_run_dir "$NEW_DIR" 40 "$seed") || {
        echo "MISSING new run: budget=40 seed=$seed"
        divergences=$((divergences + 1))
        continue
    }
    for f in final_population.npz result.json; do
        if [ ! -f "$old/$f" ] || [ ! -f "$new/$f" ]; then
            echo "MISSING file: budget=40 seed=$seed $f"
            divergences=$((divergences + 1))
            continue
        fi
        old_hash=$(shasum -a 256 "$old/$f" | awk '{print $1}')
        new_hash=$(shasum -a 256 "$new/$f" | awk '{print $1}')
        if [ "$old_hash" = "$new_hash" ]; then
            echo "OK       budget=40 seed=$seed $f $old_hash"
        else
            echo "DIVERGE  budget=40 seed=$seed $f old=$old_hash new=$new_hash"
            divergences=$((divergences + 1))
        fi
    done
done

if [ "$divergences" -gt 0 ]; then
    echo ""
    echo "DETERMINISM CHECK FAILED: $divergences divergence(s) across 4 overlap seeds × 2 files"
    echo "→ Route §2d-primary chronicle verdict to Row 6 SWAMPED (reason: determinism-failure); investigate before any downstream analysis."
    exit 1
fi
echo ""
echo "DETERMINISM CHECK PASSED: all 4 overlap seeds × 2 files byte-identical"
