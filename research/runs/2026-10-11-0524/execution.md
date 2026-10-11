# Execution

Code: commit `7c0e5df23ae6229312664d666c35fcdb743f6576` on `research/2026-10-11-0524`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 7c0e5df23ae6229312664d666c35fcdb743f6576`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-0524-prepare | done | 66.936 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0524-prepare |
| 2026-10-11-0524-score | done | 2736.78 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0524-score |
