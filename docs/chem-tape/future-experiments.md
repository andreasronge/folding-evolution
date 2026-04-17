# Future Experiments — Design Space

**Status:** Pre-experiment design notes. No pre-registrations yet.
Captures insights from Pigozzi et al. (2024) analysis, Codex adversarial
review (2026-04-16), and the §v2.14 safe-pop arc (§v2.14 / §v2.14b /
§v2.14c / §v2.14d / §v2.14e). Intended as input for future
pre-registrations under the methodology in `docs/methodology.md`.

**Relationship to existing docs:**
- `docs/theory.md` §Meta-Learned Developmental Systems — theoretical framing
- `docs/theory.md` §Related Work §1 — Srivastava-Louis-Martin, Sappington-Mohanty, Moreno et al. AutoMap, Evolvability ES
- `docs/chem-tape/architecture-v2.md` §Secondary direction — the narrow
  "header cells select slot bindings" probe (level 2, still valid as a
  minimal entry point)
- `docs/chem-tape/experiments-v2.md` §v2.14 arc — safe-pop consume chronicle
- `docs/chem-tape/findings.md` `proxy-basin-attractor`, `safe-pop-consume-effect`
- `docs/future-directions.md` Direction 4 — folding-track evolvable chemistry
  (DevGenome history, individual-level variation plan)
- `docs/folding/findings.md` §Evolvable Chemistry — DevGenome negative result

---

## Section map

The design space after §v2.14 falls into four themes:

| Part | Theme | Intent | Cost |
|---|---|---|---|
| **Part 1** | Meta-learning the developmental system | Attack the proxy basin at the representation level (evolve the decoder) | High (new machinery) |
| **Part 2** | Theory-driven diagnostics | Measure intrinsic landscape properties of the current decoder before replacing it | Low (analysis only) |
| **Part 3** | Gap-filling on the v2 / safe-pop arc | Close scoped open questions from the §v2.14 chronicle | Low–medium (single sweeps) |
| **Part 4** | High-stakes new arcs | Experiments that would reshape the paper's story if they land | Medium–high |

Parts 2 and 3 are cheap and should be run before committing to Part 1.
Part 4 is independent of the proxy-basin track and can run in parallel.

---

# Part 1 — Meta-learning the developmental system

## The core problem (reframed)

The original framing: "chem-tape's bonding rules are discrete and
combinatorial, blocking gradient-based meta-learning."

**Better framing (from Codex review):** The blocker is not discreteness
per se. It is that **evolvability credit assignment is delayed, noisy, and
dominated by proxy basins**. The proxy-basin-attractor is decoder-general
(§v2.12) and survives executor-rule changes (§v2.14b). Making chemistry
smooth is necessary but not sufficient — the meta-objective must directly
reward properties like:
- Resistance to cheap proxy attractors under sampler shifts
- Adaptation speed after task switches
- Body reuse across slot changes
- Phenotypic diversity of offspring

If the outer objective rewards only immediate fitness, the meta-learner
will optimize the wrong thing (the DevGenome story again).

## Six approaches

### Approach 1: Soft bonds, hard tokens

Replace binary bond/no-bond with continuous bond strength in [0, 1].

```
bond_strength(i, i+1) = σ(w_affinity[token[i], token[i+1]] + w_bias)
```

Learnable token-pair affinity matrix. Soft segmentation: cells contribute
to the program weighted by cumulative bond connectivity. Stack machine
still receives discrete tokens.

**Promise:** Cleanest relaxation. Keeps symbolic semantics intact.
Intermediate bond states provide gradient signal that binary bonding lacks
("this bond is almost useful, strengthen it").

**Risk:** Only smooths the edge of the decoder. May collapse to
near-uniform bonding or trivial masking — DevGenome in softer clothing.
Gradients learn "bond more/less," not developmental biases that improve
long-horizon adaptation.

**Verdict:** Useful as a baseline/control, not the main bet.

### Approach 2: Probabilistic token embeddings (Gumbel-softmax)

Each tape cell holds a probability distribution over the token alphabet.
Bonding from cosine similarity of adjacent embeddings. Temperature
controls exploration/exploitation. Discretize at execution.

