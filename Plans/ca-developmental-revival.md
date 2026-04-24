# CA Developmental Revival — Visuals, Regeneration, Morphology

**Purpose:** Shift the CA track from "can the CA compute?" to "is the CA actually developing?" Thirteen sweeps have bounded rule-family expressivity, search pressure, I/O geometry, and λ-class. Two mechanisms (banded_3, phased_2) broke the 8-bit parity ceiling to ~0.81 median / 0.97 best. Those evolved rules are sitting on disk, and no sweep has yet asked whether what they do qualifies as *development* in any meaningful sense.

**Approach: visuals first, probes after, dashboard last.** For a hobby project the fun multiplier is huge when you *watch* the thing before you measure it. The atlas tells you in one evening whether there is anything worth poking. Damage and I/O probes land more informative readings once the undamaged trajectories are in your head. The dashboard grows organically around whichever trajectory you keep wanting to rewatch — not a pre-designed control panel with every slider you can imagine.

**Not a pivot.** The chem-tape v2 probe stays where it is — §v2.5-plasticity-2d finishes its one cell, and that claim lands as-is. This plan reactivates the CA track in parallel. The folding paper is still the paper. This is the next chapter.

**Hobby-mode methodology.** Lab notebook, not courtroom. One paragraph per run before launch ("what would be interesting to see?"), chronicles go straight into `docs/ca/experiments.md` under §14+. No prereg, no codex review gauntlet, no FWER audit unless a result survives and wants to grow into a paper-grade claim. If a probe produces something surprising, *then* rigor catches up.

---

## Motivation — the gap in the existing CA work

The CA track already has real experimental depth:

- K=2 representational cliff (triple-confirmed, task-invariant)
- K=4 sufficient, K=8 redundant; grid size near-flat at tested range
- Parity-vs-majority gap widens with n_bits (Mitchell/Crutchfield reproduced on clean data)
- Symmetry matters: OT beats DT under matched budget (symmetry = inductive bias, not just compression)
- Two independent ceiling-breakers on 8-bit parity: spatial specialization (banded_3, §11.a, 0.969 max) and temporal specialization (phased_2, §11.b, 0.961 max)
- Langton's λ does not predict fitness (§13) — evolved rules sit in the same λ band as random rules

What all thirteen sweeps share: the CA is scored as a static function. Input → T steps → readout cell → accuracy. Nothing in the existing suite tests whether the evolved dynamics do the things *development* is supposed to do — canalize, self-repair, redeploy under perturbed I/O, produce reusable spatial structure. The project's stated thesis is *developmental encodings*. The CA is the cleanest developmental substrate in the repo. It has never been stressed as one.

Two concrete hints from the existing chronicle already scream "watch this":

- Banded_3's 8 errors concentrate at bit-count=5 (one residue class, every other cleanly solved). `docs/ca/experiments.md:410–421`.
- Phased_2's errors spread across bit-counts with a peak at 4. `docs/ca/experiments.md:502–516`.

Two rules with nearly identical fitness numbers and visibly different internal computations. Static metrics can't see that. Space-time diagrams probably can.

---

## Reframe

Three questions replace "what's the fitness?":

1. **Canalization.** If you perturb the grid mid-development (randomly zero or randomize a fraction of non-input cells at t = T/2), does the final readout survive? A brittle rule collapses; a canalized rule repairs.
2. **I/O plasticity.** If you shift the input row sideways, or read from a neighboring output cell, or change the input layout (clamped row 0 → scattered cells), does the rule degrade gracefully? Evolved rules with real structure degrade gracefully; lookup-like rules cliff.
3. **Morphology.** What does a best-of-run rule *look like* running across the input space? Are there traveling waves, domain boundaries, role-specialized bands, attractor cycles?

All probes pick from evolved winners sitting in `experiments/ca/output/` rather than evolving fresh. Artifacts already exist on disk.

---

## Probes — in priority order

### 1. Visual atlas — render the substrate before probing it

**Zero new training compute.** Reload the three rules of primary interest: uniform-OT best, banded_3 best (seed=2, fitness 0.969), phased_2 best (seed=8, fitness 0.961). Render space-time diagrams (`N × T` grid, state-colored) for all 256 inputs, sorted by bit-count. Output: one 16×16 thumbnail sheet per rule. Ideally side-by-side (banded vs phased on the same input) because the question is whether the two rules look mechanistically different at the pixel level.

