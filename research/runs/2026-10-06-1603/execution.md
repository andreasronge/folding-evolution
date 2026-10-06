# Execution

Code: commit `92ba7c54d0c7ad45db905d2d410cdc170c647e1b` on `research/2026-10-06-1603`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 92ba7c54d0c7ad45db905d2d410cdc170c647e1b`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-06-1603-four-reducer-family | done | 2621.211 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-1603-four-reducer-family |
