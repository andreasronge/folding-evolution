# Execution

Code: commit `5dd86bd2926522958b4ae5a8b013abe124d26cd0` on `research/2026-10-08-1246`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 5dd86bd2926522958b4ae5a8b013abe124d26cd0`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-08-1246-comparison-gate-training | done | 7127.497 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-1246-comparison-gate-training |
