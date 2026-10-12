# Execution

Code: commit `4ed04691276d0647ad60a1610b5dbf41e9ec6369` on `research/2026-10-12-0250`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 4ed04691276d0647ad60a1610b5dbf41e9ec6369`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-12-0250-exposure | done | 1703.975 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-12/2026-10-12-0250-exposure |
| 2026-10-12-0250-readout | done | 4648.972 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-12/2026-10-12-0250-readout |
