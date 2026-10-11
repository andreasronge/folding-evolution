# 1315 rectified-sum development probe artifacts

`manifest.json` is the complete performance-blind nine-token screen and D625
bank, built by `rectified_bank.build(deadline)` before the new acquisition.
Canonical trees and alias witnesses are validation data only. All 54 candidates
were admitted; development retains the four stage-0 searched cells and the two
lowest label-hash/id remaining overlapping cells. All 24 protected cells remain
unsearched. Stage 0 preceded this freeze: this is a development bank, not a bank
frozen before any search. Exact digest is pinned in `rectified_run.py`.

`transport.json.gz` is a deterministic gzip archive of the reviewed 1228
prepare's libraries, preparation, method freeze, schedules and seed audit, with
original raw-byte hashes and source path in `provenance`. The full artifacts
are retained so their preparation hashes can be checked. Only `semantic_all`
from builds 0–7 is deployed, unchanged; the original source acquisition and
extraction/validation costs are reported separately from the already-owned
library deployment case. Uncompressed archive SHA256 is pinned in the runner.
No new bank labels are used to fit or modify the transported donors.

Full queue: `RAYON_NUM_THREADS=1 .venv/bin/python -m
experiments.chem_tape.rectified_run prepare --workers 11 --seconds 870`, followed
by `score --prepared <prepare RUN_DIR> --workers 11 --seconds 2370`. Both write
only under `$RUN_DIR`, fail on provenance disagreement and retain partial rows.
`--smoke` uses distinct seeds, 48 source jobs and 16 jobs across the four
previously seen development cells, with the production restart budget.

`order_library.build`'s optional diagnostic vectors affect helper census only;
semantic/literal class selection is unchanged. Fixed whole-build bootstrap
intervals and the recommendation thresholds are descriptive investment aids.
Source solver containment does not measure donor ancestry or helper causality.
