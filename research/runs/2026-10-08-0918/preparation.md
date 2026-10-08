# Preparation complete — queue admitted

Implementation: merged approved `c01f16d` as `8be061d`; final implementation commit `511711c` on `research/2026-10-08-0918`. The acquisition law, seed construction and frozen scoring engine are unchanged. References now default to shared indices 0–15 only; CLI accepts the approved 16-seed roster and optional `--omit-fit` fallback. Manifests, roster validation, contrasts, break-even summaries, plots and pricing handle fit omission consistently. Input manifests reject reference-arm/count mismatches. No Rust changes or rebuild required. No research/ files were committed on this branch.

Plan was written before merge, tests or experiment execution. Preparation stayed within the 120-minute limit. No substantive acquisition/scoring queue was launched and no new learned vector was scored for frozen performance. The four 0843 timing vectors remain excluded from inference.

Validation: **127 tests passed** across `test_inherited_bias.py`, `test_chem_tape_tagged.py`, `test_chem_tape_evolve_smoke.py`, `test_evolve_bias.py`, `test_evolve_bias_components.py` and `test_chem_tape_evolve_k.py`. Ruff passed for all five merged/touched source/test files; git diff checks passed. The new staged synthetic CLI checks caught and fixed a JSON tuple/list comparison in reference-arm manifest validation before admission. Both approved rosters now complete acquisition→sum scoring→max scoring→analysis with actual plotting, using synthetic capped records only. Tests enforce exact 80-acquisition/2752-search rosters (2688 if fit omitted), reference indices, unchanged paired/shared bootstrap contrasts on fit omission, acquired precedence, missing/duplicate searches and incomplete infrastructure rejection. Synthetic fully censored learned arms retain the linkage-unidentified flag.

Final operational smoke from clean commit `511711c`: P=32, two episodes, three reproductions per episode, one run per family/arm. All four completed exactly six reproductions, eight censuses and 256 population evaluations; run seconds ranged 0.0121–0.0142. This small smoke is an implementation check, not a full-size runtime estimate or scientific result. Target witnesses, balanced labels, recipient/elite bookkeeping, support floor and 20-seed sigma-zero legacy replay passed. See [validation](final-smoke/validation.json), [smoke rows](final-smoke/smoke.json), [clean-commit manifest](final-smoke/manifest.json) and [rendered and inspected trajectories](final-smoke/trajectories.png). Source hashes match the final committed code. Earlier dirty-state smoke is preserved under `smoke/`.

Exact repricing uses the four acquisition measurements in [0843 timing](../2026-10-08-0843/stage0/timing.json) and the prior 2243 frozen timing cells only. No full-size acquisition was re-timed, as specified by the approved proposal's post-merge-only smoke. Cell means and final-worker/2× allowances are unchanged. Cost source hashes and acquisition diagnostics are retained in [projection](cost/projection.json), with final code provenance in [cost manifest](cost/manifest.json).

| Stage | Expected seconds | Timeout seconds |
|---|---:|---:|
| Acquisition | 2761.80 | 5824 |
| Sum scoring | 583.28 | 1317 |
| Max scoring | 1505.98 | 3162 |
| Analysis/check allowance | not separately mean-priced | 300 |
| Total | 4851.06 (80.85 minutes, acquisition/scoring) | **10603 (176.72 minutes)** |

The total is **197 seconds below** the 10800-second gate. Keep all three references: **80 acquisitions + 2560 learned searches + 192 reference searches**. The optional fit-removal price is 10593 seconds; it is not used because the complete approved roster passes. Ten-worker throughput and verifier tails remain unvalidated. This is the pre-stated measured-mean planning allowance, not a runtime guarantee. Roughly 3.35 h includes expected queue time plus the 2 h preparation allowance; roughly 5 h includes timeout allowances plus preparation.

[queue.yaml](queue.yaml) has four sequential entries with correct task prefixes, 10 workers, explicit RUN_DIR outputs and sibling input paths independent of date/output-root. It parses through `scripts/queue_lib.py`; every shell command passes `/bin/sh -n`; timeout sum matches the projection. Score entries require the acquisition completion marker; analysis requires all three stage markers. The engine independently rejects incomplete rows, wrong schedules/parameters, incompatible manifests and missing/duplicate rosters before verdicts. Missing/timed-out searches cannot be treated as completed cap censoring.

Critique 1–5 is reflected in plan and implementation. Notes 6–7 are steward scope-audit matters: the observed 3× early-stopping imbalance applied only to the single sum timing pair, not both families generally. The researcher has not edited questions/digest/briefs. All scientific results or subsequent runtime/build stops require the promised immediate strategist review; no threshold-2 transfer is authorized by this queue.

Branch worktree is clean at completion. Task artifacts live only in this run folder in the main checkout and are left for the driver/steward's research-artifact commit.
