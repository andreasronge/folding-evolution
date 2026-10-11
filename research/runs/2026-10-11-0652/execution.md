# Execution

Code: commit `163f0051cc1948792b656d702ab3fb65bb262651` on `research/2026-10-11-0652`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 163f0051cc1948792b656d702ab3fb65bb262651`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-0652-prepare | done | 146.739 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0652-prepare |
| 2026-10-11-0652-score | done | 3673.693 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0652-score |
