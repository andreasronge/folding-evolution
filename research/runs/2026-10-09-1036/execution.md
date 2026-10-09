# Execution

Code: commit `348f9e236045eac6c31a6c6b50e1b869483bb7a2` on `research/2026-10-09-1036`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 348f9e236045eac6c31a6c6b50e1b869483bb7a2`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-09-1036-fragment-reuse-prepare | done | 57.178 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1036-fragment-reuse-prepare |
| 2026-10-09-1036-fragment-reuse-score | done | 9046.471 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1036-fragment-reuse-score |
