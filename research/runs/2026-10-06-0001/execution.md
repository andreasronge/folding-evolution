# Execution

Code: commit `a65ded0db3621ad2293c9693c0c34c3e2adbeb7d` on `research/2026-10-06-0001`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> a65ded0db3621ad2293c9693c0c34c3e2adbeb7d`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-06-0001-assembly-family | done | 2089.136 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-0001-assembly-family |