**Static frames first, motion where it matters.** Thumbnails are for comparison (sort, eyeball, spot patterns). GIFs or animated sliders are for the 3–5 specific inputs where the trajectory itself is the story — most likely the bit-count=5 boundary where banded concentrates its errors. Building the renderer once serves every subsequent probe and eventually the dashboard.

**Plots:** 16×16 thumbnail sheet per rule; bit-count=5 animated side-by-side banded vs phased; overlay showing which inputs each rule gets wrong.

**What this decides.** If the three rules are visibly different and the two winners look qualitatively distinct from the uniform baseline, there's something worth poking. If they all look the same, the §11 ceiling-breakers were probably capacity stories dressed up as specialization, and the whole plan needs rethinking. Either outcome in an evening.

### 2. Damage assay — the first real robustness probe

**Also zero new training compute.** Reload the same three rules. At `t_damage ∈ {4, 8, 12}`, randomly zero (or randomize) a fraction `p ∈ {0.1, 0.25, 0.4, 0.6}` of non-input, non-readout cells. Replay to T, score accuracy on the full 256-input space. 20 damage realizations per input × 3 rules × 3 timesteps × 4 damage levels.

**Damage scars — the clean one-line diagnostic.** For each (rule, input, damage config), plot Hamming distance between damaged and undamaged trajectories over time. Three shapes:
- Converges back to zero → repair.
- Stays fixed at the damage size → damage absorbed but not corrected.
- Grows → chaos / broken canalization.

That plot is probably the most legible one the CA track can produce. If banded_3 shows repair curves on p=0.25 damage where uniform-OT shows chaos curves, that's the headline.

**Controls:**
- Random-rule at λ-matched density with the same damage schedule; should chaos-diverge.
- Early-damage vs late-damage: `t=4` tests canalization-under-development, `t=12` tests robustness once the pattern is mostly set.

### 3. I/O-shift probe — is robustness structural or geometry-exact?

**Zero new training compute.** Reload the same three rules. Modified I/O conventions:
- Input row shifted to row 2 instead of row 0 (readout row stays N−1).
- Input bits scattered to non-adjacent columns (cols 2, 5, 8, 11) instead of contiguous (6–9).
- Readout cell shifted to `(N−1, N/2 ± 2)` instead of `(N−1, N/2)`.

**What it tests.** Rules that encode structure degrade smoothly; rules that encode coincidences of the training input layout cliff. The §8-b null ("readout aggregation doesn't matter") was about *pooling*, not *position* — this is the position test. Less emotionally fun than §1–§2, scientifically essential. Without it, "regeneration" might just mean "exact-geometry memorization under noise."

**Plot:** fitness as a function of input-column offset, swept −4 to +4. Flat → brittle. Bell → robust within tolerance. Cliff → hyper-specialized.

### 4. Rule surgery — knock out one organ at a time

**The gene-knockout probe.** Banded_3 has three bands; phased_2 has two phases. Replace one band's rule table (or one phase's) with the identity rule or a random rule table. Rescore on the full input space. Five total knockouts: bands {1, 2, 3}, phases {1, 2}.

**Hypothesis.** If band 2 is the "transducer" (marks where input bits were) and band 1 is the "reducer" (integrates to the readout), knocking out band 2 kills fitness while knocking out band 1 degrades it gracefully. If all knockouts behave identically, the bands are redundant capacity, not organs.

**Why this is more satisfying than random damage.** Asks whether the evolved system has *functional parts*. Five experiments, trivial compute, directly answers the specialization question §11.a raised but didn't resolve.

### 5. Fate maps — who is causally downstream of whom?

For each cell `(i, j)` at time T, compute which input-bit columns reach it via the rule's causal cone (reachability under the rule's local neighborhood, iterated T times). Render the N×N grid colored by which input bits can influence each final cell.

