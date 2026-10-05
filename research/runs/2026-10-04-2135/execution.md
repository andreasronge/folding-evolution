# Execution

Code: commit `f418c91c59e3b84fc2996c15effa203ced7a7d51` on `research/2026-10-04-2135`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> f418c91c59e3b84fc2996c15effa203ced7a7d51`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-04-2135-shared-arrival | done | 8416.128 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-04/2026-10-04-2135-shared-arrival |
