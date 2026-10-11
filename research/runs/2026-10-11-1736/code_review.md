---
verdict: pass
---

# Code review — 2026-10-11-1736 (recurrent inherited library choice)

Reviewed commit range `fa56829..3a18ef5` (worktree HEAD `3a18ef5`, clean), [proposal](proposal.md), [critique](critique.md), [plan](plan.md), [queue](queue.yaml), [preparation](preparation.md) and the `smoke-v2` artifacts. Re-ran `tests/test_recurrent_library.py` at HEAD (13 passed), `run_queue.py --validate` on the queue (OK, two entries, 9,000 s summed timeouts, under the 8 h cap), and confirmed the committed method hashes are digest-identical to the ones recorded by the final smoke's `method_freeze.json`.

## Blocking issues

None.

## What was verified

1. **Arm wiring.** L: library donors, no shuffle. S: library donors, `shuffle_modifiers=True`. N: `donor_library=None`, so both bit states use ordinary donors; the shared validator rejects any library draw in N or in state 0. Initial carriers are 16/256 from an arm-independent `assignment` seed, so L/S/N start from identical bit slots per (library, population).
2. **Mutation rule.** Child inherits the recipient's bit, then with probability 1/32 is redrawn from Bernoulli(1/16) before variation; the redrawn bit decides the donor law and is kept on rejected edits; elites keep their own bits. Implied conditional rates 1/512 and 15/512 are checked by a test and by the smoke (0.00204 and 0.0306). With `modifier_mutation_probability=0` the engine's draw sequence is unchanged, and the replay test compares against the committed 1427 engine `f8f4246` for all three arms.
3. **Episode structure.** Twelve 64-generation episodes, balanced cell rotation (each cell first in 24 trajectories per arm, each cell twice per trajectory), programs reset per episode, bits persist (validator checks `initial_f == prior final_f`), `continue_after_solve=True` so exposure is equal across arms.
4. **Readout.** Each of the 432 endpoints is scored separately at `q = 0.5 * final_f` with its own library; `final_f = 0` yields `q = 0` and ordinary search, which `execute_readout` handles (no donors). References q₀ = 1/32 and R-all = 0.5 are scored once per (library, cell, population, repeat) block, with the same 8 restart seeds shared across all five laws in a block (asserted by test). Grid 5,184 + 3,456 = 8,640, no duplicates (validator keys on cell/arm/build/repeat with repeat = 2p + r). Failed jobs are forced to 524,288 evaluations.
5. **Analysis.** Costs average within population, then within library, then across libraries; the bootstrap resamples libraries and populations nested, using one index set for all laws so each endpoint stays attached to its reference block, and shared references are never duplicated as independent observations (test covers both properties). `classify()` implements the four frozen branches exactly as plan.md states them.
6. **Fail-closed paths.** Readout refuses partial exposure, smoke/full mismatch, artifact, method, schedule or seed-audit drift, and endpoint-extraction drift; all exercised by `smoke_validation.py`. Deadlines: batch aborts at the fixed deadline and writes `failure.json`, so the only ways the readout stops are the right ones.
7. **Gates / stop rules.** There is no pilot or power gate that decides whether the main stage runs; both entries run serially at the approved fixed size. The precision sensitivity script is informational and not wired into the queue. No risk of stopping the main stage for the wrong reason.
8. **Timing margin.** Smoke worker sums scale to about 7 min exposure and 56 min readout at ten workers, against 29.5 and 119.5 min deadlines. A failed readout job costs roughly 40 s, so even ~10% failures stay inside the readout window.
9. **Critique.** Notes 1–5 are addressed in plan.md and in code/report fields (anchors and solve counts listed, nested paired precision calculation labelled as synthetic, "20% saving excluded for this procedure" branch, headroom treated as a limitation, Kim et al. reworded). Notes 6–8 concern digest/question wording outside the researcher's write scope; plan.md records them for the steward, which is an acceptable reason not to act here.

## Minor notes (not blocking)

- **S-arm modifier stream.** In S the shuffle and the redraw draws come from the same `modifier_seed` RNG, so S's mutation events are not draw-for-draw paired with L and N even though the seeds are. The analysis should not describe mutation events as paired across S and the other arms; seeds-paired is accurate.
- **Headroom hint from the smoke.** In the one-library smoke, q₀ = 1/32 was cheaper than R-all (initial/R-all point 0.42 on 12 jobs each), the opposite of the forecast 1.9×. This is far too small to decide anything, but if the full run gives q₀/R-all below 1.25, the plan's own rule makes the candidate uninformative; `classify()` does not apply that caveat, so the analysis must apply it by hand before reading a "20% excluded" or "unresolved" branch as evidence about inheritance.
- **Zero-carrier endpoints** deploy as ordinary search (q = 0). The report counts them (`zero_endpoints`); the analysis should state how many endpoints per arm were scored at q = 0, since those rows carry no library at all.
- **Smoke provenance.** The smoke manifest's `git_commit` is `fa56829` because the smoke ran before the commit; the method hashes it recorded are identical to HEAD, so the smoke exercised the committed code.
- **Pre-existing failures.** The two `test_order_cap.py` failures come from the 1129 frozen-method guard rejecting any change to `tree_gp_search.py` and also fail at the base commit; they are unrelated to this runner.
- **S elites keep the shuffled bit**, as in 1427 (shuffle precedes elite selection). Consistent with the frozen description, just worth remembering when interpreting S's final frequencies.
