# Execution

Code: commit `e29219b14fa5dd6a8334d06fdcb4aa11d0e88f63` on `research/2026-10-11-1019`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> e29219b14fa5dd6a8334d06fdcb4aa11d0e88f63`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-1019-prepare | done | 49.324 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1019-prepare |
| 2026-10-11-1019-score | done | 1881.34 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1019-score |
