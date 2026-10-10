# Execution

Code: commit `c32ff04f4d3fae4f7b74fc0b137f872ccdd9a5df` on `research/2026-10-10-2254`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> c32ff04f4d3fae4f7b74fc0b137f872ccdd9a5df`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-10-2254-prepare | done | 555.273 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-2254-prepare |
| 2026-10-10-2254-dg | done | 1954.785 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-2254-dg |
| 2026-10-10-2254-ts | done | 386.472 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-2254-ts |
