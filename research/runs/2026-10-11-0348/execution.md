# Execution

Code: commit `1f02bb7382c64c4f77fca9eb75f3aa38e9f640b7` on `research/2026-10-11-0348`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 1f02bb7382c64c4f77fca9eb75f3aa38e9f640b7`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-0348-prepare | done | 274.687 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0348-prepare |
| 2026-10-11-0348-gate-sum | done | 2316.626 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0348-gate-sum |
