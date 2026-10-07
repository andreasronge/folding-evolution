Frozen inputs for the approved 1924 one-feedback-step experiment.

- `parents.json`: all 32 1707 C tables, lineage identifiers and table hashes
  independently matched against C evaluation rows in the original search log.
- `solvers.json`: all 7,408 exact collection solver tapes from 1707. The runner
  independently verifies each tape against its training target on D1331 before A.
- `replay.json`: the 20 GG rows for each of the two replay cells in 1707 (40
  total). The runner replays all rows and compares scientific fields and tapes;
  elapsed timings and administrative metadata are excluded.
- `provenance.json`: original paths, source commit/file SHA256 values, committed
  artifact SHA256 values, and historical costs used for control admission.

The provenance digest is pinned in `solver_feedback_run.py`. All runtime inputs
are committed here; the original git-ignored output directory is not required.
No parent was selected by its observed search speed. Canonical/witness programs
never enter fitting or search payloads. The fitter and search remain unchanged.
