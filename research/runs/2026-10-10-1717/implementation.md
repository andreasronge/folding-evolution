Implemented and committed as `b5697a125347a91773db2ffc9f34d05e03b8f898` on research/2026-10-10-1717.

Plan: [plan.md](plan.md). Full-run queue: [queue.yaml](queue.yaml),80+140minute
timeouts,220minutes total. No full confirmation or target search was run.

Validation:56 relevant tests passed; the final calibration-schedule change passed
all7 crossed-comparison tests. Ruff and byte compilation passed. Final reduced-cap
prepare/score/report/plot smoke passed, and96 full-cap development calibration
searches passed with separate pilot acquisitions. Measured complete price is about
106minutes, rounded to110 expected queue wall-clock; full preparation recalibrates
all24 confirmation builds and enforces its own measured admission.

Evidence: [smoke_measurements.json](smoke_measurements.json),[smoke/final-score](smoke/final-score/)
and[smoke/full-cap-pilot](smoke/full-cap-pilot/). Pilot method hashes precede the
final all24-build development-calibration cycling change; no recipe change.

Critique points are addressed in plan.md. Digest wording is deferred to the
steward because the researcher is authorized to write only this task folder in
research/. No research/ files were committed on the task branch.

The closer fragment precedent was checked against the authors' Lancaster archive
abstract: [Wild and Porter2022](https://eprints.lancs.ac.uk/id/eprint/174982/).
The [PIPE abstract](https://pubmed.ncbi.nlm.nih.gov/10021756/) was also checked.
