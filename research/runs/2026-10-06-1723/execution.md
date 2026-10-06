# Execution

Code: commit `db96645f54b72e890f55d9236dbeec85c41df256` on `research/2026-10-06-1723`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> db96645f54b72e890f55d9236dbeec85c41df256`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-06-1723-crossed-family-training | done | 15394.289 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-1723-crossed-family-training |