Overlay the actual state trajectories. Do transducer zones exist? Do the bands in banded_3 correspond to fate-map boundaries, or are they unrelated to causal structure? If the visible band boundaries and the causal-cone boundaries align, banded_3's specialization is real in both structural and dynamic senses. If they don't align, the bands might be doing something more subtle (or nothing).

This reframes §12's planned particle analysis in developmental-biology vocabulary (Waddington, Turing). More evocative than "particles" for the first visual pass; §12 particle theory remains the formal version that follows.

### 6. Failure galleries — what's the hidden "almost parity" algorithm?

For banded_3's 8 errors (all at bit-count=5) and phased_2's ~10 errors (spread across bit-counts), display each failed input next to its nearest-Hamming-distance correct input. What changes between them?

The §9 chronicle already proved this methodology productive (it surfaced the "predicts 0 at bit-count=7" pathology for the overfit uniform rule). Applied to the near-solvers, the pattern should expose *which specific structural fact* the rule is actually computing. The prediction is that banded and phased compute qualitatively different "almost parity" algorithms — failure galleries make that explicit.

### 7. Attractor portraits — what happens past T=16?

**Genuinely new axis.** Every existing sweep stopped at T=16. Run the evolved rules out to T=64 or T=128 on each input. Does the grid settle to a fixed point? Enter a short cycle? Drift chaotically? Keep the readout bit stable past its trained endpoint?

**Why it matters for development.** Canalization at equilibrium is the classical morphogenetic signature — a developmental program that settles into a stable final pattern. A rule that quiesces at T=32 and holds its readout is canalized. A rule that cycles is computing continuously, which is a different (also interesting) regime. A rule that drifts is not developmentally stable even when it solves the task at the trained T.

Free diagnostic, no extra training. Probably the most surprising single probe in the plan — nobody has looked.

---

## Dashboard — grown, not pre-designed

Once probes 1–3 produce a compelling visual, build an interactive viewer around *that specific thing*, not around a generic dropdown-slider panel. If damage scars on bit-count=5 are the thing you keep rewatching, that's the dashboard's v1 — one view, polished. Add controls only when you find yourself wanting to change one specific parameter repeatedly. The UI emerges from the artifact, not the other way around.

Likely v1 primitives (reuse the atlas renderer):
- Pick a rule and an input, replay with or without damage at a chosen timestep.
- Side-by-side: banded vs phased on the same input.
- Hamming-scar overlay on the replay.

What to *not* build up front: dropdowns for every rule × every task × every parameter combination. You'll know in one session which 3–5 views matter.

---

## Deferred: evolve-for-regeneration (post-atlas reframing)

Originally scheduled as probe §16 in the first draft of this plan. Correctly identified in revision as the wrong first new-training sweep — generic "evolve for damage recovery" risks turning the fun back into another fitness-sweep grind.

**Deferred, not canceled.** The post-atlas version gets specific: instead of "evolve rules that survive random damage," it becomes something like *"evolve banded rules that preserve the transducer band's state under p=0.25 damage at t=8"* — a specific mechanistic prediction grounded in whatever probes 4 (rule surgery) and 5 (fate maps) surface about which bands do which jobs. That specificity only exists after visuals. Revisit this probe when/if probes 1–7 produce a concrete robustness hypothesis worth training against.

---

## Out of scope (explicitly)

- **Meta-learning on CA substrate** (evolve CA rules that learn arbitrary 2-bit boolean functions in-context). Too many unknowns stacked before establishing whether the CA substrate actually computes rather than lucks into readout basins. Revisit after probes 1–3 report.
- **Evolvable chemistry / AutoMap.** Worth reviving separately once the CA track gives a clean signal. Not on the critical path for this plan.
- **Chem-tape v2 continuation.** §v2.5-plasticity-2d finishes its single cell as-is. No further chem-tape probes until this plan's probes 1–7 report.
- **Folding track regressions.** Closed chapter for this plan.
- **FWER audits.** Until a probe lands a surprising positive and someone wants to cite it as a paper claim, this entire plan operates on descriptive/exploratory evidence. That is deliberately the point.

---

## Sequencing

