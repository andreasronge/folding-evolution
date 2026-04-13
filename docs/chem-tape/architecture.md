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

- **v1 — Substrate gate (this doc).** *Does persistent local bonding around a fixed tape outperform direct stack-GP on tasks where scaffold completion matters?* Two arms: direct stack-GP vs. chemistry-tape with a fixed trivial bond rule. If B ≤ A on simple string benchmarks, the entire direction is falsified cheaply. If B > A, the separator-based decode earns the right to everything downstream.
- **v2 — Expressivity parity.** *Can chem-tape, extended to match folding-Lisp's problem domain, compete with folding-Lisp on its own benchmarks?* Adds quotation tokens (LAMBDA_OPEN/LAMBDA_CLOSE or Joy-style `[` `]`), structured-record inputs, field-access tokens, control-flow tokens. Alphabet grows to ~30. Enables direct comparison against folding-Lisp on filter/map/reduce queries over records.
- **v3 — Chemistry ablation.** *How much of folding's evolvability comes from the clever multi-pass chemistry, and which mechanism within it?* At matched alphabet (v2's), introduce folding-style chemistry mechanisms one at a time: single-pass → multi-pass staged bonding → + bond priority (assembled > literal > data) → + irreversibility (consumed can't rebond). Five-arm ablation that produces a publishable-grade attribution claim.
- **v4 — Topology ablation.** *Does 2D adjacency contribute beyond chemistry mechanism?* 1D vs. 2D chem-tape at matched chemistry. Separates the dimensionality contribution from the chemistry-mechanism contribution that v3 establishes.

v1 is deliberately the cheapest possible gate. It does **not** by itself test chemistry mechanism, higher-order evolvability, or folding-comparable expressivity — those are v2+ questions that earn their runs only if v1 passes.

## Overview (v1)

```
Genotype (initial tape: 32 bytes — only field under selection in v1)
    |
    v
Fixed chemistry: bond[i] = (tape[i].token != NOP) AND (tape[i+1].token != NOP)
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

Fourteen tokens covering a small typed RPN instruction set. Chosen to be **closed** (every combination executes without crashing — see Layer 3) and sufficient for the v1 benchmark ladder (count-R, has-upper, sum-gt-10).

| id | token         | stack effect                             |
|----|---------------|------------------------------------------|
| 0  | NOP           | — (acts as separator in v1 chemistry)    |
| 1  | INPUT         | → input                                  |
| 2  | CONST_0       | → 0                                      |
| 3  | CONST_1       | → 1                                      |
| 4  | CHARS         | str → charlist                           |
| 5  | MAP_EQ_R      | charlist → boollist                      |
| 6  | MAP_IS_UPPER  | charlist → boollist                      |
| 7  | SUM           | list → int                               |
| 8  | ANY           | boollist → bool                          |
| 9  | ADD           | int, int → int                           |
| 10 | GT            | int, int → bool                          |
| 11 | DUP           | a → a, a                                 |
| 12 | SWAP          | a, b → b, a                              |
| 13 | REDUCE_ADD    | list → int (fixed combinator)            |

Ids 14–15 are unused in v1. Kept available for v2 (LAMBDA_OPEN / LAMBDA_CLOSE) so the alphabet stays at 4 bits/token and rule-table dimensions don't churn when v2 arrives.

**Types are tracked at execution time via tagged values.** `REDUCE_ADD` is a fixed combinator, not a higher-order operator — it sums a list directly. User-provided step functions require quotation tokens and are a v2 feature.

## Layer 3: Execution safety — non-negotiable

Every combination of tokens must produce *some* output. No exceptions, no crashes, no runtime errors. This is the stack-GP analog of folding's "every genotype produces some program" property, and it is load-bearing for evolvability. Without it, the fitness landscape is full of cliffs.

Semantics (not validation errors — semantics):

- Pop from empty stack → yield `0` (or empty list, matched by expected type).
- Wrong-type operand → coerce to a default: non-numeric → `0`, non-list → empty list.
- Hard cap: 256 stack operations per program. Truncate beyond; final stack top is the output.
- End of execution: if stack is empty, output is `0`. Otherwise, top of stack is the output.

## Layer 4: Chemistry (fixed, trivial in v1)

The v1 chemistry rule is deliberately the simplest non-trivial rule:

> **Bond exists between cells `i` and `i+1` iff both tokens are non-NOP.**

Computed in one pass from the tape. No temporal dynamics. No T-step CA. The rule takes the tape as input and emits a bond graph.

This is intentional. v1 is the **substrate gate** — it tests whether the *consequence* of persistent bonding (a neutral reserve plus a bonded "active" region) helps evolution at all. If it does, v2 and v3 earn the right to introduce richer dynamics (typed bonding, multi-pass staging, evolved rules). If it does not, no amount of cleverer chemistry will help either.

**What this trivializes on purpose.** The v1 rule makes NOPs the *only* source of separators — every non-NOP adjacency bonds. A v2.5 or v3 rule could make bonding *type-compatible* (e.g., INPUT bonds to CHARS, CHARS bonds to MAP_*, etc.), or allow bonds to form and break across T steps. Those are planned later ablations, not v1 concerns.

**What this preserves honestly.** Scaffold preservation in v1 is "a contiguous non-NOP region survives small mutations as long as no mutation turns an interior cell into a NOP." Neutral reserve is "NOPs and any non-NOP region shorter than the longest are selection-invisible." Both properties are weaker than folding's, but they are present and measurable.

## Layer 5: Phenotype decode

Walk the tape left to right. Identify all maximal contiguous runs of non-NOP cells (each is a "bonded run"). Execute the **longest** bonded run as an RPN stack program. All other cells — shorter runs and NOPs — are ignored; they form the neutral reserve.

Worked example. Tape:

```
idx:   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 ...
token: 1  4  5  7  0  0  1  4  5  6  8  0  2  9  0  0 ...
```

Token 0 = NOP. Bonded runs are:

- cells 0–3 = `[INPUT, CHARS, MAP_EQ_R, SUM]` (length 4)
- cells 6–10 = `[INPUT, CHARS, MAP_EQ_R, MAP_IS_UPPER, ANY]` (length 5) ← longest
- cells 12–13 = `[CONST_0, ADD]` (length 2)

Executed program: `INPUT CHARS MAP_EQ_R MAP_IS_UPPER ANY`. Everything else is neutral reserve.

**Ties:** if two bonded runs are the same length, pick the leftmost. Deterministic by construction.

**Empty case:** all-NOP tape or all-length-0 runs → empty program → stack ends empty → output `0`.

This "longest run" rule is the v1 simplification of the original spec's concatenated-runs decode. Concatenation produced semantic adjacency between fragments that were never chemically connected; longest-run keeps motif boundaries sharp at the cost of dropping secondary bonded regions.

## Layer 6: Evaluation batching

Same pattern as the CA module. For population `P` and `E` task examples:

- Tapes: broadcast to `(P·E, L)` bytes.
- Bond computation: one stencil op, `bond[i] = (token[i] != 0) AND (token[i+1] != 0)` over the full batch.
- Longest-run finding: compute run-starts and run-lengths with MLX primitives (segment reductions), take argmax, gather the run.
- Stack execution: per-example Python/NumPy loop for v1. At `P=256, E=64` that's 16K evaluations per generation, each ~32 tokens × ≤256 op cap — acceptable unless profiling shows otherwise.

**Batched stack execution** (fixed-size stack tensor with masks) is deferred to v2 or later, only if execution becomes the bottleneck. In v1 the expected hot path is bond computation + longest-run, both of which are MLX-native.

## Layer 7: Genotype and operators (v1)

One evolved array:

- **Initial tape** (`L = 32` bytes). Per-byte mutation at rate `mutation_rate` (default 0.03). Mutation randomizes the low 4 bits (token); high bits stay zero.

Single-point crossover on the tape. Mutation rate and crossover rate are sweep axes.

**No evolved rule table in v1.** The bond rule (Layer 4) is fixed. A rule table becomes an evolved genotype component in v3 (chemistry ablation). This is the main thing v1 strips compared to the original unsimplified spec: tape is 32 bytes, total evolved genotype is 32 bytes, search-space is balanced.

## Layer 8: Evolution loop

Identical to CA-GP. Tournament selection (size 3), elitism (count 2), no niching, no island model, no adaptive rates. The *representation* is the experimental variable; GA machinery stays fixed so the comparison is clean.

## Layer 9: The two research arms

A v1 result means nothing without a comparison. Two arms, sharing the same GA, token alphabet, and stack semantics:

1. **Arm A — Direct stack-GP (null hypothesis).** The tape is executed directly as an RPN program. All 32 tokens participate in execution in tape order; NOPs are no-ops but do not act as separators. This is the stack-GP baseline with no developmental layer.
2. **Arm B — Chemistry-tape v1 (this design).** NOPs act as separators; only the longest non-NOP run executes. This introduces the neutral reserve and separator-based decode.

**Outcomes that discriminate cleanly:**

- **Arm A > Arm B:** separator-based decode throws away information that direct execution uses. The whole chemistry-tape direction is falsified. Stop.
- **Arm A ≈ Arm B:** no effect. The developmental layer neither helps nor hurts. Probably also falsifying — chem-tape's thesis was that persistent bonding helps, not that it's neutral.
- **Arm B > Arm A:** separator-based decode with neutral reserve helps. v2+ earns the right to extend expressivity and study richer chemistry mechanisms.

A v1.5 fixed-typed-chemistry arm (bonds only form between type-compatible tokens) is deliberately deferred to v3, where it becomes the "Arm 2 — multi-pass staged bonding" of the chemistry ablation. Bundling it into v1 would conflate two questions.

## Layer 10: MVP sweep

`sweeps/mvp.yaml` — task = count-R benchmark, `arm ∈ {A, B}` × 10 seeds, fixed `L=32, pop=256, gens=200`, single input-string length (e.g., 16 chars).

**Gate criterion:** Arm B reaches fitness 1.0 on count-R at least as often as Arm A *and* within ≤ 2× the generations on median. If Arm B is strictly worse on this benchmark (where the separator-based decode has no specific advantage), the design doesn't survive contact with an easy problem and further benchmarks are not run.

Only if MVP passes do the real experiments begin on `has-upper` and `sum-gt-10`. The latter exercises `REDUCE_ADD` and is the closest v1 proxy for the reduce-with-lambda target folding-Lisp partially solved. It is the actual test — `sum-gt-10` is where scaffold completion matters most within the v1 alphabet, and is therefore the v1 benchmark that most directly pressures the central hypothesis.

## Layer 11: Backend, engine, and driver

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
    result.json        # best_fitness, best_genotype_hex, elapsed_sec
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
| CA-GP    | Flat `(P·E)` batching, config-hash reproducibility | Layers 6, 11                             |
| Folding  | Scaffold preservation (weak form)                 | Non-NOP runs survive small mutations     |
| Folding  | Indirect encoding / neutral network               | NOPs + non-longest runs = neutral reserve|
| Folding  | Motif emergence (weak form)                       | Bonded runs act as proto-motifs          |
| Novel    | Crash-proof stack semantics                       | Layer 3 closed RPN                       |

The "weak form" qualifications are honest. v1 does not test the strong form of scaffold preservation (bonds that genuinely persist across developmental dynamics while tokens change) — that is explicitly v3 territory. v1 tests the minimum downstream consequence of any such mechanism: "does a neutral reserve plus single-active-region decode help stack-GP at all?" If yes, v3 earns the right to study which richer chemistry mechanisms produce the most.

See [experiments.md](experiments.md) (to be written as results come in) for sweep-level hypotheses and v1 results.
