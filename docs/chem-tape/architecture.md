# Architecture: Chemistry-Tape GP — v1

A third research track alongside folding (`docs/architecture.md`) and CA-development (`docs/ca/architecture.md`). Folding taught us that scaffold preservation under drift makes evolution reach rare compositional structures. CA taught us that batched local updates on a grid run orders of magnitude faster on M1. Chemistry-tape unifies both on a single 1D data structure: a token tape with per-cell bond bits, decoded as a postfix (RPN) stack program.

This document specifies **v1** — the minimum-viable design that answers one question at the lowest possible complexity. v2–v4 are sketched in the research ladder below and will be specified when each becomes next-to-implement.

Source: `src/folding_evolution/chem_tape/` (to be created). Drivers: `experiments/chem_tape/`.

## Motivation

Two constraints drive the design:

1. **M1 speed.** The folding pipeline's graph rewriting is irregular and the current bottleneck in sweep-scale experiments. 1D stencil kernels on MLX run the same population far faster. Speed gates how many sweeps are affordable in the remaining research budget.
2. **Reduce-with-lambda evolvability.** In Lisp-tree GP this structure is nearly unreachable because four pieces (list, init, lambda body, reduce operator) must appear in one adjacency. Folding-Lisp partially solved this via scaffold preservation under neutral drift; plain CA-GP does not have that property (every cell is rewritten every step).

Chemistry-tape's bet: a separator-based decode with a neutral reserve is the simplest mechanism that could produce scaffold-like evolutionary dynamics on a 1D tape, while remaining cheap enough to batch like the CA engine.

## Research ladder

Four stages, each gated on its predecessor. Only v1 is fully specified in this document.

