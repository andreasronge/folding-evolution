# Execution

Code: commit `652fde5657629157c25999f23c7cda9b38afdc7f` on `research/2026-10-09-1743`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 652fde5657629157c25999f23c7cda9b38afdc7f`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-09-1743-small-source-prepare | done | 131.163 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1743-small-source-prepare |
| 2026-10-09-1743-small-source-score | done | 6243.055 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1743-small-source-score |
