# Execution

Code: commit `60ab76697cc1e5592474b4819f4bb3761c5bbbcd` on `research/2026-10-11-1228`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 60ab76697cc1e5592474b4819f4bb3761c5bbbcd`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-1228-prepare | done | 39.923 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1228-prepare |
| 2026-10-11-1228-score | done | 835.779 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1228-score |
