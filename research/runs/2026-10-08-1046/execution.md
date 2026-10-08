# Execution

Code: commit `a804f4f26d4d4874d22abf14a6af64be02e8bf6b` on `research/2026-10-08-1046`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> a804f4f26d4d4874d22abf14a6af64be02e8bf6b`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-08-1046-acquisition | done | 892.817 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-1046-acquisition |
| 2026-10-08-1046-sum-scoring | done | 983.362 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-1046-sum-scoring |
| 2026-10-08-1046-max-scoring | done | 2584.615 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-1046-max-scoring |
| 2026-10-08-1046-analysis | done | 3.786 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-1046-analysis |
