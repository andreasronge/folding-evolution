# Execution

Code: commit `e12edbfb7884d30fa8c211f1c906fdb0083b45e4` on `research/2026-10-09-2033`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> e12edbfb7884d30fa8c211f1c906fdb0083b45e4`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-09-2033-sparse-feedback-prepare | done | 651.878 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-2033-sparse-feedback-prepare |
| 2026-10-09-2033-sparse-feedback-score | done | 4960.899 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-2033-sparse-feedback-score |
