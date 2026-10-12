# Execution

Code: commit `465f2fa3a66929396e2e603820e1ccca60978480` on `research/2026-10-11-2353`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 465f2fa3a66929396e2e603820e1ccca60978480`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-2353-prepare | done | 112.968 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-12/2026-10-11-2353-prepare |
| 2026-10-11-2353-score | done | 8166.292 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-12/2026-10-11-2353-score |
