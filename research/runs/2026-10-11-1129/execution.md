# Execution

Code: commit `db30b154af9bb9124298a12060469331ab3b6bc6` on `research/2026-10-11-1129`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> db30b154af9bb9124298a12060469331ab3b6bc6`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-1129-prepare | done | 118.24 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1129-prepare |
| 2026-10-11-1129-score | done | 332.291 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1129-score |
