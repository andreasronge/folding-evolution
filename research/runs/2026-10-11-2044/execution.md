# Execution

Code: commit `8a621dfe5e95f94c51246d27e94f21b7183fdfb8` on `research/2026-10-11-2044`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 8a621dfe5e95f94c51246d27e94f21b7183fdfb8`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-2044-prepare | done | 111.307 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-2044-prepare |
| 2026-10-11-2044-development | done | 765.259 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-2044-development |