**Promise:** Continuous latent genotype space. Neutrality becomes
continuous (a cell with flat distribution over {ADD, SUB, MUL} is
"neutral among arithmetic ops").

**Risk (severe):** A convex combination of ADD, GT, and DUP is not a
useful intermediate — it is semantic mush. RPN interpreters are symbolic;
partial tokens have no meaning. Smooths the wrong object unless the
executor is also relaxed.

**Verdict:** "Representation theater" (Codex). Do not pursue unless
paired with a differentiable executor.

### Approach 3: Morphogen-gradient chemistry

Replace single-pass bonding with a reaction-diffusion system on the tape.

```
∂c_i/∂t = D · (c_{i-1} - 2c_i + c_{i+1}) + f(token[i], meta_params) - decay · c_i
```

After N diffusion steps, local concentration determines active/neutral.
Meta-genome controls: production rates per token type, diffusion D, decay
rate, number of steps, activation threshold.

**Promise:** The only proposal that is a genuine developmental system
(not a softened parser). Introduces non-local effects (position 5
influences position 12 through concentration field), canalization, and
positional fields. Closest to the NCA literature.

**Risk:** Collapse to fixed positional templates ("activate middle 10
cells, suppress edges") that improve average fitness on one task family
without improving evolvability. Reaction-diffusion is parameter-sensitive.

**Verdict:** Strong if paired with the right outer objective. One of two
top approaches.

### Approach 4: Attention-based program assembly

Replace top-K extraction with learned attention over the tape.
Meta-genome parameterizes query/key matrices.

Radical version: multiple attention heads each extract a semantically
coherent fragment (input-processing, aggregation, comparison).

**Promise:** Directly attacks the crude top-K bottleneck. Can assemble
fragments globally.

**Risk:** Effectively abandons "chemistry" for a generic learned selector.
No longer a developmental system in any meaningful sense. Top-K attended
tokens can produce arity-invalid or semantically incoherent RPN programs.

**Verdict:** Stronger than Approach 1 for extraction, weaker than
Approach 3 for developmental meta-learning. Consider only if constrained
to read from morphogen-defined active regions (3+4 hybrid).

### Approach 5: Population-based meta-learning (ES/CMA-ES)

Bypass differentiability entirely. Outer loop: ES or CMA-ES over a
real-valued chemistry parameter vector. Inner loop: standard chem-tape GA
under those parameters. Meta-fitness: evolvability metrics (see below).

**Promise:** Most technically honest. Works with discrete symbolic
inner system. Zero changes to chem-tape inner loop. Task-alternation
infrastructure already exists and naturally generates an evolvability
signal.

**Risk:** Meta-fitness design is everything. Optimizing bond count,
entropy, or raw diversity will produce junk. Must optimize the right
things (see §Meta-objectives below). Also: outer-loop noise and
meta-overfitting to the benchmark suite.

**Verdict:** Best single bet. Highest probability of producing
interpretable results.

### Approach 6: Chemistry-as-stack-program (self-referential)

Split the tape: chemistry header + program body. The header is
interpreted as bonding/extraction rules in the same RPN language.
Same evolutionary operators act on both regions.

**Promise:** Elegant self-reference. Maximal expressivity. Developmental
system and solutions share genome and language. Closest to biological
gene regulation.

**Risk:** Search-space explosion — evolving a program that evolves a
program. Without strong bias, creates a meta-circular tarpit. Evolution
discovers degenerate headers that trivialize extraction.

**Mitigating design:** constrain the header language to a small set of
parameterized bonding predicates, not full RPN. This bounds expressivity
while preserving the self-referential property.

**Verdict:** Moonshot with high novelty. Worth keeping alive alongside
the mainline, not as the primary bet.

## Recommended research program

### Mainline: Approach 5 + 3 hybrid

Use a morphogen-style developmental substrate (Approach 3), but optimize
it with ES/CMA-ES (Approach 5) on outer-loop evolvability metrics.

**Why this pairing:** Approach 3 provides the developmental richness
(non-local effects, canalization, temporal dynamics). Approach 5 provides
the optimization method that matches the problem (black-box, handles
discrete inner loop, no fake gradients).

### Disciplined baseline: Approach 5 + 1

Same outer loop, but with simple soft bonds instead of morphogen
chemistry. If this fails, "softening local chemistry" is not enough.
If it succeeds comparably to 5+3, morphogen complexity is not needed.

### Diagnostic gate (run first)

Before either hybrid, run a **chemistry parameter grid sweep** on
existing tasks. Take §v2.3 (80/80 BOTH) and §v2.6 Pair 1 (4/20 BOTH).
Sweep over chemistry parameters (K, bond_protection, min_run_length) in
a grid. If there exists a parameterization that lifts Pair 1 from 4/20
to ~12/20 while keeping §v2.3 at ceiling — the chemistry search space
has useful structure and meta-learning is worth the machinery. If every
parameterization leaves Pair 1 at 4/20, the chemistry knobs don't have
enough leverage. (See also Part 3 §Systematic decoder-ablation grid —
same experiment, with broader framing as Kuyucu-style micro-ablation.)

## Meta-objectives (critical design choice)

The meta-fitness function determines whether meta-learning succeeds or
fails. The DevGenome failure was partly a meta-objective failure
(optimizing immediate fitness, not evolvability).

### Candidate meta-objectives

| objective | measures | pros | cons |
|---|---|---|---|
| Adaptation speed after task switch | Generations to recover fitness after alternation flip | Directly measures evolvability; infrastructure exists | Noisy; depends on task pair choice |
| Offspring fitness variance | Variance of fitness among mutated offspring | Rewards diverse variation | High variance ≠ useful variance |
| Body reuse rate | Fraction of seeds converging to a body-invariant route | Rewards the mechanism we want | Hard to measure automatically |
| Anti-proxy resistance | Fitness under sampler shift (decorrelated distribution) | Directly targets the proxy-basin trap | Requires per-task decorrelated sampler design |
| Pareto front volume | Volume in (fitness, diversity) space | Rewards both quality and variety | Expensive to compute |
| Cross-task transfer score | Fitness on task B of genomes evolved on task A | Rewards general solutions | Quadratic in number of tasks |
| MaxVar evolvability (Evolvability ES) | Trace of offspring behavior-characteristic covariance | First-class evolvability objective; theoretically grounded | Requires a chem-tape behavior vector (run count, op histogram, output range) |

### Recommended meta-objective for first experiment

**Adaptation speed after task switch** — measured as mean fitness
recovery within 50 generations after each alternation flip, averaged
across 5 task-switch events per run. This is:
- Cheap (falls out of existing alternation infrastructure)
- Directly interpretable (faster recovery = more evolvable)
- Anti-proxy by construction (chemistries that trap in one-task proxies
  will have slow recovery after the switch)

## Additional directions identified (not yet developed)

### Differentiable executor (soft stack machine)

If we want gradient-based meta-learning (not just ES), gradients stop at
the program boundary. A differentiable stack machine (Neural Turing
Machine style) would close the loop. High implementation cost but
theoretically correct for end-to-end meta-learning.

### Meta-learning operators, not only G→P map

Bond-protection is already a mutation-shaping lever. Co-evolving mutation
rate, crossover rate, and bond-protection per individual alongside
chemistry parameters extends the meta-learning surface. The question is
whether operator meta-learning has independent value or is dominated by
G→P map meta-learning.

### Library/macrogenesis

Given evidence for reusable bodies (body-invariant routes), meta-learning
reusable fragments or typed macros may be more aligned than meta-learning
adjacency chemistry. Instead of evolving how bonds form, evolve a library
of program fragments that can be composed.

### Bilevel differentiation through evolutionary dynamics

Parameterize mutation/selection/development, unroll a short inner
evolution, differentiate adaptation speed. Conceptually correct but
computationally expensive and implementation-heavy.

### MAP-Elites chemistry repertoire

Maintain a grid of chemistry parameterizations indexed by behavioral
descriptors (average bond count, program length distribution). Each cell
holds the best-performing chemistry for that niche. Produces a repertoire
of chemistries rather than a single optimum.

## Experiment sequencing (Part 1)

```
Phase 0: Diagnostic gate
  Chemistry parameter grid sweep on §v2.3 + §v2.6 Pair 1
  → Does the chemistry space have useful structure?
  → If no: stop, chemistry knobs lack leverage
  → If yes: proceed to Phase 1

Phase 1: Approach 5+1 (ES + soft bonds)
  Outer: CMA-ES over soft-bond affinity matrix + bond_protection + K
  Inner: standard chem-tape GA on task-alternation pairs
  Meta-fitness: adaptation speed after task switch
  Evaluate on: §v2.3 pair (easy), §v2.6 Pair 1 (hard), §v2.4 AND task (proxy-trapped)
  → Establishes whether meta-learned soft chemistry improves evolvability

Phase 2: Approach 5+3 (ES + morphogen chemistry)
  Same outer loop, richer developmental substrate
  → Tests whether developmental richness adds value beyond soft bonds

Phase 3 (optional moonshot): Approach 6 constrained
  Chemistry-as-stack-program with restricted header language
  → Tests self-referential developmental evolution
```

## Key assumptions to test (Part 1)

1. "The chemistry parameter space has useful structure" — tested by Phase 0
2. "Meta-learning evolvability is better than meta-learning fitness" — tested by comparing meta-objectives in Phase 1
3. "Morphogen dynamics add value beyond soft bonds" — tested by Phase 1 vs Phase 2
4. "The proxy basin can be escaped via meta-learned chemistry" — tested by evaluating on §v2.4 AND task in all phases

---

# Part 2 — Theory-driven diagnostics

Measure intrinsic landscape properties of the **current** decoder before
replacing it. These are cheap analyses (no new evolutionary runs
required, or one small sweep) whose results would either tighten the
proxy-basin claim to a predicted consequence of measured landscape
structure — or falsify the interpretation.

## 2a. Neutral-component enumeration (Srivastava-Louis-Martin)

**Question.** Does the proxy-basin region of §v2.4 correspond to a
measurably-low-evolvability neutral component in the chem-tape G-P map?

**Method.** Following Srivastava-Louis-Martin (theory.md §1): for small
tape lengths (ℓ ≤ ~12), enumerate tapes exhaustively, group genotypes
producing the same extracted program into neutral components (NCs),
compute per-NC evolvability (distinct phenotypes reachable via
single-token mutation from the NC boundary). Apply their Eq. 9 navigability
threshold (geometric mean of NC evolvabilities). Locate the max>5
proxy-predicate NC on the resulting NC graph.

**Outcomes:**
- max>5 NC has anomalously low evolvability relative to neighbours → the
  proxy basin is a predicted consequence of the G-P map's NC structure.
  Makes "proxy-basin-attractor" a theory-grounded claim rather than a
  descriptive one.
- max>5 NC has normal evolvability → the basin is a dynamical property
  of selection, not a static landscape property. This redirects Part 1.

**Cost.** One-time enumeration + graph analysis. Limitation:
Srivastava-Louis-Martin assumes random fitness; chem-tape tasks are
correlated. Predictions are expected-value bounds, not exact.

## 2b. Phenotype-frequency histogram (Sappington-Mohanty)

**Question.** Is the chem-tape phenotype frequency distribution
heavy-tailed or uniform, and do rare multi-chunk programs sit where the
Sappington-Mohanty framework predicts suppressed mutational robustness?

**Method.** Sample ~10⁴ random tapes at length 32, decode under
BP_TOPK(k=3, bp=0.5), tabulate distinct run-structure phenotypes f_n.
Plot f_n histogram. Compute genotype entropy S'_g per tape (spread of
phenotypes under single-site mutation). Plot ρ (mutational robustness)
vs S'_g.

