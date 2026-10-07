# Execution

Code: commit `5dae3a63b59f71df612c7fa9424a946722a5e895` on `research/2026-10-07-0315`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 5dae3a63b59f71df612c7fa9424a946722a5e895`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-07-0315-training-bank-initialization | done | 15385.392 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-07/2026-10-07-0315-training-bank-initialization |
