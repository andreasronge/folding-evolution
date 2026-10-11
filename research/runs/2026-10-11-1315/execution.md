# Execution

Code: commit `4a60cc7dee19ed980bec75966af558ef90d7c379` on `research/2026-10-11-1315`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 4a60cc7dee19ed980bec75966af558ef90d7c379`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-1315-prepare | done | 11.284 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1315-prepare |
| 2026-10-11-1315-score | done | 1154.279 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1315-score |
