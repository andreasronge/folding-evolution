# Execution

Code: commit `d7ec1003c2ffd310cf5ac0fa88a20d0540adcef4` on `research/2026-10-11-0150`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> d7ec1003c2ffd310cf5ac0fa88a20d0540adcef4`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-0150-prepare | done | 847.685 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0150-prepare |
| 2026-10-11-0150-dg | done | 3136.815 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0150-dg |
