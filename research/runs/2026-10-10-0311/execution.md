# Execution

Code: commit `09c850dac6de09c4d6bc3b679d4f3d489abe603d` on `research/2026-10-10-0311`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 09c850dac6de09c4d6bc3b679d4f3d489abe603d`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-10-0311-independent-input-prepare | done | 599.174 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-0311-independent-input-prepare |
| 2026-10-10-0311-independent-input-score | done | 443.646 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-0311-independent-input-score |
