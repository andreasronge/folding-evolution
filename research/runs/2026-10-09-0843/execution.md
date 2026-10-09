# Execution

Code: commit `e347793549b0531f7acf167a5cc1768ae77ff127` on `research/2026-10-09-0843`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> e347793549b0531f7acf167a5cc1768ae77ff127`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-09-0843-fragments-prepare | done | 107.625 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-0843-fragments-prepare |
| 2026-10-09-0843-fragments-score | done | 4435.392 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-0843-fragments-score |
