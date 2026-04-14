# PSB2 Sanity Probe

**Purpose:** One-week probe to decide whether to reframe the project around inductive program synthesis from input-output examples (PBE), using PSB2 as the external benchmark.

**Not yet a pivot.** The data from this probe decides whether the PBE frame holds. If the generalization-gap story shows up, we commit; if not, we stay in the current dynamics/ceiling framing.

---

## Motivation

The current research question is internal-facing: *does a developmental encoding enable qualitatively different evolutionary dynamics?* Prior findings (ceiling break via Pareto scaffold preservation, §1.13; regime-shift adaptation; §4 diversity-loss) are legible mainly to ALife/GP-theory readers.

PBE reframes the same work as *GP representations that generalize better from few examples* — a problem with an established benchmark (PSB2) and active communities (program synthesis, neuro-symbolic, inductive programming). The reframe costs nothing if the underlying phenomena transfer. It is worth doing only if they do.

## Hypothesis

On a narrow slice of PSB2 tasks that require **structural complexity** or **long scaffolds**, the chem-tape + folding representation (with Pareto scaffold preservation from §1.11/§1.13) achieves a **smaller train→held-out generalization gap** than a matched-compute direct-encoding baseline (DEAP tree GP or minimal PushGP), even when raw training success is comparable or lower.

The claim is explicitly **not** "we beat PushGP on PSB2 leaderboard." It is "the chemical genotype produces programs that overfit less under matched compute."

## Task selection (5 tasks)

Pick tasks where structural depth matters, avoid tasks dominated by lexicase-tuned primitives:

| Task | Why it fits | Risk |
|------|-------------|------|
| Mirror Image (PSB2) | Long scaffold, symmetric structure — plays to folding's structural story | — |
| Run-Length Encoding | Requires paired primitives + counter, compositional | PushGP strong here |
| Parens Matching | Nested state, benefits from scaffold preservation | — |
| Number of Occurrences (PSB2) | Matches existing `count-R` intuition; cheap sanity check | Easy → little signal |
| Grade (PSB2) | Chain of conditionals — expected to *not* fit our rep well | Control task; we should lose or tie |

Grade is deliberately included as a negative-control task: if we win everywhere, we've overfit the framing.

## Protocol

1. **Primitives.** Extend the chem-tape VM with minimal PSB2-shaped primitives (string indexing, list primitives, integer arithmetic). Keep it minimal — do not chase PushGP's 100+ instruction set.
2. **Data split.** PSB2 ships train/test. Further split train into *visible* (given to GP) and *held-out-train* (never touched). Report held-out-train AND PSB2 test. This catches lexicase-style leakage.
3. **Baseline.** DEAP tree GP with a matched primitive set, matched population × generations budget. (PushGP is optional stretch — not required for the probe to be informative.)
   - *Optional secondary baseline:* a minimal Analog GRN (AGRN, ~32 genes, sigmoid update) decoding network activations into stack-machine tokens. If included, it positions the work against both direct tree-GP *and* the established developmental-evolution line (Banzhaf / Cussat-Blanc et al.), strengthening the claim from "better than tree-GP" to "better than tree-GP *and* AGRN." Cost: ~1 week extra implementation; only worth it if the primary probe looks positive. If the probe kills the PBE frame, AGRN baseline work is abandoned with it.
4. **Compute match.** Fix total program evaluations, not generations.
5. **Seeds.** 20 per (task × system). Report distributions, not means.
6. **Metrics.**
   - *Train success:* fraction of visible examples passed by best-of-run.
   - *Generalization gap:* train success − held-out success.
   - *Test success:* fraction of PSB2 test cases passed.
   - *Program size distribution* at best-of-run (sanity: are we producing tiny overfit programs or real structures?).

## Decision rule

After data collection:

- **Commit to PBE frame** if the generalization gap for folding is smaller than baseline on ≥3/5 tasks (including at least one non-negative-control task), at matched compute, with non-overlapping seed distributions on at least one task.
- **Abandon PBE frame** if gaps are indistinguishable, or if folding loses on generalization everywhere.
- **Ambiguous → run longer probe** if signal is directionally right but underpowered (ship the §1.14 lineage work in parallel, revisit).

## Out of scope for this probe

- Co-evolved testers. That is the natural follow-up *if* the basic generalization story holds. Evolving tests on top of a representation that doesn't help generalize is pointless.
- Evolvable chemistry (d2 bonds, DevGenome). Use fixed v1 chemistry to isolate the representation effect from the §2c efficiency story.
- Full PSB2 (25 tasks). Explicitly a 5-task probe.
- Beating PushGP. Different question.

## Budget

One week wall-clock. If VM primitive extension alone takes more than two days, stop and reassess — that's a signal the rep isn't ready for PSB2-shaped tasks yet.

## Deliverable

A short findings section (one-pass probe, not a full experiment writeup) in the appropriate track's `findings.md`/`experiments.md` with: task list, seed distributions for gap metric, decision against the rule above, and a one-paragraph recommendation on framing.

---

## Parking lot: GRN-parameterized chemistry (not part of this probe)

If the evolvable-chemistry direction (DevGenome, d2 bonds) comes back as a live priority after the PBE probe decides, there is a more principled parameterization worth exploring: **a small GRN as the bond rule itself.**

Current chemistry decides bonding via a fixed lookup on local neighborhood characters. DevGenome generalizes this with family-based d2 bonds, but the family structure is hand-designed. A GRN variant would replace both with a tiny learned network:

```
local neighborhood (chars + positions) -> small GRN (e.g. 8-16 genes) -> bond / no-bond
```

Why this is the *right* way to use GRNs in this project (and the only way that doesn't compete with the Altenberg thesis):

- **Preserves the constructional-selection story.** Spatial folding, genome extension, and scaffold accumulation all continue to work — we are only reparameterizing the chemistry rule, not replacing the substrate.
- **Makes the chemistry continuously evolvable.** DevGenome's family structure creates discrete mutation events; a GRN gives smooth weight changes, which is where the "continuous-dynamics for smoother landscapes" claim would actually have teeth.
- **Keeps the ANE angle honest.** GRNs here are tiny (order-10 genes) and many-per-individual — still not obviously ANE-shaped, but closer than whole-phenotype GRNs.

Explicitly **not** in scope now because:
- The current priority is the PBE frame decision, not chemistry reparameterization.
- If PBE fails, evolvable chemistry comes back with fixed v1 or DevGenome; the GRN variant is a *follow-up refinement*, not a reset.
- Adding it concurrently would inflate the ablation matrix (folding × chemistry × preservation × baseline) beyond what one paper can defend.

Revisit trigger: after the PBE probe decides *and* the evolvable-chemistry thread becomes the active direction.
