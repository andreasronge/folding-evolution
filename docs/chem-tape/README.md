# Chemistry-Tape GP — Overview

A self-contained introduction to the chem-tape research track. Assumes you
know what genetic programming is (a population of candidate programs,
mutation + crossover + fitness-proportional selection) but nothing about
this project's specific vocabulary. All internal jargon is defined on first
use.

Authoritative sources, if you want full detail after this overview:

- [architecture.md](architecture.md) — v1 design spec
- [architecture-v2.md](architecture-v2.md) — v2 probe (extended alphabet)
- [experiments.md](experiments.md) — v1 experimental record
- [experiments-v2.md](experiments-v2.md) — v2-probe experimental chronicles
- [findings.md](findings.md) — durable claims with scope tags

---

## 1. What is Chemistry-Tape?

Chem-tape is a **genotype-phenotype (G→P) mapping** for genetic programming.
In most GP systems the genotype *is* the program (a Lisp tree, a linear
instruction sequence). In chem-tape, there is a translation step between
them:

- **Genotype:** a fixed-length array of cells (default 32 cells), each
  holding one integer token from a small alphabet. This is the only thing
  selection, mutation, and crossover ever touch.
- **Chemistry rule** (deterministic, one-pass): two adjacent cells "bond"
  whenever both contain non-NOP tokens. Bonds form contiguous **runs** of
  bonded cells.
- **Phenotype:** one or more of those bonded runs, read left-to-right as a
  postfix / reverse-Polish-notation (RPN) stack program.
- **Execution:** a stack machine runs the program on each input example and
  produces an output. Compare outputs to labels → fitness.

```
Tape (genotype):   [NOP] [INPUT] [SUM] [CONST_5] [CONST_5] [ADD] [GT] [NOP] [NOP] ...
                          └──────────── bonded run ────────────┘
RPN program:        INPUT SUM CONST_5 CONST_5 ADD GT
Behaviour on x:     sum(x) > (5 + 5)        i.e., sum(x) > 10  →  0 or 1
```

**Why bother with the indirection?** Two design bets:

1. **Neutral reserve.** Tokens outside the bonded run are invisible to
   selection — mutations there are free exploration. This is analogous to
   "junk DNA" in biological genomes: room to drift without breaking
   working phenotypes.
2. **Scaffold preservation.** Because programs are *extracted* rather than
   stored in a rigid tree, crossover and mutation can rearrange, duplicate,
   or hide fragments without shattering the current working program. In
   Lisp-tree GP, a single bad mutation at the root destroys everything
   below it; chem-tape can often absorb the damage.

These properties matter most when a task requires a **long, structured
program** (many tokens in a specific order). Short programs don't need the
indirection; long ones might.

### The two decoders under comparison

- **Arm A (direct GP baseline):** skip the chemistry step entirely. The
  whole tape is treated as the program. Any inactive / NOP cells are
  dropped but there's no bonding, no extraction. This is the "does
  chemistry help at all?" control.
- **BP_TOPK (chem-tape proper):** apply the chemistry rule, then extract
  the top-K longest bonded runs (default `K=3`, so up to three runs
  concatenated into one program). A `bond_protection` parameter biases
  mutation against breaking existing bonds. This is the chemistry-on
  variant.

Everywhere below, "the mechanism" means a property we've shown under
BP_TOPK that Arm A lacks or is weaker at.

### v1 versus v2-probe

- **v1** uses a 14-token alphabet (NOP, INPUT, CONST_0, CONST_1, SUM, ADD,
  GT, DUP, SWAP, CHARS, ANY, REDUCE_ADD, plus two per-task slot tokens).
  Enough for simple integer and string tasks like "does this string
  contain an R?" or "is the sum of this int-list greater than 10?".
- **v2 probe** adds six primitives — `MAP_EQ_E`, `CONST_2`, `CONST_5`,
  `IF_GT` (a value-level if/else), `REDUCE_MAX`, and `THRESHOLD_SLOT`
  (see below). The goal is to test whether v1's mechanism claims survive
  at richer expressivity, without committing to full Lisp-parity.

Most current results live in the v2 probe.

### Slots: the key mechanism lever

A **slot** is a token whose semantics are task-bound rather than fixed.
Example: token `SLOT_12` doesn't have a single meaning — each *task*
declares what `SLOT_12` does in its own config:

