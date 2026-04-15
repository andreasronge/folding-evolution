# Chemistry-Tape GP — Overview

A reader-friendly summary of the chem-tape research track: what the design is,
where it currently stands, and which experiments did the load-bearing work.
Authoritative sources (with full detail, scope tags, and commit anchors):

- [architecture.md](architecture.md) — v1 design spec (stable)
- [architecture-v2.md](architecture-v2.md) — v2 probe (alphabet expansion)
- [experiments.md](experiments.md) — v1 experimental record
- [experiments-v2.md](experiments-v2.md) — v2-probe chronicles
- [findings.md](findings.md) — durable scope-tagged claims

---

## 1. What is Chemistry-Tape?

Chem-tape is a genotype-phenotype mapping for genetic programming. The
genotype is a fixed-length **token tape**; the phenotype is a **stack
program** decoded out of that tape by a simple, deterministic "chemistry"
rule. The bet is that this indirection produces scaffold-like evolutionary
dynamics on a 1D substrate that batches cheaply on M1 hardware.

```
Genotype (tape of ~32 cells, one token per cell — the only thing selection sees)
    │
    ▼
Chemistry rule: adjacent cells "bond" when both tokens are active (non-NOP)
    │
    ▼
Phenotype: a bonded run of tokens, extracted as an RPN (postfix) program
    │
    ▼
Stack machine executes the program on inputs → output → fitness
```

Two properties make this interesting as a representation:

1. **Neutral reserve.** Any cell that contains `NOP` (or lies outside the
   extracted bonded run) is evolutionary dark matter — mutations there don't
   change the phenotype. That reserve gives drift somewhere to explore
   without breaking working programs.
2. **Scaffold preservation.** Because the bonded run is extracted rather than
   executed in place, crossover and mutation can rearrange or duplicate
   fragments without shattering the program the way Lisp-tree GP does.

**Decoder arms.** Two decoders are under active comparison:
- **Arm A** (direct GP baseline): the whole tape is the program; no chemistry.
- **BP_TOPK** (chem-tape proper): chemistry bonds adjacent active cells; the
  extracted program is the top-K longest bonded runs (`k=3` by default,
  `bond_protection=0.5`). This is the chemistry-layer-on variant.

**v1 vs v2-probe.** v1 runs a 14-token alphabet sufficient for short integer
and string tasks. The **v2 probe** adds six primitives (`MAP_EQ_E`, `CONST_2`,
`CONST_5`, `IF_GT`, `REDUCE_MAX`, `THRESHOLD_SLOT`) to test whether v1's
mechanism findings survive at richer expressivity — without committing to
full folding-Lisp parity. v2 probe is where most current results live.

---

## 2. The north-star question

> **Does chem-tape's "body-invariant-route" mechanism scale with
> expressivity, or is it a v1-scale artifact?**

"Body-invariant route" is shorthand for: two tasks that differ only in
*which op or constant is bound to a task slot* evolve a **single shared
program body** and route the task-specific bit through the slot. v1's
§v1.5a-binary showed this at 20/20 cross-task solves when the varying axis
was an op (`MAP_EQ_R` vs `MAP_IS_UPPER`). The v2 probe tests whether that
absorption extends to (a) a wider primitive set and (b) constant variation.

Four possible regimes frame the decision tree:

| regime | what it means |
|---|---|
| **Scales cleanly** | ≥3/4 graded v2-probe experiments pass their pre-registered bar → commit to full v2 + v3 chemistry ablation. |
| **Swamped by expressivity** | v2 primitives are so permissive that the mechanism has nothing to absorb (ceiling too high to measure). |
| **Does not scale** | v1 findings are rep-scale-specific; paper claim confined to v1. |
| **Partial** | Mixed outcomes with a characterizable edge — narrower claim, still mechanistic. |

Current combined verdict: **Partial, with a sharp decomposition** (see §4).

---

## 3. Current findings — the durable claims

Three claims live in [findings.md](findings.md) with scope tags, supporting
experiments, and commit anchors. Each is narrower than it sounds, by design.

### 3.1 `op-slot-indirection` — ACTIVE

When two binary tasks share a token-identical body and differ only in the
**op** bound to a task slot, evolution discovers the body once and solves
both tasks via that body.