**Outcomes:**
- Heavy-tailed f_n → rare multi-chunk programs (e.g., the canonical
  §v2.4 AND body) face suppressed mutational robustness — a
  representation-level explanation for the proxy-basin trap.
- Uniform or light-tailed f_n → the decoder is not producing the
  phenotypic bottleneck structure that the framework predicts; the
  proxy-basin is not a distributional phenomenon.

**Cost.** One random-tape sampling sweep + analysis. Adapts the theory
to insertion/deletion operators (limitation: framework assumes
single-character substitution over fixed alphabet).

## 2c. Motif enrichment on evolved populations (Altenberg)

**Question.** Do evolved chem-tape populations show n-gram enrichment
relative to random tapes, as predicted by Altenberg's
genome-as-population thesis (theory.md Type I effects)?

**Method.** Take §v2.3 evolved populations (80/80 BOTH across 4 seed
blocks). Compute token n-gram frequencies (n ∈ {2, 3, 4}) over evolved
populations vs matched-length random tapes. Test for enrichment of
n-grams that correspond to fragments of the canonical body.

**Outcomes:**
- Significant enrichment of canonical-body substrings → constructional
  selection is operating on chem-tape genotypes; supports extending
  Altenberg's genome-as-population model to this representation.
- No enrichment beyond what match-constraint alone predicts →
  chem-tape populations are not exhibiting motif-level constructional
  dynamics at this scope.

