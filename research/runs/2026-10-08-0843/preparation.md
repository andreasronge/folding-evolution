# Preparation checks

The plan was written before implementation or experiment execution. Reused the reviewed modifier implementation from `25f929e` by cherry-picking it as `82d2d02`; no Rust changes or rebuild were needed.

Validation: 22 inherited-bias tests and 89 relevant TAG/evolution/bias regression tests passed (111 total). Ruff passes for all five touched source/test files; git diff checks pass. The final small-scale smoke completed all four family/arm cells: two episodes, three reproductions/episode, eight evaluated populations and 256 evaluations/run. Evidence: `final-smoke/validation.json`, `final-smoke/smoke.json` and `final-smoke/manifest.json`. The trajectory plot was rendered and inspected.

Tests cover first-generation, intermediate, last-generation and absent witnesses in both arms; preservation of the first witness and cessation of verification; continued population evaluation, reproduction and broken shuffling; recipient/elite bookkeeping, final extraction and sigma-zero replay over 20 seeds. Synthetic analysis checks the exact 80-acquisition/3328-search roster, independent acquired/bounded family decisions, uniform as primary, the scaffold ratio, shared-seed/paired-run bootstrap algebra, and rejection of missingness/duplicates. A staged CLI test verifies saved acquisitions and rejection of incompatible input manifests.

Timing acquisition vectors are excluded from inference. No new frozen performance was scored or inspected during preparation. Old 2243 frozen files are used only for the pre-stated cost calculation. Fixed-duration timing artifacts are in `stage0/`; progress is in `stage0.log`.

Smoke and timing artifacts were created in a dirty worktree and include their source hashes. While timing was running, the final code added price/report/plot plumbing and corrected the configuration's logged generation field to 128; the fixed-duration loop already used 128, so no timing selection or acquisition-law change occurred. The raw timing manifest and files are preserved. Full queue manifests must match each other's master, source hashes, reference indices and reference-spec hash.

Admission result: both roster prices fail. Full timeout sum 11397 s; approved fallback 10868 s versus 10800 s maximum. Stop and return to strategy; see infeasible.md. No queue written or launched.
