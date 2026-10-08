# Execution

Code: commit `36c665df005776d0b7d63d6ed80c4a2b688a7544` on `research/2026-10-07-2156`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 36c665df005776d0b7d63d6ed80c4a2b688a7544`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-07-2156-context-increment | done | 1585.034 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-07/2026-10-07-2156-context-increment |
