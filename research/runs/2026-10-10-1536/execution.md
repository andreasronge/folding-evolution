# Execution

Code: commit `7244fa1651e0cb331a0e1dd47fbdad2f8e86f954` on `research/2026-10-10-1536`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 7244fa1651e0cb331a0e1dd47fbdad2f8e86f954`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-10-1536-independent-input-prepare | done | 1902.465 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-1536-independent-input-prepare |
| 2026-10-10-1536-independent-input-score | done | 1892.837 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-1536-independent-input-score |