- **v1 — Substrate gate (this doc).** *Does persistent local bonding around a fixed tape outperform direct stack-GP on tasks where scaffold completion matters?* Two arms: direct stack-GP vs. chemistry-tape with a fixed trivial bond rule. The predicted positive signal is *differential*, not uniform — Arm B is expected to lose on short-scaffold benchmarks and win on long-scaffold ones (see Layer 9 and the methodological note below). If B ≤ A on sum-gt-10 (the long-scaffold test), the entire direction is falsified cheaply.
- **v1.5 — Regime-shift test (optional, gated on v1).** *Does chem-tape show temporal-regime-shift advantages analogous to folding's?* Same three benchmarks as v1, but the active task alternates every `N` generations within a single run (e.g., count-R → has-upper → sum-gt-10 → repeat). Tests whether Arm B's neutral reserve enables cross-task adaptation the way folding's pleiotropy enabled regime recovery (`docs/findings.md` §4–§5). Cheap — one extra sweep if v1 passes. Answers whether chem-tape inherits folding's dynamic advantage on a different axis or produces its own independent structural-scaffold advantage.
- **v2 — Expressivity parity.** *Can chem-tape, extended to match folding-Lisp's problem domain, compete with folding-Lisp on its own benchmarks?* Adds quotation tokens (LAMBDA_OPEN/LAMBDA_CLOSE or Joy-style `[` `]`), structured-record inputs, field-access tokens, control-flow tokens. Alphabet grows to ~30. Enables direct comparison against folding-Lisp on filter/map/reduce queries over records.
- **v3 — Chemistry ablation.** *How much of folding's evolvability comes from the clever multi-pass chemistry, and which mechanism within it?* At matched alphabet (v2's), introduce folding-style chemistry mechanisms one at a time: single-pass → multi-pass staged bonding → + bond priority (assembled > literal > data) → + irreversibility (consumed can't rebond). Five-arm ablation that produces a publishable-grade attribution claim.
- **v4 — Topology ablation.** *Does 2D adjacency contribute beyond chemistry mechanism?* 1D vs. 2D chem-tape at matched chemistry. Separates the dimensionality contribution from the chemistry-mechanism contribution that v3 establishes.

**Methodological note — the conditional-benefit pattern (analog to folding's regime-shift result).** Folding's key finding (`docs/findings.md` §4–§5) was not a uniform improvement over direct encoding but a *conditional* one: folding looked comparable or worse on static metrics, and only outperformed when the fitness regime shifted. The original hypothesis ("folding increases neutrality") turned out to be the wrong vocabulary; the reframed finding was about pleiotropy enabling structural reorganization under pressure. Chem-tape's v1 hypothesis has the same shape — Arm B is predicted to *lose* on short-scaffold tasks (count-R, has-upper) and *win* on long-scaffold tasks (sum-gt-10). A differential outcome is the expected positive signal under the hypothesis, not a contradiction. Gate criteria and result interpretation below are designed for this expectation, and the mechanism language ("scaffold preservation") is deliberately loose enough that v1 data can rename the mechanism if it needs to.

v1 is deliberately the cheapest possible gate. It does **not** by itself test chemistry mechanism, higher-order evolvability, or folding-comparable expressivity — those are v2+ questions that earn their runs only if v1 passes.

## Overview (v1)

```
Genotype (initial tape: 32 bytes — only field under selection in v1)
    |
    v
Fixed chemistry: bond[i] = is_active(tape[i]) AND is_active(tape[i+1])
    |
    v  (one-pass; no temporal dynamics in v1)
Phenotype: longest contiguous bonded run on the tape
    |
    v
Stack machine (RPN): execute bonded run on input
    |
    v
Output → compare to labels → fitness
```

Every layer batches over `(population × examples)` as a flat first dimension. The existing CA engine's batching pattern applies unchanged.

## Layer 1: The tape

A length-`L` array of cells. Each cell is one byte:

| bits  | field         |
|-------|---------------|
| 0-3   | token (0..15) |
| 4     | bond_left     |
| 5     | bond_right    |
| 6-7   | reserved      |

Default `L = 32`. In v1 the bond bits on the input tape are always zero — bonds are computed, not stored as part of the genotype. (The byte layout reserves them anyway because v2+ chemistry will write bonds as state.)

## Layer 2: Token alphabet (14 tokens)

Each task defines its own 14-token alphabet, split into **12 task-invariant shared tokens** (ids 0–11) and **2 task-specific slots** (ids 12–13). The shared core is what makes cross-task comparisons clean; the task-specific slots let each task access operations relevant to its problem shape.

**Shared tokens (ids 0–11) — identical across all tasks:**

| id | token       | input types      | output type |
|----|-------------|------------------|-------------|
| 0  | NOP         | —                | —           |
| 1  | INPUT       | —                | task-declared (str, intlist, …) |
| 2  | CONST_0     | —                | int         |
| 3  | CONST_1     | —                | int         |
| 4  | CHARS       | str              | charlist    |
| 5  | SUM         | intlist          | int         |
| 6  | ANY         | intlist          | int (0/1)   |
| 7  | ADD         | int, int         | int         |
| 8  | GT          | int, int         | int (0/1)   |
| 9  | DUP         | a                | a, a        |
| 10 | SWAP        | a, b             | b, a        |
| 11 | REDUCE_ADD  | intlist          | int (fixed combinator) |

**Task-specific slots (ids 12–13) — per-task, declared in each benchmark's config (see Layer 10):**

| task        | id 12         | id 13 |
|-------------|---------------|-------|
| count-R     | MAP_EQ_R      | NOP   |
| has-upper   | MAP_IS_UPPER  | NOP   |
| sum-gt-10   | NOP           | NOP   |

- `MAP_EQ_R`: `charlist → intlist` — maps each char to 1 if `== 'R'`, else 0.
- `MAP_IS_UPPER`: `charlist → intlist` — maps each char to 1 if uppercase, else 0.

Unused task-specific slots (`NOP`) mean some tasks have an effective alphabet smaller than 14. This is deliberate — the extra NOPs become additional neutral reserve. Sum-gt-10 uses only the shared core, which is the point (see Layer 10).

**Ids 14–15** are unused in v1 and **execute as NOP** (see Layer 7). Kept reserved for v2 quotation tokens (LAMBDA_OPEN / LAMBDA_CLOSE) so the 4-bit encoding stays stable when v2 arrives.

`REDUCE_ADD` is a fixed combinator, not a higher-order operator — it sums a list directly. User-provided step functions require quotation tokens and are a v2 feature.

## Layer 3: Execution safety — non-negotiable

Every combination of tokens must produce *some* output. No exceptions, no crashes, no runtime errors. This is the stack-GP analog of folding's "every genotype produces some program" property, and it is load-bearing for evolvability. Without it, the fitness landscape is full of cliffs.

Semantics (not validation errors — semantics):

- Pop from empty stack → yield the default value for the op's expected input type (see runtime type system below).
- Wrong-type operand → coerce to the same type-matched default.
- Hard cap: 256 stack operations per program. Truncate beyond; final stack top is the output.
- End of execution: if stack is empty, output is `0`. Otherwise, top of stack is the output.

### Runtime type system

Four tagged value types:

| type     | default | notes                                                |
|----------|---------|------------------------------------------------------|
| int      | `0`     | bools are ints; `0` is false, non-zero is true       |
| intlist  | `[]`    | used for counts, boolean vectors, list reductions    |
| str      | `""`    | input-only in v1; no str-constructing ops            |
| charlist | `[]`    | produced by `CHARS`; consumed by map-ops             |

**No separate `bool` type.** `ANY`, `GT`, and `MAP_EQ_R` all produce ints in `{0, 1}`. `SUM` of an intlist of 0/1 values is a count — this is the v1 idiom for counting.

**Per-op dispatch on pop.** Each op declares an input signature. When popping, if the stack is empty or the top-of-stack has the wrong type, the op substitutes the declared type's default before consuming. Example: `ADD` expects `(int, int)`; an empty stack supplies `(0, 0)` and `ADD` produces `0`. `SUM` expects `(intlist)`; wrong type supplies `[]` and `SUM` produces `0`. Codified once in `executor.py` and dispatched from each op's declared signature — no op contains its own empty-stack logic.

## Layer 4: Chemistry (fixed, trivial in v1)

The v1 chemistry rule is deliberately the simplest non-trivial rule. Define:

> **A cell is *active* iff its token executes a non-NOP operation — `token ∈ {1..13}`. Ids 0, 14, and 15 all execute as NOP in v1 and are inactive.**
>
> **Bond exists between cells `i` and `i+1` iff both cells are active.**

Computed in one pass from the tape. No temporal dynamics. No T-step CA. The rule takes the tape as input and emits a bond graph.

This is intentional. v1 is the **substrate gate** — it tests whether the *consequence* of persistent bonding (a neutral reserve plus a bonded "active" region) helps evolution at all. If it does, v2 and v3 earn the right to introduce richer dynamics (typed bonding, multi-pass staging, evolved rules). If it does not, no amount of cleverer chemistry will help either.

**What this trivializes on purpose.** The v1 rule makes inactive cells the *only* source of separators — every active adjacency bonds. A v3 rule could make bonding *type-compatible* (e.g., INPUT bonds to CHARS, CHARS bonds to MAP_*, etc.), or allow bonds to form and break across T steps. Those are planned later ablations, not v1 concerns.

**What this preserves honestly.** Scaffold preservation in v1 is "a contiguous active region survives small mutations as long as no mutation turns an interior cell inactive." Neutral reserve is "inactive cells plus any active region shorter than the longest are selection-invisible." Both properties are weaker than folding's, but they are present and measurable.

### Layer 4.1: Permeable bond rule (v1.1 refinement)

The v1-strict rule above bundled two distinct semantics into a single "inactive cell" class: (a) *no-op in execution* (the cell does nothing when run) and (b) *hard boundary in the decode* (the cell terminates a bonded run; execution cannot cross it). The v1 MVP evidence (see [experiments.md](experiments.md) §2) localised the sum-gt-10 failure to (b), not (a): Arm A's successful runs routinely used NOP cells as interior padding within the scaffold, which Arm B's strict separator rule prunes.

The **permeable rule** splits the two semantics:

> **Separator cells are `token ∈ {14, 15}`** (the reserved-for-v2 quotation slots, which execute as NOP in v1 but serve as *hard* separators for decode purposes).
> **Bond-transparent cells are `token ∈ {0..13}`** — including `NOP` (id 0), which remains a no-op at execution time but is *transparent* to bonding: a bonded run can span across NOPs as if they weren't there.
> **Bond exists between cells `i` and `i+1` iff both cells are bond-transparent.**

Concretely, the bond predicate changes from `is_active[i] & is_active[i+1]` (v1-strict, `is_active := token ∈ {1..13}`) to `is_non_separator[i] & is_non_separator[i+1]` (permeable, `is_non_separator := token ∈ {0..13}`). NOP execution semantics are unchanged — the cell still does nothing on the stack — only its role in the decode changes.

**Expected distributional effect under uniform init.** v1-strict expects ~6 inactive cells per 32-cell tape (ids 0, 14, 15 at 3/16) and a longest-runnable-segment of ~8 cells. The permeable rule drops this to ~4 separators (ids 14, 15 at 2/16) and widens the expected longest-runnable segment to ~14 cells — *right at the sum-gt-10 canonical scaffold length* (Layer 10). This is the hypothesis: scaffold completion was budget-limited by the separator density the v1-strict rule enforced, not by the bonded-run decode per se.

**Implementation.** One token-class split (separator vs. non-separator, replacing active vs. inactive) plus a parameterised mask function in the engine. See `src/folding_evolution/chem_tape/alphabet.py` and `engine_numpy.py`. Layer 6's `is_active` expression generalises to a selectable mask predicate; the longest-run algorithm is otherwise unchanged.

**Status.** The permeable rule is the **current default** for chem-tape experiments from [experiments.md](experiments.md) §3 onward. The v1-strict rule remains documented above because (a) it is the gate design the v1 MVP acceptance criterion (Layer 11) was written against and (b) the v1-strict-vs-permeable head-to-head is itself an ablation — see Arm B vs Arm BP in Layer 9.

## Layer 5: Phenotype decode

Walk the tape left to right. Identify all maximal contiguous runs of active cells. Execute the **longest** active run as an RPN stack program. All other cells — shorter runs and inactive cells — are ignored; they form the neutral reserve.

Worked example with tape tokens (inactive cells marked `_`):

```
idx:   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
token: 1  4 12  5  _  _  1  4 12  6 10  _  2  7  _  _
                                   ANY
```

Interpreting the `_` cells as inactive, active runs are:

- cells 0–3 = `[INPUT, CHARS, MAP_EQ_R, SUM]` (length 4) — count-R task alphabet.
- cells 6–10 = `[INPUT, CHARS, MAP_EQ_R, ANY, GT]` (length 5) ← longest
- cells 12–13 = `[CONST_0, ADD]` (length 2)

Executed program: cells 6–10. Everything else is neutral reserve.

**Ties:** if two active runs are the same length, pick the leftmost. Deterministic by construction.

**Empty case:** all-inactive tape or all-length-zero runs → empty program → stack ends empty → output `0`.

This "longest run" rule is the v1 simplification of the original spec's concatenated-runs decode. Concatenation produced semantic adjacency between fragments that were never chemically connected; longest-run keeps motif boundaries sharp at the cost of dropping secondary bonded regions.

## Layer 6: Evaluation batching

Same pattern as the CA module. For population `P` and `E` task examples:

- Tapes: broadcast to `(P·E, L)` bytes.
- Bond computation: one stencil op — compute `is_active[b, i] = (token[b, i] >= 1) & (token[b, i] <= 13)` in parallel.
- Longest-run finding: algorithm below.
- Stack execution: per-example Python/NumPy loop for v1. At `P=256, E=64` that's 16K evaluations per generation, each ≤32 tokens × ≤256 op cap — acceptable unless profiling shows otherwise.

### Longest-run algorithm (vectorized, batched)

For batched tape `(B, L)` of uint8 tokens:

```
1. is_active    = (token >= 1) & (token <= 13)               # (B, L) bool
2. run_start    = is_active & ~shift_right_pad0(is_active)   # (B, L); 1 at first cell of each active run
3. run_id       = cumsum(run_start, axis=1) * is_active       # (B, L); 0 for inactive, else 1-indexed
4. lengths      = scatter_add_per_row(run_id, ones)           # (B, L+1); lengths[b, k] = cells with run_id=k
5. best_run     = argmax(lengths[:, 1:], axis=1) + 1          # (B,); skip run_id=0 (inactive); ties → leftmost
6. active_mask  = (run_id == best_run[:, None]) & is_active   # (B, L)
7. gather token[b] where active_mask[b] is true, preserving tape order → program per batch row
```

`shift_right_pad0` shifts the axis right by one with zero padding. `scatter_add_per_row` is implementable in MLX via `mx.zeros((B, L+1)).at[batch_idx, run_id].add(1)`; the NumPy reference uses `np.apply_along_axis(np.bincount, 1, run_id, minlength=L+1)`.

**Batched stack execution** (fixed-size stack tensor with masks) is deferred to v2 or later, only if execution becomes the bottleneck. In v1 the expected hot path is bond computation + longest-run, both of which are MLX-native.

## Layer 7: Genotype and operators (v1)

One evolved array: the **initial tape** (`L = 32` bytes). No evolved rule table in v1 — the bond rule (Layer 4) is fixed. A rule table becomes an evolved genotype component in v3 (chemistry ablation).

### Genotype distribution (initialization and mutation)

**Per cell, sample uniformly from `{0..15}`** for both initialization and mutation. Ids 14 and 15 execute as NOP in v1, giving three NOP alleles (0, 14, 15). Effective NOP frequency per cell ≈ 3/16 ≈ 19%, or ~6 inactive cells per 32-cell tape at gen-0 — enough for a meaningful neutral reserve and multiple bonded segments from the start, without any ad-hoc init bias.

Three NOP alleles is a feature, not a bug: extra neutrality, no special code path. When v2 arrives, ids 14 and 15 take on their quotation-token meanings without changing the init/mutation distribution.

### Operators

- **Point mutation:** per-byte, rate `mutation_rate` (default **0.03**). Replaces the byte with a fresh uniform sample from `{0..15}` (so a mutation to the same value is possible but rare — 1/16).
- **Crossover:** single-point splice on the tape, rate `crossover_rate` (default **0.7**). When crossover does not fire, one parent copies through. Children are always mutated.

Both rates are sweep axes.

## Layer 8: Evolution loop

Identical to CA-GP. Tournament selection (size 3), elitism (count 2), no niching, no island model, no adaptive rates. The *representation* is the experimental variable; GA machinery stays fixed so the comparison is clean.

## Layer 9: The research arms

A v1 result means nothing without a comparison. The arms share the same GA, token alphabet (per task), and stack semantics; they differ only in which of Layers 4 and 5 apply and which bond rule is used:

1. **Arm A — Direct stack-GP (null hypothesis).** The tape is executed directly as an RPN program. All 32 tokens participate in execution in tape order; NOPs (and ids 14–15) are no-ops but do not act as separators. This is the stack-GP baseline with no developmental layer.
2. **Arm B — Chemistry-tape v1-strict (original design).** v1-strict bond rule (Layer 4): NOPs act as separators; only the longest active run executes. This introduces the neutral reserve and separator-based decode.
3. **Arm BP — Chemistry-tape v1.1 permeable (current default).** Permeable bond rule (Layer 4.1): only ids 14–15 are separators; NOPs are bond-transparent. Otherwise identical to Arm B — same longest-run decode, same stack machine.

**Arm A = Arm B minus Layers 4 and 5.** Both arms use identical: token alphabet, runtime type system, stack safety (256-op cap, pop-empty defaults), mutation rate, crossover rate, population size, generation budget, initialization distribution, tournament/elitism, and example sampling. The *only* differences are:

- Arm A skips Layer 4 (no bond graph computed).
- Arm A skips Layer 5 (executes the whole tape in order, not the longest run).

**Arm BP = Arm B with the Layer 4.1 permeable predicate substituted for the Layer 4 v1-strict predicate.** Same decode (Layer 5), same executor (Layer 3), same genotype and operators (Layer 7). The B-vs-BP comparison directly isolates the separator semantics — bundled-inactive (B) vs. separator-only (BP) — as an ablation axis.

Everything else is bitwise the same code path. This is the equivalence the comparison hinges on.

**Outcomes that discriminate cleanly (differential pattern across tasks, not per-task in isolation):**

Chem-tape's mechanism is predicted to be task-dependent. On short-scaffold tasks (count-R, has-upper, ~4-cell optimum), Arm B's longest-run decode can drop cells that Arm A uses freely — the mechanism is a net cost. On long-scaffold tasks (sum-gt-10, ~14-cell optimum), the neutral reserve protects partial scaffolds from disruption elsewhere on the tape — the mechanism is a net gain. The expected positive signal is therefore *differential*, not uniform:

| count-R (short) | has-upper (short) | sum-gt-10 (long) | interpretation |
|-----------------|-------------------|------------------|----------------|
| B < A | B < A | B > A | **Predicted pattern — hypothesis confirmed, mechanism localized to scaffold-completion pressure** |
| B ≈ A | B ≈ A | B > A | Also hypothesis-confirming (weaker differential) |
| B > A | B > A | B > A | Uniform benefit — something beyond scaffold-preservation is active; reframe the mechanism |
| B ≤ A | B ≤ A | B ≤ A | Design worse everywhere. Falsifies. |
| B > A | B < A | B < A | Incoherent; suggests confound or noise — rerun with more seeds |

**Acceptance criterion:** Arm B > Arm A on sum-gt-10 (the load-bearing benchmark). Outcomes on count-R and has-upper characterize the mechanism but do not gate it. **Rejection** requires Arm B ≤ Arm A on *all three* benchmarks, or Arm B < Arm A on sum-gt-10 specifically.

A typed-chemistry arm (bonds only form between type-compatible tokens) is deliberately deferred to v3, where it becomes the "Arm 2 — multi-pass staged bonding" of the chemistry ablation. Bundling it into v1 would conflate two questions.

## Layer 10: Benchmark definitions

Each task is fully specified by: INPUT type, task-specific slot assignments (ids 12–13), input-space size, sampling strategy, and label function.

### count-R

Count the occurrences of `'R'` in a string.

- **INPUT type:** `str`
- **Slots:** id 12 = `MAP_EQ_R`, id 13 = `NOP`
- **Input generator:** strings of length 16 over alphabet `[A-Za-z ]` (53 chars). Input space ≈ 53^16 (sampled).
- **Sampling:** `E = 64` examples per evaluation, drawn with a fixed per-seed sub-seed (same across generations within a seed, different across seeds). Balanced: half with `R`-count ≥ 1, half with `R`-count = 0.
- **Label:** integer count of `'R'` characters.
- **Natural scaffold:** `INPUT CHARS MAP_EQ_R SUM` (4 cells).

### has-upper

Does a string contain any uppercase character?

- **INPUT type:** `str`
- **Slots:** id 12 = `MAP_IS_UPPER`, id 13 = `NOP`
- **Input generator:** strings of length 16 over `[A-Za-z ]`. Sampled.
- **Sampling:** `E = 64`, fixed per-seed. Balanced: half contain at least one uppercase, half contain none.
- **Label:** `1` if any uppercase present, else `0`.
- **Natural scaffold:** `INPUT CHARS MAP_IS_UPPER ANY` (4 cells).

### sum-gt-10

Is the sum of an integer list greater than 10?

- **INPUT type:** `intlist`
- **Slots:** id 12 = `NOP`, id 13 = `NOP`. No task-specific ops — sum-gt-10 uses only the shared core.
- **Input generator:** lists of length 4, values in `[0, 9]`. Input space = 10^4 = 10000 (sampled).
- **Sampling:** `E = 64`, fixed per-seed. Balanced: half with sum > 10, half with sum ≤ 10.
- **Label:** `1` if sum > 10, else `0`.
- **Natural scaffold:** `INPUT SUM <construct 10> GT` (~12+ cells). The literal 10 must be built from `CONST_0`, `CONST_1`, `ADD`, and `DUP`. A minimal construction is `C1 DUP ADD DUP ADD DUP ADD C1 ADD` (→ 1, 2, 4, 8, 9) plus one more `C1 ADD` (→ 10) = 11 cells for the literal plus 3 cells for the rest = 14 cells. This long scaffold is deliberate — a `CONST_10` shortcut would remove exactly the scaffold-completion pressure sum-gt-10 is designed to exert.

### Generalization evaluation (for tasks with large input space)

Any task whose input space exceeds `E` also logs a **held-out generalization fitness** on a separate 256-example sample (fixed per-seed, disjoint from the training sample). This guards against the overfitting-as-fitness artifact that caught out 8-bit parity in the CA module (§9). Count-R and has-upper both require this; sum-gt-10 is borderline and also runs it.

## Layer 11: MVP sweep

`sweeps/mvp.yaml` — `task ∈ {count-R, has-upper, sum-gt-10}` × `arm ∈ {A, B}` × 10 seeds, fixed `L=32, pop=256, gens=200, E=64, mutation_rate=0.03, crossover_rate=0.7`. ~1.5 hours total on M1 — cheap enough that there is no reason to stage benchmarks behind a single-task gate.

**Acceptance criterion (from Layer 9):** Arm B > Arm A on sum-gt-10 (the load-bearing benchmark). Outcomes on count-R and has-upper characterize the mechanism (differential, uniform, or null) but do not gate the design. Rejection requires Arm B ≤ Arm A on *all three* benchmarks, or Arm B < Arm A on sum-gt-10 specifically.

**Why no single-benchmark gate.** An earlier draft gated on count-R. That is the wrong test: count-R is the benchmark where chem-tape is most likely to lose regardless of whether the underlying mechanism works, because its ~4-cell natural scaffold makes Arm B's longest-run decode a cost without a matching benefit. Gating on count-R would reject exactly the differential outcome pattern that most strongly supports the hypothesis (see the methodological note in the research ladder, above). Running all three from the start and judging on the differential is the sound version.

**Diagnostics to log** (beyond best/mean/std fitness):

- Longest active run length at gen-0 and final (mean and distribution across population).
- Per-generation best-tape with active-run boundaries marked — for visual inspection of scaffold-building dynamics.
- Held-out generalization fitness alongside training fitness (Layer 10) — guards against the overfitting artifact that caught out 8-bit parity in the CA module (`docs/ca/experiments.md` §9).

If Arm B loses on count-R (expected under the hypothesis), these diagnostics are what tell us *why*: is Arm B's longest-run dropping useful cells, or is the active-cell fraction at gen-0 too sparse for short scaffolds? The former is intrinsic; the latter suggests tuning the genotype distribution per task.

## Layer 12: Backend, engine, and driver

Two interchangeable kernels, mirroring the CA module:

| Backend | File                 | When to use                              |
|---------|----------------------|------------------------------------------|
| NumPy   | `engine_numpy.py`    | Reference / correctness baseline / CI    |
| MLX     | `engine_mlx.py`      | M1 Metal acceleration for sweeps         |

Both produce bitwise-identical results on fixed seeds (verified by `tests/test_chem_tape_engine_parity.py`). The stack executor lives in `executor.py` and is backend-agnostic (pure NumPy for v1).

A `ChemTapeConfig` dataclass, SHA-1 hashed, names the output directory. Sweeps are YAML files, resumable via `result.json` presence. Output layout per run:

```
output/<sweep>/<hash>/
    config.yaml
    result.json        # best_fitness, best_genotype_hex, elapsed_sec, holdout_fitness
    history.csv        # per-generation stats
    history.npz        # per-generation stats (fast reload)
    best_tape.txt      # final tape with bonds marked (for inspection)
```

## Expressivity vs folding-Lisp (v1 scope, explicit)

v1 chemistry-tape is **significantly less expressive** than folding-Lisp by design. The v1 alphabet was scoped to the string benchmark ladder, not to match folding-Lisp's structured-record query domain. The table below makes the gap explicit so the comparison is honest:

| Capability                | Folding-Lisp                             | Chem-tape v1 |
|---------------------------|------------------------------------------|--------------|
| Higher-order functions    | `fn`, used by filter/map/reduce/group-by | **missing**  |
| Typed structured records  | `data/products`, `data/employees`, …     | **missing**  |
| Field access              | `get`, `:price`, `:name`, …              | **missing**  |
| Conditionals              | `if`, `match`                            | **missing**  |
| Local bindings            | `let`                                    | **missing**  |
| Set operations            | `set`, `contains?`                       | **missing**  |
| General reduce            | `reduce` with user `fn`                  | only `REDUCE_ADD` (fixed combinator) |
| Boolean algebra           | `and`, `or`, `not`                       | only via `GT` (implicit) |
| Numeric literals          | 10 constants (0, 100, …, 900)            | 2 (CONST_0, CONST_1) |

A canonical folding-Lisp benchmark — `(filter (fn [x] (> (get x :price) 500)) data/products)` — has **no expressible form in v1 chem-tape**. Closing this gap is the v2 research question; matching folding-Lisp's evolvability on its own benchmarks is the v2 gate.

RPN as a substrate is Turing-equivalent to Lisp — Forth, Joy, and Factor demonstrate that higher-order functional programming composes fine on stacks. The gap above is alphabet scope, not stack-vs-tree. Closing it in v2 requires quotation tokens (LAMBDA_OPEN/LAMBDA_CLOSE), typed data-source tokens, field-access tokens, and ~16 more alphabet slots (up from v1's 14). Rule-table dimensions stay manageable because 4 → 5 bits/token keeps the v3 rule table under 33K entries.

## Scope boundary — what v1 does NOT include

- **Evolved chemistry (rule table).** Fixed bond rule in v1. Evolved rule is v3.
- **Temporal dynamics (T-step CA).** One-pass chemistry in v1. Multi-step developmental dynamics are deferred to v3 or later if fixed-rule chemistry shows promise.
- **Higher-order functions / quotations.** No LAMBDA_OPEN or LAMBDA_CLOSE. v2.
- **Structured data / field access / control flow.** v2.
- **2D substrate.** 1D throughout v1. 2D is v4.
- **Neural cellular automata (learned rules).** Never in this module's scope; a separate direction.
- **Typed DAG phenotype.** RPN is sufficient for the benchmark ladder and far simpler to execute in batch. A DAG phenotype is a possible v2-alt if RPN saturates.
- **Cross-representation comparison against folding-Lisp on folding-Lisp's benchmarks.** v2.
- **Variable-length tapes.** Fixed `L=32` in v1.
- **Batched stack execution.** Per-example loop in v1; batched executor is v2 if profiling demands it.

## Summary of unified strengths (what v1 actually takes from each parent)

| From     | Property                                          | Realized in v1 as                        |
|----------|---------------------------------------------------|------------------------------------------|
| CA-GP    | 1D stencil kernel on MLX                          | Layer 6 bond computation (one stencil op)|
| CA-GP    | Flat `(P·E)` batching, config-hash reproducibility | Layers 6, 12                             |
| Folding  | Scaffold preservation (weak form)                 | Active runs survive small mutations      |
| Folding  | Indirect encoding / neutral network               | Inactive cells + non-longest runs = neutral reserve|
| Folding  | Motif emergence (weak form)                       | Active runs act as proto-motifs          |
| Novel    | Crash-proof stack semantics                       | Layer 3 closed RPN + runtime type system |

The "weak form" qualifications are honest. v1 does not test the strong form of scaffold preservation (bonds that genuinely persist across developmental dynamics while tokens change) — that is explicitly v3 territory. v1 tests the minimum downstream consequence of any such mechanism: "does a neutral reserve plus single-active-region decode help stack-GP at all?" If yes, v3 earns the right to study which richer chemistry mechanisms produce the most.

See [experiments.md](experiments.md) (to be written as results come in) for sweep-level hypotheses and v1 results.
