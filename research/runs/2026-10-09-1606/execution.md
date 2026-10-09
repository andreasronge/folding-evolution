# Execution

Code: commit `af8a7e5d77455bbeb32afe365ff0880757be9370` on `research/2026-10-09-1606`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> af8a7e5d77455bbeb32afe365ff0880757be9370`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-09-1606-suffix-preservation-prepare | done | 73.611 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1606-suffix-preservation-prepare |
| 2026-10-09-1606-suffix-preservation-score | done | 2796.155 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1606-suffix-preservation-score |