- Task `any_char_is_R`: `SLOT_12 → MAP_EQ_R` (map each char `c` to `1 if c=='R' else 0`)
- Task `any_char_is_E`: `SLOT_12 → MAP_EQ_E` (map each char `c` to `1 if c=='E' else 0`)
- Task `any_char_is_upper`: `SLOT_12 → MAP_IS_UPPER`

These three tasks share the **identical program body** `INPUT CHARS SLOT_12 ANY`.
Only the task-bound op differs. A program evolved for one task can be used
unchanged for the others — *if* evolution actually finds that shared body.

The three ops above form the **MAP-family**: each takes a char-list and
produces a 0/1 list, differing only in predicate. When we say "within-MAP
family" we mean both tasks pick their slot-op from that family
(e.g., R vs E, both exact-character matches). **"Cross-MAP family"** means
one task uses an exact-character op and the other uses a structural op
(e.g., R vs is-upper).

The v2 probe adds a second kind of slot: `THRESHOLD_SLOT`, which pushes an
integer constant whose value is task-bound. Example:

- Task `sum_gt_5_slot`: `THRESHOLD_SLOT → 5`
- Task `sum_gt_10_slot`: `THRESHOLD_SLOT → 10`

Both share the body `INPUT SUM THRESHOLD_SLOT GT`. Only the bound integer
differs.

---

## 2. The north-star question

> **Does chem-tape's "body-invariant route" mechanism scale with
> expressivity, or is it a small-representation artifact?**

A **body-invariant route** is just a program body shared across multiple
tasks, where the task differences are absorbed by slot bindings rather
than encoded in the body tokens. If evolution can reliably *find* such
shared bodies when they exist, it gets cross-task transfer "for free" —
solving one task trains a body that already solves the others.

v1 established this at small scale with op-slot variation (one task's
slot binds `MAP_EQ_R`, another's binds `MAP_IS_UPPER`; **20 out of 20
random seeds** evolved the shared body and solved both tasks when they
alternated every 300 generations). The v2-probe asks whether this
survives when the alphabet is larger and the tasks are richer.

### The experimental setup in one paragraph

For each experiment, we run **20 independent evolutionary runs** (each
with a different random seed), each using a population of 1024 genomes for
1500 generations. When an experiment has **two tasks**, the fitness target
alternates between them every 300 generations — the population sees Task A
for 300 gens, then Task B for 300 gens, etc. A seed is counted as
"**BOTH**" when its final best genome scores ≥ 0.999 on *both* tasks
simultaneously. The headline number "17/20 BOTH" means 17 of the 20 seeds
produced a genome that solves both tasks at once.

A **"fixed baseline"** is the same setup with no task alternation — just
each task run solo. We call the per-task solo solve rate `F_task` and
define `Fmin = min(F_A, F_B)`. `Fmin` tells us how hard the easier task is
on its own, which anchors whether alternation actually added anything.

### Four possible outcomes

| outcome | what it means | decision |
|---|---|---|
| **Scales cleanly** | Most experiments pass their pre-registered bar. Mechanism generalises. | Commit to full v2 engineering. |
| **Swamped** | Fixed baselines are already at ceiling (`Fmin ≥ 19/20`). Alternation can't show a mechanism lift because there's no headroom. | Narrow the paper claim to v1 scope. |
| **Does not scale** | Most experiments fail the bar. v1 findings are rep-specific. | Pivot research direction. |
| **Partial** | Mixed outcomes with a characterizable edge. | Narrower claim, still mechanistic. |

**Current combined verdict: Partial**, with a sharp decomposition (§4).

---

## 3. Current findings — the durable claims

Three claims have survived promotion to [findings.md](findings.md) with
scope tags and commit anchors. Each is deliberately narrower than the
phrase suggests.

### 3.1 `op-slot-indirection` — ACTIVE

**Claim:** When two tasks share a token-identical body and differ only in
which **op** is bound to a task slot, evolution discovers the shared body
and solves both tasks through it.

Tested at v1 with MAP_EQ_R vs MAP_IS_UPPER (20/20 BOTH), and replicated
under the v2 alphabet across both within-family ({R, E} — 20/20 BOTH) and
cross-family ({R, upper} — 20/20 BOTH) variants.

### 3.2 `constant-slot-indirection` — NARROWED

**Claim:** When two tasks share the body `INPUT SUM THRESHOLD_SLOT GT` and
differ only in the integer bound to `THRESHOLD_SLOT`, evolution discovers
the shared body and solves both tasks through it.

