# Stop: revised acquisition costs narrowly fail the admission gate

Stop before the substantive queue, per the approved proposal, plan and researcher role. This is a **cost-admission failure**, not an unreachable-target or validation failure. The reduced-reference timeout sum is **10868 seconds (181.13 minutes)**, **68 seconds above** the pre-stated 10800-second ceiling. Do not silently shave the allowance or reduce acquisition replication to pass it.

Evidence: [projection and both roster prices](cost/projection.json), [four timing acquisitions](stage0/timing.json), [timing progress](stage0.log), [validation](final-smoke/validation.json), [preparation checks](preparation.md), and individual files under `stage0/acquisition/timing/`. No new frozen search was scored during preparation. The four timing vectors are excluded from any substantive inference.

| Family / arm | Seconds | First exact solves / 48 | Verification seconds | Population evaluation seconds | Reproduction seconds |
|---|---:|---:|---:|---:|---:|
| sum inherited | 181.38 | 35 | 8.35 | 29.62 | 138.84 |
| sum broken | 174.65 | 25 | 1.90 | 31.00 | 137.03 |
| max inherited | 396.47 | 26 | 236.41 | 26.53 | 129.41 |
| max broken | 433.38 | 19 | 276.49 | 26.39 | 126.27 |

Every run completed exactly **6144 reproduction generations, 6192 population censuses and 6340608 population evaluations**. Every episode completed 128 reproductions and 129 censuses regardless of its first solve. Broken arms shuffled after every census, including solved and final censuses. Mean/max lineage depths: sum inherited 6102.38/6107, sum broken 6131.75/6132, max inherited 5995.34/6029, max broken 6129.56/6130. These diagnostics do not equalize selection intensity or establish a mechanism.

The proposal anticipated about 260 seconds/acquisition, including at most about 90 seconds of verification. The measured max runs cost 1.52–1.67 times the anticipated acquisition time; verification alone cost 2.63–3.07 times the allowance. Their first exact witnesses were checked through 247460 and 211760 fresh verifications, respectively. Continuing selection after solving changes later modifier trajectories and resets, so the old verifier estimate was not an upper bound. No scientific inference is made from one timing run per cell.

Four-worker timing wall-clock was **434.01 seconds**, with **68.31% realized utilization**: sum workers finished first while max workers remained busy. These four measurements do not establish ten-worker throughput or runtime tails. Pricing extrapolates worker work to ten workers and adds an explicit final-worker allowance, then doubles that estimate and adds fifteen minutes of checks/overhead. It is a planning allowance, not a tail guarantee.

## Exact pre-stated gate

Scoring is priced only from the prior 2243 timing files, by target × vector-kind mean and the exact roster. New fixed-duration vectors were not screened, scored, selected or tuned. Cost-source SHA256s and acquisition diagnostics are recorded in `cost/projection.json`.

| Roster | Mean-based acquisition estimate incl. final-worker allowance | Sum scoring estimate | Max scoring estimate | Expected queue wall-clock | Timeout sum |
|---|---:|---:|---:|---:|---:|
| 80 acquisitions + 2560 learned + 768 reference searches (64 reference seeds/target) | 46.03 min | 10.47 min | 30.96 min | 87.46 min | 11397 s = 189.95 min |
| Same acquisitions/learned searches + 384 references (32 reference seeds/target: approved fallback) | 46.03 min | 9.97 min | 27.05 min | 83.05 min | 10868 s = 181.13 min |

Full timeouts: acquisition **5824 s**, sum **1407 s**, max **3866 s**, analysis **300 s**. Fallback: acquisition **5824 s**, sum **1347 s**, max **3397 s**, analysis **300 s**. The permitted fallback was evaluated arithmetically; no substantive runs were executed. It still fails the three-hour gate. Neither estimate proves that actual execution would exceed three hours: this is a narrow admission failure under the policy written before timing, not evidence of scientific infeasibility.

## What could work instead (steward re-plan required)

The code and scientific targets work. A revised allowance of **190 minutes** would admit the full roster under these measured means; that is not a validated tail guarantee and should be considered with the uncertain ten-worker utilization and changed acquisition trajectory. Alternatively, remove the remaining extra descriptive reference seeds and retain only the 16 shared contrast seeds. That would keep all 80 acquisitions and 2560 learned searches, reducing references to 192; it requires approval because the existing fallback retains 16 extra seeds. Another option is reviewed acquisition/scoring stages with a separately funded scoring decision. Do not cut acquisition replication or choose maps/families by timing solves. Further verifier optimization would need its own correctness checks and re-timing, not an unreviewed last-minute gate adjustment.

The substantive **queue.yaml was not written or launched**, as required on infeasibility. Preparation remained within the 120-minute limit. The implementation is committed on the task branch; task artifacts are written only into this main-checkout run folder and are not committed on the research branch.

## Reusable implementation

The reviewed modifier path from `25f929e` is retained. Fixed-duration acquisition preserves first hits, skips verification after a witness and continues normal selection/reproduction. CLI stages save acquisitions, score each family separately and reject inconsistent manifests/missingness. Analysis now uses **20** acquisitions/arm, **uniform/inherited** as primary, separate family verdicts, paired acquisition resampling and shared target-seed resampling across every vector/contrast. It consistently reports **S = inherited/scaffold**; S lower < 2 means a twofold disadvantage is not established, while S upper < 2 supports within-twofold. Extra reference seeds remain descriptive. Run-level SDs, capped costs/solve counts, exposure, Price covariances, token trajectories and break-even costs are emitted for a future approved queue.

Validation and smoke pass: **111 tests** (22 mechanism/staging/analysis and 89 regression), Ruff and git diff checks. No Rust changes. See preparation.md for artifact provenance: timing ran from an intermediate dirty source state; subsequent changes added pricing/analysis/plot plumbing and corrected the logged configuration generation count without changing the timed fixed-duration acquisition law.

Implementation commit: `c01f16d` on `research/2026-10-08-0843` (reviewed base cherry-pick `82d2d02`). Worktree is clean; neither commit includes research/ files.