**Cost.** Re-analysis of existing §v2.3 sweep output. No new runs needed.

---

# Part 3 — Gap-filling on the v2 / safe-pop arc

Scoped experiments that close specific open questions flagged by the
§v2.14 chronicle itself. Each is a single sweep (≤ 1h wall) on existing
infrastructure.

## 3a. Non-MAP slot binding (completes §v2.14e type-chain claim)

**Question.** Is the safe-pop consume effect driven by the shared
type-chain structure (str→charlist→intlist→int), or is it specific to
MAP-family slot bindings?

**Design.** Replicate §v2.14e with a non-MAP op at slot 12 that produces
a different type chain (e.g., FILTER_EQ or a REDUCE variant). Compare
preserve vs consume solve rates.

**Why it matters.** §v2.14e itself flags this: replication across two
MAP-family bindings (MAP_EQ_R, MAP_EQ_E) is consistent with both
type-chain and MAP-family-specific readings. A non-MAP op cleanly
distinguishes them. Without this test the consume mechanism reading is
one slot-op-family wide.

**Cost.** ~20 min at 10-worker M1 (single sweep, n=20, matched compute).

## 3b. Consume × Arm A × 4× compute (fills §v2.14d off-grid gap)

**Question.** Is the Arm A consume null result (§v2.14d, 5/20 vs
preserve 7/20) rescued by 4× compute, mirroring the BP_TOPK stacking
seen in §v2.14c?

