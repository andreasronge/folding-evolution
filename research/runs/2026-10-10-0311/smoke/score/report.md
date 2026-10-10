# Independent-input pilot (descriptive)

SMOKE ONLY; no scientific admission.

|Contrast (capped cost)|Point|95% build/seed interval|
|---|---:|---:|
|G4/A8|1.000|[1.000, 1.000]|
|G4/O|1.000|[1.000, 1.000]|
|O/A8|1.000|[1.000, 1.000]|

Failures contribute2cap. A finite no-hit sample is a bound, not impossibility. Shared G4 seed uncertainty is propagated.

|Arm|Solved/attempts|
|---|---:|
|G4|0/16|
|A8|0/16|
|O|0/16|

G4 development headroom is outside10–80%; pilot contrast may be uninformative.
All arms mostly fail at the cap; ratios near1 provide little evidence about relative ability.
O/A8 is unresolved; this does not establish equality or that old syntax carries useful help.

Between-build log-SD: {'A8': 0.0, 'O': 0.0}. O identities: ['BE1|A8', 'BE2|A8', 'BE3|A8', 'BE4|A8', 'PA1|A8', 'PA2|A8', 'PA3|A8', 'PA4|A8'].

The stage2 price is a conditional scenario based on four development cells and pilot variance. Independent fresh builds are required. Both build and baseline-seed uncertainty enter the half-width calculation; increasing builds alone cannot eliminate a fixed baseline floor.

Fixed16-seed/cell baseline floor factor: 1.000.
Measured sustained effective workers used for pricing: 2.83.

{'mode': 'baseline_grows_with_builds', 'fresh_builds': 8, 'protected_cells': 8, 'fitted_target_seeds_per_build_cell': 2, 'G4_seeds_per_protected_cell': 16, 'half_width_factor': 1.0, 'jobs': {'acquisition': 256, 'G4': 128, 'A8': 128, 'O': 128}, 'acquisition_plus_G4_A8_evaluations': 4194304.0, 'acquisition_plus_G4_A8_worker_seconds': 194.0310666700825, 'projected_compute_wall_seconds': 68.47803464487238, 'optional_O_additional_worker_seconds': 77.94392433483154, 'optional_O_additional_evaluations': 1048576.0, 'caveat': 'conditional scenario; development build variance held constant, not divided by number of protected cells; O artifact supply/confirmation design requires separate approval'}
{'mode': 'baseline_fixed16_per_cell', 'fresh_builds': 8, 'protected_cells': 8, 'fitted_target_seeds_per_build_cell': 2, 'G4_seeds_per_protected_cell': 16, 'half_width_factor': 1.0, 'jobs': {'acquisition': 256, 'G4': 128, 'A8': 128, 'O': 128}, 'acquisition_plus_G4_A8_evaluations': 4194304.0, 'acquisition_plus_G4_A8_worker_seconds': 194.0310666700825, 'projected_compute_wall_seconds': 68.47803464487238, 'optional_O_additional_worker_seconds': 77.94392433483154, 'optional_O_additional_evaluations': 1048576.0, 'caveat': 'conditional scenario; development build variance held constant, not divided by number of protected cells; O artifact supply/confirmation design requires separate approval'}

Source/fallback incidence and full acquisition costs are in source_summary.json; exact-check tails and fitting/batch load are in timing.json and preparation.json. Per-cell solves and bootstrap details are in result.json.

PIPE is the external-fitting precedent; DreamCoder connects library learning and search policy. This literal-window recipe does not test a new learning principle. No pilot observation is promoted to the digest.