- Established at v1 (§v1.5a-binary, 20/20) and replicated at v2 scale across
  both within-family and cross-family MAP ops (§v2.2, 20/20 on both pairs).
- Scope: MAP-family ops on a 4-cell scan-map-aggregate body, at
  `pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5)`.

### 3.2 `constant-slot-indirection` — NARROWED

When two binary tasks share the body `INPUT SUM THRESHOLD_SLOT GT` and
differ only in an integer bound to `THRESHOLD_SLOT`, evolution solves both
tasks via the shared body.

- Established at precision: **80/80 BOTH** across four seed blocks on
  `{sum_gt_5_slot, sum_gt_10_slot}` (§v2.3), with 399/400 zero-cost flip
  transitions.
- **Narrowed to one pair / one body shape** after §v2.6 breadth check
  failed: 0/3 new pairs scaled (two were swamped at Fmin=20/20, one failed
  the scales bar). The "across-family" extension is not supported.
- **Decoder-dependence caveat** (added from §v2.6-pair1 follow-ups): on
  6-token bodies, Arm A direct GP at 1× compute ≈ BP_TOPK at 4× compute.
  Decoder arm is a real lever of comparable size to compute.

### 3.3 `proxy-basin-attractor` — ACTIVE

When the training data contains a single-predicate (e.g., `max > 5` or
`sum > 10`) whose accuracy on the labels is ≥ ~0.90, evolution under
BP_TOPK reliably converges to that predicate alone — even when the true
label requires AND-composition, and **even at 4× compute**.

- Established by the §v2.4 → §v2.4-alt → §v2.4-proxy sequence. Original
  framing "compositional depth doesn't scale" was **falsified** by
  §v2.4-alt (threshold=5 solves at 17/20 on the same compositional shape).
- The mechanism is the **basin shape**, not the specific predicate:
  decorrelating `max > 5` just routes evolution to `sum > 10`.
- Sampler design (class-balanced, proxy-decorrelation-aware) is now a
  first-class experimental axis for any AND-composition follow-up.

---

## 4. The most interesting experiments

The chronicles in [experiments-v2.md](experiments-v2.md) are dense. Here
are the ones worth reading for the story arc.

### §v2.2 — Multi-slot indirection *(scales cleanly)*
Two pairs alternating across MAP-family slot bindings. **20/20 BOTH on both
pairs**, train and holdout. The cleanest positive result of the suite; the
v2 replication of v1's §v1.5a-binary finding under a richer alphabet.

### §v2.3 — Constant-slot indirection *(scales cleanly, at precision)*
The sharpest body-invariance test in the suite: two tasks with
**token-sequence-identical** bodies, differing only in a task-bound
integer. Recovers v1's §v1.5a-internal-control failure: **80/80 BOTH**
across four seed blocks, max |train-holdout gap| = 0.0156, 399/400
zero-cost flip transitions. This is the load-bearing positive result.

### §v2.4 → §v2.4-alt → §v2.4-proxy — The compositional mystery
- **§v2.4** (F_AND = 0/20 at 1× and 4× compute): first read as "does not
  scale on compositional depth." Direct genotype inspection instead found
  that 14/20 seeds converge to an exact `max > 5` predicate — a proxy that
  scores ~0.92 on both train and holdout.
- **§v2.4-alt** (body-matched compositional pair, threshold=5 scored
  17/20): **falsifies** the compositional-depth framing. The same
  `IF_GT + CONST_0`-prefix shape is solvable when no strong proxy exists.
- **§v2.4-proxy** (decorrelated sampler): shifts the attractor from
  `max > 5` to `sum > 10` — evolution finds whichever single-predicate is
  best-in-distribution. Mechanism generalised, renamed from "max>5 proxy"
  to "single-predicate proxy basin."

Methodology lesson: **direct genotype inspection + sampler redesign
reframed a structural-failure claim into an attractor-mechanism claim in
two sweeps.** Zero-compute inspection is load-bearing.

### §v2.6 — Task-diversity breadth check *(FAIL, by its own rules)*
Three additional body-invariant pairs meant to extend §v2.3's claim from
one pair to four. Verdict: **0/3 pairs scale** — Pair 1 (6-token
string-count body) failed at 4/20, Pair 2 and Pair 3 were **swamped** at
Fmin=20/20 (baseline too permissive to measure any alternation lift).

