# Execution

Code: commit `3a18ef5a7dbcd751d4a5f052691e3fa0d9cda4d8` on `research/2026-10-11-1736`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 3a18ef5a7dbcd751d4a5f052691e3fa0d9cda4d8`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-1736-exposure | done | 615.034 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1736-exposure |
| 2026-10-11-1736-readout | done | 3676.333 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1736-readout |