**Design.** Single sweep: Arm A, consume rule, pop=2048, gens=3000 on
the §v2.6 Pair 1 body. Compare against the preserve-Arm-A baseline at
matched compute.

**Why it matters.** §v2.14d landed off-grid between INCONCLUSIVE and
FAIL. §v2.14c showed consume × compute stack on BP_TOPK. If they also
stack on Arm A, the consume effect is decoder-arm-independent at
sufficient compute. If they don't, the decoder-arm-dependence claim in
findings.md §safe-pop-consume-effect tightens.

**Cost.** ~40 min at 10-worker M1.

## 3c. Systematic decoder-ablation grid (generalizes safe-pop)

**Question.** Safe-pop is one executor-rule micro-ablation inspired by
Kuyucu et al. (theory.md §6). Which other decoder knobs (top-K K,
bond_protection, min_run_length, run-malformed handling) behave
similarly?

**Design.** 3×3×3 grid over {K, bond_protection, min_run_length} on
§v2.3 (expect ceiling-sensitivity) and §v2.6 Pair 1 (expect
phenotype-mixing). n=20 per cell. Record ADI, BOTH solve rate, attractor
categories per cell.

**Why it matters.** Doubles as **Part 1 Phase 0 diagnostic gate** (see
§Experiment sequencing). If the grid has no cell that lifts Pair 1
measurably, the chemistry-knob search space lacks leverage and the Part 1
program should not commit to full ES machinery. If it does, the lift
locates a promising meta-learning direction.

**Cost.** ~2–3h overnight sweep. Fits one queue slot.

## 3d. Seeded-initialization probe on §v2.4 AND

**Question.** Is the §v2.4 AND task un-solved because the canonical
body is (a) undiscoverable, (b) discoverable but not maintainable, or
(c) discoverable-and-maintainable but the training gradient doesn't
point toward it from realistic starts?

