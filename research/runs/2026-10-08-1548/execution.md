# Execution

Code: commit `45b2bdb2cbe5dee7ef04c3b5ebc10c54ce3e233a` on `research/2026-10-08-1548`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 45b2bdb2cbe5dee7ef04c3b5ebc10c54ce3e233a`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-08-1548-fresh-then-addition | done | 4171.027 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-1548-fresh-then-addition |
| 2026-10-08-1548-development-holdouts | done | 3142.813 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-1548-development-holdouts |