Methodology lesson: **a test that cannot fail is not a test.** Threshold
selection in the prereg is a dependent-variable carrier — pre-registering
permissive thresholds pre-accepts swamp and wastes compute.

### §v2.6-pair1 follow-up sweeps — decoder × compute × tape
Four follow-ups on Pair 1 (the non-swamped failure):
- **4× compute** → 4/20 → 8/20 (INCONCLUSIVE). Assembly barrier closes
  (`ADI = 0.00`); component-discovery barrier remains.
- **16× compute** → 13/20 (PASS-partial, discovery-limited). Compute has
  diminishing returns under BP_TOPK(k=3).
- **Arm A direct GP at 1× compute** → 7/20 (PASS-partial). Roughly matches
  BP_TOPK at 4× compute — decoder arm is a real lever.
- **Tape length 24 at 1× compute** → 6/20 but with **zero seed overlap**
  to baseline. Net-positive BOTH came entirely from seed substitution, not
  from extending baseline's solved set. Misleading without the overlap
  diagnostic.

Methodology lesson: report **seed-set overlap**, not just solve counts.
Two +2 gains can mean very different things.

### §v2.7 — Assembly-transition rates *(CONTROL-DEGENERATE)*
An attempted landscape analysis using §v2.3 as a control. The pre-reg had
a degeneracy trigger that **fired**: §v2.3 is so easy that 15/20 seeds
reach canonical in < 20 gens, making the ratio-based test uninterpretable.
No mechanism reading was promoted — the pre-registered short-circuit
saved an hour of uninterpretable compute. An example of pre-registering
the degenerate case doing real work.

---

## 5. Combined v2-probe verdict

| axis | verdict | status |
|---|---|---|
| §v2.1 K-alternation | Swamped (F_10_v2 = 18/20) | threshold noted as permissive |
| §v2.2 op slot-indirection | **Scales cleanly** | 20/20 on both pairs |
| §v2.3 constant slot-indirection | **Scales at one-pair precision** | 80/80 on `sum_gt_{5,10}_slot` |
| §v2.6 breadth of §v2.3 | **FAIL** | 0/3 pairs scale; §v2.3 does not extend across-family |
| §v2.4 compositional | Failure reframed | attractor-driven, not depth-driven |
| §v2.5 aggregator (exploratory) | 20/20 co-solve | consistent with scaling |

**Paper-scope headline:** evidence for slot-op indirection (§v2.2) and
slot-constant indirection at one precision pair (§v2.3); compositional
failure reframed as a single-predicate proxy basin under AND-composition.
**Not claimable:** "across-family constant indirection", "four task
families", "compositional depth fails generally".

---

## 6. Open questions / what's being probed next

Active pre-regs queued in [`Plans/`](../../Plans/):

- **§v2.8** — 6-token integer-domain body to disambiguate body-length from
  input-domain on Pair 1's failure (isolates body-length confound).
- **§v2.11** — Arm A direct GP on §v2.3's precision pair: does the 80/80
  result hold when you strip the chemistry layer?
- **§v2.12** — Arm A on the §v2.4 proxy-basin tasks: is the proxy basin a
  property of greedy search in general, or BP_TOPK-specific?
- **§v2.13** — BP_TOPK `k=5` sweep: does widening the extraction window
  help or hurt, and on which body shapes?

Standing open questions not yet probed:

- Does a redesigned §v2.6' at Fmin-intermediate thresholds land an
  across-family constant-indirection claim?
- Does simultaneous decorrelation of multiple proxies (§v2.4-proxy-2)
  produce a novel attractor or confirm the basin story generalises?
- Can the G→P mapping itself be evolved (level-2 probe, deferred pending
  v2-probe scope decisions)?

---

## 7. How experiments are run

- Overnight queue: `queue.yaml` at repo root defines entries;
  `scripts/run_queue.py` executes them; per-run output lands under
  `experiments/output/YYYY-MM-DD/<entry_id>/`.
- Morning summarization: `scripts/summarize_runs.py` invokes the Claude
  CLI on each new run's metadata + logs + result file, writing
  `summary.json` with a structured PI-briefing payload.
- Pre-registration and result-logging workflow is enforced by the
  `research-rigor` skill, following [`docs/methodology.md`](../methodology.md)
  and the templates in [`docs/_templates/`](../_templates/).