1. **Atlas renderer** (probe 1). Cheapest, most compounding. Serves every subsequent probe and the dashboard. ~1 evening.
2. **Damage assay** (probe 2) immediately after. The atlas renderer gives it the trajectory baselines for free. ~1 evening of compute + half a day of analysis.
3. **I/O-shift probe** (probe 3). Zero new training. Decides whether the §2 signal is canalization or geometry dependence. ~1 evening.
4. **Rule surgery** (probe 4). Five knockouts, trivial compute. ~1 evening.
5. **Fate maps** (probe 5) and **failure galleries** (probe 6) can run in parallel once the renderer exists. ~1 evening each.
6. **Attractor portraits** (probe 7). Trivial to add once the replay infrastructure is there. ~2 hours.
7. **Dashboard v1** emerges organically from whichever probe produced the most rewatchable visual. ~1 day when the answer becomes obvious.
8. **§12 particle/space-time diagnostic** (already queued in `docs/ca/experiments.md`). Natural bridge once probes 4–6 have given the microscope something specific to look for.
9. **Deferred: evolve-for-regeneration** with a post-atlas-specific objective.

Total budget: ~2 weeks of evenings for probes 1–7. If nothing interesting surfaces in those two weeks, the plan has falsified itself.

---

## Decision rule

Two triggers, in order:

**First trigger (after probe 1, atlas).** If banded_3 and phased_2 look qualitatively different from each other and from uniform-OT at the pixel level → continue to probes 2–3. If all three look the same → stop. The §11 ceiling-breakers were probably capacity stories, and the rest of this plan is premature.

**Second trigger (after probes 2–3, damage + I/O shift).** Keep going if either:
- Banded_3 or phased_2 retains ≥ 0.75 accuracy at p=0.25 damage where uniform-OT falls below 0.55, *and* damage scar curves show repair shape rather than chaos shape.
- Or I/O-shift shows banded/phased degrade gracefully within ±2 column offset where uniform-OT cliffs at ±1.

Both parts matter. Numerics alone could be specialization artifact; visuals alone could be anthropomorphism.

**Outcomes:**
- **KEEP GOING.** Probes 4–7 and the dashboard are worth building. The track has legs.
- **PIVOT TO CHEM-TAPE PLASTICITY V2** (the meta-learning framing, not the current prereg) if all probes collapse uniformly. CA development as executed so far was readout memorization, not structural computation.
- **CLEAN PUBLISHABLE NULL** if damage shows mixed results and I/O shift shows rigid geometry-exact dependence. The ceiling-breakers were overfit to training geometry. That's a legitimate finding.

All three outcomes ship a lesson. That's the bar for a hobby project: every two weeks of evenings should either extend a claim, kill a claim, or produce a picture you want to send to a friend.

---

## Relationship to the other tracks

- **Folding:** §1.11/§1.13 scaffold preservation was structural persistence through evolution. Probes 2 and 7 here test structural persistence through perturbation at development time. Same thesis, different axis. A positive result here strengthens the folding paper's claim that developmental encodings do something real.
- **Chem-tape:** the body-invariant-route mechanism on 4-token bodies is a different kind of canalization — token-level, not spatial. If probes 2 and 7 land, the unified framing is "canalization is the observable that developmental encodings produce; it shows up as token substitution in chem-tape, as damage recovery in CA, as scaffold preservation in folding."
- **§12 particles:** this plan makes §12 more tractable by providing the visualization infrastructure (probe 1) and a selection criterion (probes 2, 4, 5 — rules that canalize are the ones worth analyzing as particle computers). Fold §12 in once probes 1–6 have produced rules worth opening up.

---

## Why this is fun

The existing CA infrastructure already has working best-rules that solve 4-bit parity exactly and nearly solve 8-bit with spatial specialization. Nobody has watched one of those rules get hit with a bucket of noise and recover, or seen side-by-side what banded and phased *look* like doing their computation. When you render the atlas, either (a) the two rules are visibly different and the repo just gained its most watchable artifact, or (b) they look indistinguishable and you've learned something concrete about the gap between "evolution found a rule that works" and "evolution found a developmental program." Either way, one evening gets you a picture, a finding, and an obvious next probe.

The key bet: if banded_3 and phased_2 look different under damage, this direction has legs. If they don't, clean negative plus good pictures. The dashboard shows up when there's something specific worth rewatching — not before.
