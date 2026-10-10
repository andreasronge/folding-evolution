# Execution

Code: commit `6dabda8496453ed00b00f55694dd2bfc841a8db5` on `research/2026-10-10-2001`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 6dabda8496453ed00b00f55694dd2bfc841a8db5`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-10-2001-component-prepare | done | 141.877 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-2001-component-prepare |
| 2026-10-10-2001-component-DG | done | 4055.558 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-2001-component-DG |
| 2026-10-10-2001-component-TS | done | 1147.665 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-2001-component-TS |
