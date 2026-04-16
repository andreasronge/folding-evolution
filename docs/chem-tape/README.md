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

Four claims have survived promotion to [findings.md](findings.md) with
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

### 3.3 `proxy-basin-attractor` — ACTIVE (decoder-general)

**Claim:** When a single sub-predicate (e.g., "is the max value greater
than 5?") achieves ≥ ~90% accuracy on the training labels, greedy
evolution converges to that predicate alone — regardless of decoder arm
(BP_TOPK or Arm A direct GP) — even when the true label requires a
compound predicate like AND, and even when we scale compute 4×.

**Updated 2026-04-16:** §v2.12 tested Arm A direct GP on both the
natural and decorrelated samplers. Arm A traps in the same proxy basins
as BP_TOPK (attractor share 0.80 natural, 0.84 decorrelated), and the
attractor-switch pattern after decorrelation reproduces under both
decoders. The basin is now established as **decoder-general** — a
property of greedy fitness search with cheap single-predicate proxies,
not an artifact of BP_TOPK's extraction logic.

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

### 3.4 `safe-pop-consume-effect` — ACTIVE

**Claim:** Changing one line in the RPN executor — how the stack handles
type mismatches — doubles the solve rate on a hard 6-token program from
4/20 to 8/20.

**What the executor normally does ("preserve" mode):** when an op tries to
pop a value of the wrong type (e.g., `SUM` expects an `intlist` but finds
a `str` on top), the executor returns a default value *without removing*
the mismatched value from the stack. The wrong-typed value stays there,
blocking future ops from reaching useful values underneath it.

**What "consume" mode does instead:** pop the wrong-typed value off the
stack anyway, then return the default. The mismatched value is gone;
downstream ops can now reach what's below it.

**Why it matters for the 6-token body:** the program
`INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT` crosses four type boundaries
(the input is a string, `CHARS` converts it to a character list, `MAP_EQ_R`
produces an integer list, `SUM` reduces it to an integer). During
evolution, partially-assembled programs often have tokens in the wrong
order, creating type mismatches. Under preserve mode, those mismatches
leave "junk" on the stack that blocks the rest of the program from
working. Under consume mode, the junk is cleared, giving partially-correct
programs a better fitness signal and making it easier for evolution to
complete the assembly.

**The evidence:** under preserve, only 3/20 seeds assembled the full
canonical 6-token program; 6/20 got stuck at partial assembly. Under
consume, 9/20 seeds assembled the canonical program and only 1/20 got
stuck at partial assembly. The effect is specific to bodies with
multi-type chains — on the 4-token all-integer body (`INPUT SUM
THRESHOLD_SLOT GT`), both modes score 20/20. See §v2.14 in
[experiments-v2.md](experiments-v2.md) for full data.

**On AND-composition tasks** (intlist-only, no multi-type chain), consume
does not produce additional solves but shifts *what evolution attempts*:
10/20 seeds try to build AND-composition programs under consume vs 0/20
under preserve. The proxy-basin still traps them, but the exploration
landscape changes (§v2.14b).

**Implementation:** `src/folding_evolution/chem_tape/executor.py` —
the `safe_pop` function, controlled by `ChemTapeConfig.safe_pop_mode`
(`"preserve"` default, `"consume"` ablation). The Rust executor
(`rust/src/chem_tape.rs`) has the matching `safe_pop_consume` flag
threaded through `ExecCtx`.

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

### §v2.12 — Is the proxy basin decoder-specific? *(FAIL — decoder-general)*

The proxy-basin-attractor finding (§3.3 / §v2.4 arc above) was
originally established under BP_TOPK only. A natural objection: maybe
the basin is an artifact of BP_TOPK's extraction logic — perhaps Arm A
(direct GP, no chemistry layer) would escape the trap.

§v2.12 tested Arm A on both samplers (natural and decorrelated). Result:
**Arm A is trapped just as thoroughly** — 0/20 AND-solves on the natural
sampler (matching BP_TOPK exactly), 1/20 on the decorrelated sampler
(vs BP_TOPK's 3/20). The attractor breakdown mirrors BP_TOPK: under the
natural sampler, most non-solvers converge to `max > 5`; under the
decorrelated sampler, they shift to `sum > 10` variants — the same
attractor-switch pattern.

**Consequence:** the proxy basin is not a decoder artifact. It is a
property of **greedy fitness search with cheap single-predicate proxies**,
period. The decoder determines how the genome *encodes* the proxy
program, but the evolutionary dynamics — convergence to the cheapest
≥0.90-accurate predicate, robustness to 4× compute scaling, attractor-
switching under decorrelation — are decoder-invariant.

### §v2.11 — Is the chemistry load-bearing on the easy body? *(PASS — decoder-robust)*

§v2.3's 80/80 BOTH was under BP_TOPK. A natural worry: is the chemistry
layer (bonding + run extraction) doing the work, or would Arm A (direct
GP, no chemistry) achieve the same result?

**Result: 20/20 BOTH under Arm A**, with a counterfactual threshold-swap
test confirming genuine slot-indirection (not an artifact). On the
4-token all-int body, decoder choice simply doesn't matter — the body is
short enough that both decoders find it easily. This **narrows** the
decoder-arm caveat from the constant-slot-indirection finding: decoder
dependence only kicks in on bodies demanding ≥6 tokens.

### §v2.12 — Is the proxy basin decoder-specific? *(FAIL — decoder-general)*

The proxy-basin-attractor finding (§3.3 / §v2.4 arc above) was
originally established under BP_TOPK only. A natural objection: maybe
the basin is an artifact of BP_TOPK's extraction logic — perhaps Arm A
(direct GP, no chemistry layer) would escape the trap.

§v2.12 tested Arm A on both samplers (natural and decorrelated). Result:
**Arm A is trapped just as thoroughly** — 0/20 AND-solves on the natural
sampler (matching BP_TOPK exactly), 1/20 on the decorrelated sampler
(vs BP_TOPK's 3/20). The attractor breakdown mirrors BP_TOPK: under the
natural sampler, most non-solvers converge to `max > 5`; under the
decorrelated sampler, they shift to `sum > 10` variants — the same
attractor-switch pattern.

**Consequence:** the proxy basin is not a decoder artifact. It is a
property of **greedy fitness search with cheap single-predicate proxies**,
period. The decoder determines how the genome *encodes* the proxy
program, but the evolutionary dynamics — convergence to the cheapest
≥0.90-accurate predicate, robustness to 4× compute scaling, attractor-
switching under decorrelation — are decoder-invariant.

### §v2.4-proxy-2 — Dual decorrelation *(FAIL — proxy cascade)*

After §v2.4-proxy broke `max > 5` and evolution shifted to `sum > 10`,
the natural next step: decorrelate **both** simultaneously. Drop both to
~0.75 accuracy on training.

**Result: 0/20 AND-solves.** Evolution cascaded to third-tier proxies
(`sum > 15` at 0.91 accuracy, `any cell > 7` at ~0.86). The basin is
not a two-predicate phenomenon — it's a landscape property: whenever
*any* single-predicate achieves ≥~0.85 accuracy, it creates a basin.
Trapping threshold relaxed from ≥~0.90 to ≥~0.85 based on this data.

### §v2.4-proxy-3 — Split-halves boundary probe *(INCONCLUSIVE)*

Attempted to measure the exact proxy-accuracy threshold at which the
basin releases, using a split-halves AND task with independently
controllable conjunct thresholds. All conditions collapsed to trivial
solutions due to a search-space confound — the split-halves design made
the task too easy for single-element predicates. Inconclusive by its own
pre-registered rules.

### §v2.13 — Does wider K help? *(INCONCLUSIVE)*

BP_TOPK extracts the top-K longest bonded runs from the tape. K=3 was
the default. §v2.13 tested K=5 on both the easy body (§v2.3, 4 tokens)
and the hard body (§v2.6 Pair 1, 6 tokens).

On the 4-token body: **completely identical** seed-level outcomes at K=3
and K=5 — same seeds solve, same seeds fail, same stuck seed. K is a
saturated parameter here.

On the 6-token body: BOTH moved from 4/20 to 5/20, but **60% of the
combined solver set is disjoint** — K=5 unlocked different seeds, not
more seeds. More interestingly, wider K eliminated the "gt_3-only solver"
phenotype entirely (F_gt3 collapsed from 10/20 to 5/20), suggesting that
a wider extraction window dilutes the selection pressure needed for
strict 6-token assembly.

**Methodology lesson:** K is a body-shape-dependent lever, not a global
hyperparameter. On short bodies it's saturated; on long bodies it
reshuffles which seeds are navigable rather than uniformly helping.

### §v2.14 / §v2.14b — Safe-pop executor-rule ablation *(PASS + PARTIAL)*

Inspired by Kuyucu et al. (2011), who showed that small decision rules
in developmental systems can reshape evolvability. The ablation changes
one line in the RPN executor: how type mismatches are handled during
stack pops (see §3.4 above for the full explanation).

**§v2.14 (hard pair):** consume doubles BOTH-solve from 4/20 to 8/20
on the 6-token mixed-type body. Attractor inspection reveals the
mechanism: canonical 6-token assembly triples (3→9/20) while partial-
assembly drains (6→1/20). On the 4-token body: 20/20 under both rules.

**§v2.14b (AND-composition):** consume shifts the attractor landscape
dramatically (0→10/20 seeds now attempt AND-composition vs 0/20 under
preserve on the natural sampler) but does not produce additional solves.
The proxy basin holds, but what evolution *tries* changes.

**Combined reading:** the consume rule is a real executor-level lever
that affects both assembly (§v2.14) and exploration dynamics (§v2.14b),
but its solve-rate benefit is specific to multi-type-boundary chains.

---

## 4b. The proxy-basin-attractor — explained

This section unpacks the proxy-basin-attractor finding (§3.3) in more
accessible terms, since it is the most surprising and methodologically
consequential result in the chem-tape track.

### The setup

Consider a binary classification task on integer lists: "label = 1 if
and only if `(sum > 10) AND (max > 5)`." This is a **compound predicate**
— the correct answer requires checking two conditions simultaneously.

We give evolution a population of 1024 candidate programs and 1500
generations to discover this compound predicate. Each program is a short
RPN (reverse-Polish-notation) instruction sequence executed on a stack
machine.

### What we expected

We expected evolution to either (a) discover the compound predicate, or
(b) fail in some identifiable structural way — maybe the program
representation couldn't express AND, or crossover kept breaking partially
assembled solutions.

### What actually happened

Evolution scored **0/20** seeds on the AND task. But not because it
*couldn't* compose — because it *didn't need to*. Under a uniform random
input distribution over `[0,9]`, the single predicate `max > 5` alone
agrees with the true AND label on ~92% of training examples. Evolution
found this 4-token shortcut and stopped — it had no fitness gradient
pulling it toward the more complex (but only ~8% more accurate) compound
predicate.

### What is a "basin"?

In optimization, an **attractor basin** (or basin of attraction) is a
region of the search space from which the search dynamics pull toward a
particular solution. Think of a marble on a landscape of hills and
valleys: once the marble rolls into a valley, it settles at the bottom
of that valley rather than climbing over a ridge to reach a deeper valley
elsewhere.

Here, the "valley" is the `max > 5` predicate: once a population
contains individuals scoring ~0.92 via this shortcut, selection pressure
keeps refining that predicate rather than exploring the harder compound
alternative. The fitness gap between "perfect shortcut" (0.92) and
"partial compound" (often < 0.85 during assembly) means the compound
route is actively selected *against*.

### What makes this a "proxy" basin?

The predicate `max > 5` is a **proxy** — it correlates with the true
label but isn't the true label. The basin is defined not by a specific
predicate but by the **shape of the fitness landscape**: whenever *any*
single predicate achieves ≥ ~90% accuracy on the training data, it
creates a basin that traps greedy search.

We confirmed this by **decorrelation**: we redesigned the training data
sampler so that `max > 5` dropped from ~92% to ~75% accuracy. Evolution
immediately escaped that specific basin — but fell into the *next* one.
Under the new distribution, `sum > 10` became the highest-accuracy
single predicate (~91%), and 11 of 17 non-solving seeds converged to it.
Only 3 of 20 seeds found the true AND.

### Why is it decoder-general?

The original finding was under BP_TOPK (chemistry-on). §v2.12 tested
Arm A (direct GP, no chemistry). Result: Arm A traps identically. The
attractor shares (fraction of non-solvers stuck in single-predicate
basins) were 0.80 (natural sampler) and 0.84 (decorrelated) under Arm A
— nearly identical to BP_TOPK's numbers. The attractor-switch pattern
(shifting from `max > 5` to `sum > 10` after decorrelation) also
reproduced.

This means the basin is not caused by how the genome is decoded into a
program. It is caused by **how greedy selection interacts with cheap
proxy fitness** — a property of the evolutionary algorithm and the task's
fitness landscape, not the representation.

### The methodology used

- **Pre-registration:** each experiment was designed in advance with
  explicit hypotheses, outcome tables, and decision rules — before any
  data was collected. This prevents post-hoc rationalization of results.
- **n=20 independent seeds:** each experimental condition is run 20 times
  with different random seeds to measure variance, not just point
  estimates.
- **Direct genotype inspection:** rather than just reporting aggregate
  solve rates, we decoded the best genome from each seed to identify
  *which* program evolution actually found. This is how we discovered
  that 14/20 "failing" seeds had converged to `max > 5`.
- **Sampler redesign (decorrelation):** to test whether the basin was
  specific to one predicate or general, we modified the training data
  distribution to break the `max > 5` correlation while preserving the
  task's ground truth. This is the experimental equivalent of a
  controlled variable manipulation.
- **Cross-decoder replication:** testing the same hypothesis under a
  structurally different decoder (Arm A vs BP_TOPK) to distinguish
  decoder-specific artifacts from general properties.

### Why this matters for the project

The proxy-basin finding reframed a negative result ("chem-tape fails at
compositional depth") into a positive mechanistic insight: the failure is
not about representation capacity but about the interaction between
greedy search and training-data statistics. This has a direct practical
consequence: **sampler design is a first-class experimental variable**.
Any future experiment on compound predicates must actively decorrelate
high-accuracy single-predicate proxies from the label, or it will
measure basin-trapping rather than compositional capability.

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
| §v2.11 Arm A on §v2.3 pair | **PASS (decoder-robust)** | Arm A reproduces 20/20 BOTH on 4-token body; decoder choice doesn't matter on short bodies |
| §v2.12 decoder-generality of basin | **FAIL (decoder-general)** | Arm A traps in same basins as BP_TOPK; basin is not decoder-specific |
| §v2.13 K=5 parameter sweep | **INCONCLUSIVE** | K saturated on 4-token body; phenotype-mix shift on 6-token body |
| §v2.4-proxy-2 dual-decorrelation | **FAIL (proxy cascade)** | decorrelating top-2 proxies → evolution cascades to third-tier; basin threshold relaxed to ≥~0.85 |
| §v2.4-proxy-3 split-halves boundary | **INCONCLUSIVE** | all conditions collapse; search-space confound prevents boundary measurement |
| §v2.14 safe-pop ablation | **PASS** | consume doubles 6-token BOTH (4→8/20); canonical assembly triples (3→9/20) |
| §v2.14b consume on proxy-basin | **PARTIAL** | shifts attractor landscape (0→10/20 AND attempts) without escaping basin |

**What the paper can claim:**
- Slot-op indirection works generally (§v2.2).
- Slot-constant indirection works at precision on one body shape (§v2.3).
- Greedy search is dominated by proxy-predicate basins whenever a
  high-accuracy single-predicate exists in the training data — and this
  is **decoder-general**, not specific to BP_TOPK (§v2.4 reframing +
  §v2.12 broadening).
- K (extraction window width) is a saturated parameter on short bodies
  and a body-shape-dependent lever on longer bodies, not a global
  improvement direction (§v2.13).
- The executor's safe-pop rule is a real lever on mixed-type body
  assembly: consume doubles the 6-token solve rate and triples canonical
  assembly at matched compute (§v2.14). The effect extends to attractor-
  landscape structure on intlist tasks (§v2.14b) but does not escape the
  proxy basin.

**What the paper can also claim:**
- Constant-slot indirection on the 4-token body is **decoder-robust**:
  Arm A reproduces 20/20 BOTH (§v2.11). Decoder-arm dependence only
  matters on ≥6-token bodies.
- The proxy-basin cascades through at least three tiers of single-
  predicate proxies under dual-decorrelation, with a trapping threshold
  at ≥~0.85 accuracy (§v2.4-proxy-2).

**What the paper cannot claim:**
- "Across-family constant-slot indirection" — breadth check failed.
- "Compositional depth fails under chem-tape" — directly falsified by
  §v2.4-alt threshold=5 = 17/20.
- "Constant-slot indirection works on any body" — tested only on
  `INPUT SUM THRESHOLD_SLOT GT` at thresholds {5, 10}.
- "Safe-pop consume helps on all task types" — it helps on mixed-type
  chains but does not escape the proxy basin on intlist-only tasks.

---

## 6. Open questions and queued experiments

Active pre-regs in [`Plans/`](../../Plans/):

- **§v2.8** — 6-token *integer* body with no `CHARS`/`MAP_EQ_R`, at same
  budget as §v2.6 Pair 1. Isolates body-length from string-domain
  confound.
- **§v2.14c** — consume + 4× compute on Pair 1. Do the two levers stack
  (both relieve different bottlenecks) or substitute (same bottleneck)?
- **§v2.14d** — consume under Arm A on Pair 1. Does the safe-pop effect
  generalize beyond BP_TOPK?
- **§v2.14e** — consume on a second slot binding (MAP_EQ_E instead of
  MAP_EQ_R). Tests whether the effect is type-chain-driven or op-specific.

Recently completed:

- **§v2.11** *(DONE — PASS decoder-robust)* — Arm A reproduces 20/20 BOTH
  on §v2.3's 4-token pair. Decoder choice doesn't matter on short bodies.
- **§v2.12** *(DONE — FAIL decoder-general)* — Arm A traps in the same
  proxy basins as BP_TOPK (0/20 natural, 1/20 decorrelated).
- **§v2.13** *(DONE — INCONCLUSIVE)* — K=5 is saturated on 4-token body;
  reshuffles seeds on 6-token body without lifting the ceiling.
- **§v2.4-proxy-2** *(DONE — FAIL proxy cascade)* — dual-decorrelation
  confirms proxy cascade to third-tier predictors. Basin threshold
  relaxed to ≥~0.85.
- **§v2.4-proxy-3** *(DONE — INCONCLUSIVE)* — split-halves boundary probe
  collapsed due to search-space confound.
- **§v2.14** *(DONE — PASS)* — consume doubles 6-token BOTH (4→8/20);
  canonical assembly triples (3→9/20). Promoted to findings.md.
- **§v2.14b** *(DONE — PARTIAL)* — consume shifts attractor landscape on
  AND-composition (0→10/20 AND attempts) without escaping basin.

Standing open questions not yet probed:

- Does a redesigned §v2.6' with Fmin-intermediate thresholds recover an
  across-body constant-indirection claim?
- Can the G→P mapping itself be evolved (e.g., genotype-encoded header
  cells that choose which ops get bound to which slots)? Deferred pending
  v2-probe scope decisions. See
  [meta-learning-design-space.md](meta-learning-design-space.md) for the
  full design space (six approaches, recommended hybrids, meta-objectives,
  experiment sequencing).
- If §v2.14c shows consume + compute stack, should consume become the
  project default?

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
