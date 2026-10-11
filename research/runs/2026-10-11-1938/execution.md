# Execution

Code: commit `9da9c2c7fcbabbc95032662c5fa32d91263f2851` on `research/2026-10-11-1938`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 9da9c2c7fcbabbc95032662c5fa32d91263f2851`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-1938-prepare | done | 32.786 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1938-prepare |
| 2026-10-11-1938-development | done | 51.993 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1938-development |
| 2026-10-11-1938-protected | done | 260.766 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1938-protected |
