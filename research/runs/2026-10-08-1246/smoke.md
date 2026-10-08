# Preparation smoke and feasibility

Approved design implemented without changing targets, cap, fit law or full sample
sizes. Full execution remains pending in [queue.yaml](queue.yaml).

- Bank: all 220 groups (ids, aliases, agreement and retention) exactly reproduce
  the steward probe. 37 BE / 56 PA survivors, eight protected holdouts, full
  Python/Rust canonical agreement on 480 × 1331 checks per executor.
  [Bank build timings](smoke/bank/screen_timing.json): 111.5 s total,
  about 5.17 GiB peak screen RSS. Bank byte hash is independently pinned.
- [Final smoke](smoke/final/result.json): 112/112 searches completed in
  191.3 s; 45/64 collection solves
  (BE 20/32; PA 25/32), 45 distinct exact solver tapes, no empty cell,
  45 independent verifications and 16 C/T pairing checks. Both T/C searches,
  fitted-but-unscored K, report generation and plots completed. No holdout
  search occurred. These observations are feasibility checks, not efficacy claims.
- [Frozen provenance](smoke/final/freeze.json): all current module hashes,
  the actual Rust extension binary hash, the method hash and schedule hash verified.
  All 112 scientific rows replay exactly from the [initial smoke](smoke/corpus/),
  excluding only clock-derived fields. Smoke seed base is 202710081246;
  full/future seeds use the separate 202610081246 base. Smoke artifacts are
  explicitly flagged and cannot serve as full-run freeze artifacts.
- Conservative final smoke projection: 145.7
  minutes for full stage 1 at measured small-block utilization, including fits.
  It fits the 180-minute queue ceiling; the internal work deadline is 176 minutes.
  Reporting took 0.23 s and has a 120-second
  reserve. Stage 2 extrapolates to
  121.8 minutes at the same
  difficulty, without timing protected targets; that continuation needs strategy
  review and repricing from the full training results.
- [Forced deadline](smoke/deadline/result.json): worker shutdown succeeded,
  zero complete pairs, explicit incomplete execution and no efficacy eligibility.
  Unit tests independently verify a timeout retains only the fixed completed
  balanced prefix, including rejection of missing pairs and non-timeout errors.
- 22 focused tests passed (`test_comparison_gate`, `test_solver_corpus`,
  `test_four_reducer`); Ruff passed; queue parser validation passed with one
  10800-second entry. Diagnostic plot layout was visually inspected.

The code and bank live in the worktree; all preparation outputs and task files
are confined to this task folder in the main checkout. No research belief,
question, digest or prior-result text was edited. The queue executes the approved
3072 collection + 2048 C/T training + 256 G4 training searches and freezes the
4352-search stage-2 roster without executing it.
