# Execution

Code: commit `b5697a125347a91773db2ffc9f34d05e03b8f898` on `research/2026-10-10-1717`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> b5697a125347a91773db2ffc9f34d05e03b8f898`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-10-1717-family-preference-prepare | done | 1065.131 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-1717-family-preference-prepare |
| 2026-10-10-1717-family-preference-score | done | 3425.545 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-1717-family-preference-score |
