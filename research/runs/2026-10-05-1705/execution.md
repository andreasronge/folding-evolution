# Execution

Code: commit `9abc25c17ead79c2269d67b591bdb48263d8246c` on `research/2026-10-05-1705`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 9abc25c17ead79c2269d67b591bdb48263d8246c`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-05-1705-evolve-bias | done | 1196.826 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-05/2026-10-05-1705-evolve-bias |
