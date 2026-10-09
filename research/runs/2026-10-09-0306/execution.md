# Execution

Code: commit `2bab2c29db138dac4ef92f76d80707f5fe84f7e6` on `research/2026-10-09-0306`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 2bab2c29db138dac4ef92f76d80707f5fe84f7e6`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-09-0306-position-matched-prepare | done | 197.791 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-0306-position-matched-prepare |
| 2026-10-09-0306-position-matched-score | done | 5775.585 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-0306-position-matched-score |