**Design.** Inject 1–5 hand-crafted tapes containing the canonical
12-token AND body into the initial population (seed 0 fraction); run
standard chem-tape GA at pre-reg compute. Measure whether the injected
solvers are retained, improved, or shed in favor of the max>5 proxy.

**Why it matters.** §v2.4-proxy-3 already queued this in its next
steps. Cleanly separates discoverability from maintainability — the
missing half of the proxy-basin diagnostic. Directly informs whether
Part 1's ES machinery needs to attack discoverability, maintainability,
or both.

**Cost.** ~20 min at 10-worker M1.

---

# Part 4 — High-stakes new arcs

Experiments that would reshape the paper's story if they land. Higher
implementation cost than Parts 2–3, independent of the proxy-basin
track.

## 4a. Regime-shift benchmark on chem-tape

**Question.** Does chem-tape's body-invariant route mechanism track a
shifting target (AND ↔ OR every N generations) better than Arm A direct
GP, as Altenberg's framework (theory.md §The Central Prediction)
predicts?

**Design.** Alternate F_AND and F_OR (or §v2.3's `sum_gt_5_slot` /
`sum_gt_10_slot`) every 10 generations for 200 generations. Measure mean
fitness-over-time and recovery speed for chem-tape (BP_TOPK, then Arm A)
vs a matched DEAP tree-GP baseline.

**Why it matters.** This is the single experiment from theory.md's
central prediction table that has **never been run on chem-tape**. The
v2 suite was entirely fixed-task or narrow alternation within pair-type.
A clean "folding/chem-tape adapts, Arm A can't" result on the regime
shift would generalize the folding-track headline to the chem-tape
representation. A null result would narrow the paper claim sharply.

**Cost.** ~1h sweep; infrastructure exists.

## 4b. Denoising autoencoder decoder (AutoMap; Moreno et al.)

**Question.** Can a learned decoder (trained on §v2.3 / §v2.6 champions)
escape proxy basins that BP_TOPK cannot?

**Design.** Following AutoMap (theory.md §Meta-Learned Developmental
Systems): train a denoising autoencoder on champion tape phenotypes
harvested from existing sweeps, inject character-substitution +
insertion/deletion noise during training. Substitute the trained decoder
in for BP_TOPK on §v2.3, §v2.6 Pair 1, and §v2.4 AND. Measure BOTH-solve
rates, attractor categories, and single-mutation repair behaviour.

**Why it matters.** Safe-pop (§v2.14) demonstrated the decoder is a real
lever — a learned decoder is the natural next-generation test. If it
lifts §v2.4 AND (where compute, consume, and Arm A all fail), it
validates the meta-learning direction without committing to full Part 1
ES machinery first. If it doesn't, it narrows Part 1 toward approaches
that change chemistry dynamics (3, 6) rather than extraction (4).

**Cost.** Higher — requires training infrastructure. Limitation: the
trained decoder is task-family-specific; regime-shift evaluation requires
retraining or online adaptation.

## 4c. MaxVar evolvability measurement on current configurations

**Question.** Is the §v2.4 proxy-basin region measurably lower in
MaxVar evolvability (Evolvability ES; theory.md §1) than configurations
that escape it?

**Design.** Define a chem-tape behavior-characteristic vector (run count,
operator-frequency histogram, token-diversity, program-output range).
For each of §v2.3-solving, §v2.6-Pair-1-solving, and §v2.4-trapped
configurations, sample ~10³ mutated offspring, compute covariance trace
and distribution entropy.

**Why it matters.** Makes the proxy-basin-attractor a quantitatively
measurable property rather than a descriptive one. Directly predicts
which configurations Part 1 Phase 1 should favour as starting points.

**Cost.** One batch-eval pass per configuration (no evolution). Medium
implementation cost for the behavior vector definition, trivial compute.

---

*Created 2026-04-16. Sources: Pigozzi et al. (2024) analysis, Codex
adversarial review, chem-tape experimental record through §v2.14e.
Reorganized 2026-04-16 into four thematic parts post-§v2.14 safe-pop
arc: meta-learning design space (Part 1), theory-driven diagnostics
(Part 2), v2-arc gap-filling (Part 3), high-stakes new arcs (Part 4).*
