# Execution

Code: commit `74196a82db1a2b5b2cfacb812d6bd0e906a78e99` on `research/2026-10-09-2303`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 74196a82db1a2b5b2cfacb812d6bd0e906a78e99`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-09-2303-two-sum-prepare | done | 246.132 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-2303-two-sum-prepare |
| 2026-10-09-2303-two-sum-score | done | 6251.718 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-2303-two-sum-score |
