# Execution

Code: commit `83c7c5b3cfb5d948c003e9f9505991a043db8e22` on `research/2026-10-11-2150`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 83c7c5b3cfb5d948c003e9f9505991a043db8e22`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-2150-prepare | done | 111.138 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-2150-prepare |
| 2026-10-11-2150-confirm | done | 5104.781 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-2150-confirm |