Established at high precision: **80/80 BOTH** across four independent
blocks of 20 seeds on `{sum_gt_5_slot, sum_gt_10_slot}`. Plus: of the 400
task-switch events observed, **399 had zero fitness drop** — the best
genotype at the end of one task was already solving the other.

**Narrowed** because a breadth check (§v2.6) across three additional body
shapes did **not** extend the claim: two shapes had `Fmin = 20/20` (both
tasks independently trivial — no mechanism signal to measure), one shape
failed outright at 4/20. The claim is therefore restricted to this one
body shape at these thresholds, not a general "constant-slot absorbs
variation across any body" property.

**Decoder caveat:** on a 6-token body, switching from BP_TOPK to Arm A
direct GP at the same compute budget recovers 3 of the ~7 BOTH-solves
lost. Decoder choice is a real lever of comparable size to compute scaling
for bodies longer than ~5 tokens.

### 3.3 `proxy-basin-attractor` — ACTIVE

**Claim:** Under BP_TOPK, when a single sub-predicate (e.g., "is the max
value greater than 5?") achieves ≥ ~90% accuracy on the training labels,
evolution converges to that predicate alone — even when the true label
requires a compound predicate like AND, and even when we scale compute 4×.

**Why this matters:** the AND-composition tasks were originally read as
"chem-tape fails at compositional depth." Direct inspection of the
evolved genomes showed evolution wasn't failing at composition — it was
succeeding at finding a simpler-but-correlated shortcut. Disable one
shortcut by changing the input distribution, and evolution immediately
picks the next-best shortcut. The **basin** is the general thing; the
specific predicate is just whichever one the training distribution makes
cheapest.

Consequence: the sampler (how training examples are drawn) is a
first-class experimental variable. Balanced classes aren't enough — you
have to actively decorrelate near-perfect single-predicates from the label
if you want to measure compositional discovery.

---

## 4. The most interesting experiments — story arc

Read these for the narrative; the chronicles in
[experiments-v2.md](experiments-v2.md) have the numbers.

### §v2.2 — Multi-slot indirection *(scales cleanly)*

Two pairs of string tasks, alternating every 300 generations:

- **Pair A (within-MAP-family):** `any_char_is_R` vs `any_char_is_E` —
  both slot ops are exact-character matches.
- **Pair B (cross-MAP-family):** `any_char_is_R` vs `any_char_is_upper` —
  one op is exact-character, the other is structural.

Both pairs share the body `INPUT CHARS SLOT_12 ANY`. Only the slot
binding differs per task.

**Result: 20/20 BOTH on both pairs**, on train and on a held-out test
set. The cleanest positive result in the suite — proves that v1's
op-slot-indirection finding wasn't specific to the one op pair v1 happened
to test.

### §v2.3 — Constant-slot indirection *(scales at precision)*

Two tasks, **token-sequence-identical bodies** (`INPUT SUM THRESHOLD_SLOT GT`),
alternating every 300 generations. The only between-task difference is the
integer bound to `THRESHOLD_SLOT` (5 vs 10). No way for evolution to
distinguish the tasks structurally in the genome — they have to converge
to the shared body.

**Result: 80/80 BOTH** across four independent blocks of 20 seeds. Of 400
task-flip events, 399 had zero fitness drop at the flip. The maximum
train-to-holdout gap across all 80 seeds was 0.0156 — essentially no
overfitting.

This is the load-bearing positive result. It recovers a v1 negative
finding (v1's §v1.5a-internal-control had the "same" setup but without a
slot-for-constant mechanism, and scored 0/20) — showing that what looked
like a mechanism *failure* in v1 was actually a missing *primitive*
(`THRESHOLD_SLOT`).

### §v2.4 → §v2.4-alt → §v2.4-proxy — The compositional mystery

A three-step story worth reading in order.

- **§v2.4 (original):** Two AND/OR tasks on integer lists:
  - Task A: label `1` iff `sum > 10 AND max > 5`
  - Task B: label `1` iff `sum > 10 OR max > 5`

  Requires the new `IF_GT` primitive (value-level if/else). At both 1× and
  4× compute, `F_AND = 0/20`. First-pass reading: "chem-tape fails at
  compositional depth."

- **Direct genotype inspection** of the 20 failing AND seeds: 14 of them
  had evolved a tape whose RPN program was literally just `INPUT REDUCE_MAX
  CONST_5 GT` — that is, the predicate "is the max value > 5?". Under a
  uniform `[0,9]` input distribution, this predicate happens to agree with
  the true AND label on about 92% of examples. Evolution isn't failing at
  composition; it's succeeding at finding a 4-token shortcut.

- **§v2.4-alt:** Design a *body-matched* AND pair where the only
  between-task difference is a `THRESHOLD_SLOT`-bound integer (threshold=5
  vs threshold=10). Same compositional shape (`IF_GT` + `CONST_0` prefix)
  — just varied by slot. The threshold=5 task solves **17/20**. This
  directly **falsifies** "compositional depth doesn't scale": the
  compositional shape is learnable when no strong proxy exists.

- **§v2.4-proxy:** Break the shortcut. Change the sampler so that `max > 5`
  stops correlating with the AND label (drop its accuracy from ~0.92 to
  ~0.75). F_AND lifts from 0/20 to 3/20 — a genuine AND is now discoverable
  — but 11 of the remaining 17 non-solvers have converged to the *next*
  shortcut, `sum > 10` (which scores ~0.91 under the new distribution).
  The attractor is general: whatever single-predicate has highest training
  accuracy, evolution will find it.

**Methodology lesson:** zero-compute genotype inspection plus sampler
redesign reframed a structural-failure claim ("compositional depth
doesn't scale") into a mechanism claim ("greedy search under BP_TOPK falls
into whatever single-predicate basin the training data exposes") — using
two sweeps, no new compute.

### §v2.6 — Task-diversity breadth check *(FAIL, by its own rules)*

An attempt to broaden §v2.3's claim from one pair to four. Three new
body-invariant pairs, each differing from §v2.3 in a structural axis:

- **Pair 1:** string-count body (6 tokens long, uses `MAP_EQ_R` + `CHARS`).
- **Pair 2:** same sum body as §v2.3 but with inputs over `[0,12]` instead
  of `[0,9]` and thresholds `{7, 13}`.
- **Pair 3:** `REDUCE_MAX` body (aggregator variation) at thresholds `{5, 7}`.

**Result: 0/3 pairs scale.**

- Pair 2 and Pair 3 have `Fmin = 20/20` — the solo baselines are at
  ceiling. When both tasks are independently trivial, alternation-BOTH of
  20/20 is what you'd get *without* any mechanism. The result is formally
  "swamped" — uninformative either way. The prereg had actually
  pre-accepted this for Pair 3 (its thresholds were known-permissive) but
  ran it anyway, which is exactly the mistake to avoid.
- Pair 1 has `Fmin = 4/20` — the 6-token body is hard to evolve even solo.
  Alternation scored 4/20 BOTH, matching the solo floor. Genuinely doesn't
  scale on this body at this budget, but the failure is confounded between
  "body is too long" and "string-domain is harder than integer-domain."

**Methodology lesson:** a test that cannot fail is not a test. Threshold
choice during pre-registration is part of the experimental design — if
you pick permissive thresholds, you pre-commit to swamp, and the sweep
produces no evidence. Baselines must be run *before* the alternation
sweeps and must be Fmin-intermediate (not ceiling, not floor).

### §v2.6-pair1 follow-ups — decoder × compute × tape

Pair 1 was the one §v2.6 failure with headroom to probe. Four follow-ups,
each isolating one axis:

| intervention | BOTH | reading |
|---|---|---|
| baseline (1× compute, 32-cell tape, BP_TOPK) | 4/20 | starting point |
| **4× compute** | 8/20 | +4. Assembly barrier (components-present-but-mis-chained) closes; component-discovery barrier remains. |
| **16× compute** | 13/20 | +9 total. Compute helps but with diminishing returns; still doesn't clear a 14/20 "scales" bar. |
| **Arm A direct GP** (no chemistry) at 1× compute | 7/20 | +3. Roughly matches BP_TOPK at 4× compute — the decoder arm is a real lever of comparable size to a 4× compute scale. |
| **tape length 24** (shorter tape) at 1× compute | 6/20 | +2 … but **zero seed overlap** with baseline's solved set. |

The tape-length result is the interesting one. A naive read ("6 > 4,
therefore shorter tape helps") is wrong. Examining *which* seeds solved
shows that the 4 seeds that solved under the 32-cell baseline all **lost**
their solve under the 24-cell tape, and 6 entirely **new** seeds picked it
up. Same headline number; completely different seed-set. Shorter tapes
don't lift a ceiling — they shift the lottery.

**Methodology lesson:** solve counts can disguise pure seed-substitution
effects. Always report seed-set overlap, not just the count.

### §v2.7 — Assembly-transition rates *(CONTROL-DEGENERATE)*

An attempt at landscape analysis. The idea was to measure the per-
generation rate at which Pair 1 runs transition from partial-assembly to
canonical-assembly, compared against §v2.3 as a control.

The pre-reg included a degeneracy trigger for "the control is too easy"
— and it **fired**. §v2.3 is so easy that 15 of 20 seeds reach canonical
within 20 generations, making the denominator of the ratio-based test
noise-dominated. The prereg short-circuited the analysis: no mechanism
reading promoted, no expensive mutation-neighbor sampling run.

This is an example of pre-registering a degenerate case doing real work:
we saved ~1 hour of uninterpretable compute. The re-designed §v2.7'
(with a non-trivial control task) is queued.

---

## 5. Combined v2-probe verdict

| axis | verdict | reading |
|---|---|---|
| §v2.1 baseline K-alternation | Swamped (`Fmin = 18/20`) | threshold arguably permissive |
| §v2.2 op-slot indirection | **Scales cleanly** | 20/20 within-family *and* cross-family |
| §v2.3 constant-slot indirection | **Scales at one-pair precision** | 80/80 BOTH on `sum_gt_{5,10}_slot` |
| §v2.6 breadth of §v2.3 | **FAIL** | 0/3 pairs scale — claim does not extend across bodies |
| §v2.4 compositional | **Reframed**, not failed | attractor-driven, not depth-driven |
| §v2.5 aggregator (exploratory) | 20/20 co-solve | consistent with scaling |

**What the paper can claim:**
- Slot-op indirection works generally (§v2.2).
- Slot-constant indirection works at precision on one body shape (§v2.3).
- Greedy search under BP_TOPK is dominated by proxy-predicate basins
  whenever a high-accuracy single-predicate exists in the training data
  (§v2.4 reframing).

**What the paper cannot claim:**
- "Across-family constant-slot indirection" — breadth check failed.
- "Compositional depth fails under chem-tape" — directly falsified by
  §v2.4-alt threshold=5 = 17/20.
- "Constant-slot indirection works on any body" — tested only on
  `INPUT SUM THRESHOLD_SLOT GT` at thresholds {5, 10}.

---

## 6. Open questions and queued experiments

Active pre-regs in [`Plans/`](../../Plans/):

- **§v2.8** — 6-token *integer* body with no `CHARS`/`MAP_EQ_R`, at same
  budget as §v2.6 Pair 1. Isolates body-length from string-domain
  confound.
- **§v2.11** — Arm A direct GP on §v2.3's precision pair. Does the 80/80
  BOTH result hold when the chemistry layer is stripped? Tests whether
  the chemistry is load-bearing on short bodies.
- **§v2.12** — Arm A on the §v2.4 proxy-basin tasks. Is the basin a
  property of greedy search in general, or specific to BP_TOPK?
- **§v2.13** — BP_TOPK with `K=5` (wider extraction window) on §v2.3 and
  §v2.6 Pair 1. Two competing predictions: wider K absorbs tape-scatter
  (helps on long bodies) or wider K dilutes canonical bodies (hurts).

Standing open questions not yet probed:

- Does a redesigned §v2.6' with Fmin-intermediate thresholds recover an
  across-body constant-indirection claim?
- Under simultaneous decorrelation of both `max > 5` and `sum > 10`
  (§v2.4-proxy-2), does a novel proxy like `any cell > 6` step in, or
  does the AND composition finally emerge?
- Can the G→P mapping itself be evolved (e.g., genotype-encoded header
  cells that choose which ops get bound to which slots)? Deferred pending
  v2-probe scope decisions.

---

## 7. How experiments are run (infrastructure)

- `queue.yaml` at repo root lists the overnight sweep entries
  (command + timeout + expected outputs + track + notes).
- `scripts/run_queue.py` executes each un-done entry sequentially, writing
  per-run artefacts to `experiments/output/YYYY-MM-DD/<entry_id>/`
  (config, stdout, stderr, `result.json` or `sweep_index.json`, and
  `metadata.json` with commit + rusage).
- `scripts/summarize_runs.py` runs the morning after, invoking the
  Claude CLI on each new run to produce a structured PI briefing in
  `summary.json` (headline numbers, anomalies, prereg outcome match).
- Pre-registration and result-logging follow
  [`docs/methodology.md`](../methodology.md); the `research-rigor` skill
  enforces the workflow at the natural checkpoints (pre-reg, result
  logging, findings promotion).
