# Execution

Code: commit `fe196c1d66381a25f9862ff1bfd8df75a9e2e571` on `research/2026-10-09-0537`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> fe196c1d66381a25f9862ff1bfd8df75a9e2e571`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-09-0537-recoded-prepare | done | 512.799 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-0537-recoded-prepare |
| 2026-10-09-0537-recoded-score | failed | 5972.01 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-0537-recoded-score |
