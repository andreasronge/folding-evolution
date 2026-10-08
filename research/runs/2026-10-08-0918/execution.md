# Execution

Code: commit `511711c35cfaada094184ea6c4fa616503b01ee4` on `research/2026-10-08-0918`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 511711c35cfaada094184ea6c4fa616503b01ee4`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-08-0918-acquisition | failed | 3741.851 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-0918-acquisition |
| 2026-10-08-0918-sum-scoring | failed | 0.01 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-0918-sum-scoring |
| 2026-10-08-0918-max-scoring | failed | 0.01 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-0918-max-scoring |
| 2026-10-08-0918-analysis | failed | 0.01 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-0918-analysis |
