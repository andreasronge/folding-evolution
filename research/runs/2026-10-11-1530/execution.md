# Execution

Code: commit `53f0e06a3305893be92c000d286b9b8310cc39a3` on `research/2026-10-11-1530`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 53f0e06a3305893be92c000d286b9b8310cc39a3`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-1530-prepare | done | 28.632 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1530-prepare |
| 2026-10-11-1530-score | done | 1072.855 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1530-score |
