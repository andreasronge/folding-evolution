# Execution

Code: commit `28db9640e98cb86c8dd2ac44d372877fcfde933f` on `research/2026-10-11-0833`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 28db9640e98cb86c8dd2ac44d372877fcfde933f`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-0833-prepare | done | 105.336 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0833-prepare |
| 2026-10-11-0833-score | done | 3173.329 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0833-score |
