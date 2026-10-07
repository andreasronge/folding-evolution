# Execution

Code: commit `5565d54ff76b178fe283982fc59d93640ad8f171` on `research/2026-10-07-1924`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 5565d54ff76b178fe283982fc59d93640ad8f171`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-07-1924-solver-feedback | done | 4373.24 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-07/2026-10-07-1924-solver-feedback |
