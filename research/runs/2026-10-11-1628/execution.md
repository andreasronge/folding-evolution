# Execution

Code: commit `46e05cb74e4693f4ffc6bad6bbe2611109fab900` on `research/2026-10-11-1628`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 46e05cb74e4693f4ffc6bad6bbe2611109fab900`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-1628-prepare | done | 37.184 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1628-prepare |
| 2026-10-11-1628-score | done | 1537.079 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1628-score |
