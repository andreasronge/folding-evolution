# Future Directions: Representation and Chemistry Evolution

This document sketches research directions for evolving the folding representation and chemistry beyond its current form. It is motivated by two separate pressures:

1. **Benchmark competitiveness.** To speak to established GP benchmarks (PSB2, SRBench, FlashFill-style program synthesis) the representation needs support for program constructs the current chemistry does not naturally generate — multi-argument functions, strings, booleans, recursion, typed data flow.

2. **Representation-level limitations uncovered by experiments 1.15 – 1.15c.** The reachability check showed that the current alphabet/chemistry generates one narrow compositional family (1-arg predicate/accessor pipelines over tabular data). Specific gaps have been isolated mechanistically — the clearest being that 2-argument lambdas are effectively unreachable under random assembly, which blocks `reduce` and any aggregator that needs an accumulator pattern.

The current alphabet and chemistry were selected by hand during early Elixir prototyping. No claim has been made that the 62-character layout, 8-connected 2D grid, or 5-pass chemistry is optimal — they were one reasonable first choice. Rethinking them is scope for the *next* project phase, after the current paper's bounded claims are written up.

---

## Motivation: What the Findings Say About the Representation

Across the 1.15 series, three boundary conditions on the current system have become explicit:

1. **Reachable compositional structure is narrow.** 10,000 random length-100 genotypes produce zero full-signature reduce-with-2arg-lambda programs and zero first-of-filter-with-string-equality programs. The representation is a generator for 1-arg predicate/data pipelines, not for general compositional programs.

2. **The scoring function's partial-credit geometry interacts heavily with what "transfer" means.** Pareto preservation yields benefit only when inherited outputs remain partially scorable against the novel target. Changing output type (count → first, returning an object) defeats the mechanism.

3. **Motif discovery and preservation are solved within the reachable family.** Chemistry screening surfaces the right building blocks (top 0.08% of 242K substrings); `Pareto(structural_pattern)` preserves them through evolution. But this mechanism's scope is bounded by what the representation can fold *at all* — it does not rescue cross-family reachability.

The productive reading: the current project validated a preservation mechanism within one compositional family. Extending the claim requires extending the representation.

---

## The 2-Argument Lambda Problem (Concrete and Unblocking)

### Why it matters

`reduce`, `fold`, `scan`, `zip-with`, and any aggregator with an accumulator all require a 2-argument function `(fn a b body)`. With the current chemistry these constructs are structurally unreachable — the `fn` fragment (character `Q`) binds exactly one adjacent expression to form `(fn [x] expr)`. There is no alphabet character for a 2-argument binding form, and the chemistry has no rule that consumes *two* variable slots before a body.

This matters for:
- SRBench symbolic regression with terms like `(+ x y)` inside `(reduce ...)`
- PSB2 problems requiring accumulators (sum-of-digits, string reversal, running maximum)
- Feature engineering with pairwise reductions
- Any functional-style program synthesis benchmark

### Option A: Add a distinct alphabet character for 2-arg fn

Simplest fix. Introduce a new fragment (e.g., reassign an unused slot from the i-z wildcard range) that maps to `(fn [a b] body)`. Chemistry pass 2 gets a new rule: `fn2 + two expressions → (fn [a b] expr1 using a, expr2 using b)`, or more realistically `fn2 + one body expression where the body can reference two implicit argument symbols`.

Pros:
- Minimal disruption. Existing experiments still run.
- Easy to A/B test: add the character, rerun 1.15 cross-family transfer, see if reduce becomes reachable.

Cons:
- Still doesn't address the underlying issue (the chemistry has no notion of argument binding — it relies on implicit `x`). Generalizing past 2 args requires a new character per arity, which is a combinatorial mess.
- "The body can reference two implicit argument symbols" is not well-defined without explicit variable binding.

### Option B: Explicit variable-binding characters

Add a character class that represents *bound variable references*, distinct from the current field-key alphabet (a-h). The `fn` fragment would bond with a sequence of variable-declaration characters, then a body expression. E.g., `fn var1 var2 body` → `(fn [var1 var2] body)`.

Pros:
- Composable to n-arg lambdas without alphabet explosion.
- Supports `let`, `loop`, `for` naturally (all need named bindings).

Cons:
- Requires a scoping mechanism. Which expression references which variable? The chemistry needs to track binding context, not just adjacency.
- Big chemistry refactor. Current chemistry is pass-based and context-free; scoping is context-sensitive.

### Option C: De Bruijn indices

Drop named variables entirely. Lambdas bind positionally: `(fn body)` where the body contains `#0`, `#1`, etc. for the nth enclosing binder.

Pros:
- Eliminates the scoping problem cleanly.
- More compact representation.
- Standard in compiler theory; well-understood semantics.

Cons:
- Human-readable programs become unreadable (`(fn (fn (+ #0 #1)))` for a 2-arg sum).
- Higher folding fragility: a small genotype change can shift index references unpredictably.

### Option D: Combinator-based (point-free) programs

Remove explicit variables entirely. Use combinators (`K`, `S`, `B`, `C`, `compose`, `flip`) and primitive aggregators (`sum`, `product`, `maximum`) that take the binary operation implicitly.

Pros:
- Zero binding problem — no variables to name.
- Folds cleanly: point-free programs are compositions, which adjacency encodes naturally.
- Well-studied evolvability literature around SKI combinators (Koza, Banzhaf).

Cons:
- Expressively limited without a rich combinator set.
- Requires replacing the current data-query alphabet entirely.
- Fundamental representation change, not a fix.

### Option E: Dedicated higher-order primitives with implicit binding

Instead of `(reduce (fn a b (+ a b)) 0 data)`, use `(sum-over data)` or `(reduce+ data 0)`. Each common aggregator gets its own alphabet character with fixed semantics; no general binding form.

Pros:
- Solves the reduce-blocking problem immediately.
- Extremely evolvable: fewer parts to assemble.
- Matches how much production code is actually written.

Cons:
- Loses the compositional generality that makes GP interesting.
- Each new aggregator is a new alphabet character — combinatorial again.
- Doesn't transfer to map+index, scan, fold-right, etc. without adding a character each.

### Recommended direction for this specific problem

Start with **Option A** (add a 2-arg fn character) as an engineering-cheap first experiment. Measure: does reduce become reachable? Does the 1.15 transfer advantage survive? If yes, we have a working system with two lambda arities. If Option A stalls (e.g., 2-arg fn sits unused because the chemistry can't route two expressions to it productively), escalate to **Option B** (explicit variable binding).

**Option C and Option D are project-level restarts**, not incremental fixes. Worth considering if the paper's reviewers push back on the narrow-family claim, but not before.

---

## Direction 2: Type-Aware Chemistry

The current chemistry is untyped: any adjacent pair bonds according to positional rules. Field keys and literals bond equally; the chemistry trusts the alphabet design to keep things sensible.

A typed chemistry would carry type tags on each fragment and refuse to bond incompatible types. `(> 5 data/products)` is nonsense but currently representable; a typed chemistry would reject this bond and try a different partner.

### What typed chemistry would enable

- **Boolean return types** for predicates. `and`, `or`, `not` can only take booleans. Currently the chemistry allows them to take anything; half the time they produce runtime errors that get clamped to null output.
- **Numeric vs string discrimination.** `(> x "hello")` is currently representable; a typed chemistry forbids it.
- **Collection-element type propagation.** `(filter pred list-of-products)` should only accept a predicate whose argument type matches the element type.
- **Rich data types beyond the current tabular model** — strings, dates, nested structures. Each gets distinct fragment types; the chemistry becomes a type-directed assembler.

### Tradeoffs

Pros:
- Eliminates "junk" bonds that don't evaluate. Higher fraction of folded genotypes are valid programs.
- Makes the representation competitive on PSB2 (string/list-heavy benchmarks) because string fragments can have typed bonding rules.
- Motif discovery gets cleaner: screening can restrict to type-valid motifs only.

Cons:
- More complex chemistry. Adjacency no longer sufficient; bonding requires type resolution.
- May reduce evolvability. The current chemistry's "any bond is a valid bond" property is part of why it has high pleiotropy. Enforcing type rules may over-constrain mutations.
- Loss of graceful degradation. Currently mutations rarely produce total errors; typed chemistry would produce more no-ops.

### Research question

Does a typed chemistry produce a better static/dynamic tradeoff than the untyped chemistry? Specifically: higher neutrality (types canalize mutations), similar or better regime-shift adaptation (the extra structure doesn't block reorganization)?

This is a *measurable* research question with the existing Altenberg-inspired metrics (neutrality, pleiotropy, crossover preservation, regime-shift recovery). A minimal-viable typed chemistry could be implemented and compared to the current version on the same task suite.

---

## Direction 3: Alternative Developmental Processes

Folding is one choice out of many for "how does a linear genotype become a 2D program structure." The current project's findings (discrete scaffold preservation, partial-credit interaction) may be specific to folding, or they may be general across any compositional development process. Characterizing alternatives with the same metrics would tell us which.

### 3.1 Stack-based development (push/pop)

Read the genotype left-to-right. Each character is either a **value** (push a fragment onto a stack) or an **operator** (pop the required number of operands, build the fragment, push result). The final stack state is the program.

- Well-studied in GP (PushGP, Stack-based GP, Forth-style systems).
- Loses 2D adjacency entirely. Pleiotropy comes from stack-depth dependencies, not spatial topology.
- **Comparison test:** run the existing 1.15 pipeline with stack-based development. Does scaffold preservation still produce the same distribution non-overlap? Does the elevated-baseline effect appear? If yes, preservation is a general property. If no, folding's spatial structure is load-bearing.

### 3.2 Tree-development automaton

Genotype encodes a sequence of tree-construction instructions: "push left child," "push right child," "pop and bind operator." Produces a tree directly, no 2D intermediate.

- Similar to grammatical evolution / gene expression programming.
- More expressive than stack-based (can build arbitrary trees).
- **Key tradeoff:** trees have no adjacency richness; all structure comes from instruction order.

### 3.3 3D or hexagonal folding

Same fold algorithm, but on a 3D lattice (6 neighbors per position) or 2D hexagonal grid (6 neighbors). More adjacency opportunities per position, richer bonding patterns.

- Preserves the spirit of folding — 2D → 3D is an incremental generalization.
- Might address the 2-arg lambda problem naturally: 3D gives enough adjacency slots for `fn` to bond with two variable characters *plus* a body.
- **Cost:** implementation complexity, visualization harder. Benefit uncertain without measurement.

### 3.4 Cellular-automaton development

Genotype seeds a 2D grid. CA rules run for N steps. Final grid state is decoded to a program. The chemistry becomes the CA rules.

- Used in Miller's Cartesian GP variants.
- Radically different dynamics. Mutation effects propagate via CA rules, not direct adjacency.
- **Research question:** can CA development produce higher complexity ceilings than folding? The CA can build structure iteratively, not just from initial adjacency.

### 3.5 Compositional graph rewriting

Genotype encodes a sequence of graph-rewrite rules applied to a starting "seed" program. Each rewrite replaces a pattern with a substitution.

- Most biological. Closer to gene regulatory networks and cell differentiation.
- Very expressive; very hard to analyze.
- Probably out of scope for this project but worth flagging.

### Recommended comparative program

Don't redesign from scratch. Pick one alternative — **stack-based** is cheapest and has the richest GP literature to compare against — and measure the same metrics on the same task suite. If stack-based hits similar scaffold-preservation results, folding's spatial structure is not essential to the paper's claims. If stack-based fails to preserve scaffolds under Pareto, spatial structure *is* essential and that's a publishable finding on its own.

---

## Direction 4: Revival of Evolvable Chemistry

Experiment 1.8-era explored making the chemistry itself evolvable (`DevGenome` with distance weights, bond affinities, stability parameters). The result was partial: evolvable d2 (distance-2 bonding) increased bond counts but not fitness, and the shared-DevGenome-per-population design was too coarse.

Worth revisiting with lessons from 1.9–1.15:

- **Individual-level chemistry variation.** Each genotype carries its own short chemistry-parameter suffix. Mutations to the suffix produce individuals with slightly different bonding rules. Compositional recursion: the chemistry that develops the program is itself part of the program's hereditary material.
- **Chemistry-scaffold Pareto.** Pareto selection on (fitness, scaffold_stage, chemistry_distance_from_baseline). Preserves both program structure and chemistry variants that produce useful structure.
- **Cross-family chemistry discovery.** Start with current chemistry, evolve against a reduce-family task. Does the chemistry evolve to produce 2-arg lambdas? If yes, chemistry evolution is a legitimate path to cross-family competence. If no, the chemistry search space is too rough for evolution to cross.

This is a higher-risk direction but directly addresses the "current chemistry was randomly selected" concern.

---

## Direction 5: Domain-Specific Alphabet Extensions for Benchmarks

For each benchmark family the project wants to compete on, the alphabet and chemistry need specific extensions. None of these are conceptually hard — they are engineering — but each has tradeoffs the paper should acknowledge.

### Symbolic regression (SRBench)

- Drop tabular data alphabet (data/products etc.) entirely.
- Add arithmetic operators: `+ - * / ^ sin cos exp log sqrt abs`
- Add variables (`x y z`) and constants (`0.1 0.5 1 2 π e`).
- Chemistry passes: literals+variables first, binary operators second, unary functions third, composition fourth.
- Evaluation: MSE on sample points; regime-shift = change the target function.
- The 3-bond sweet spot already produces `sin(x * c)` and similar — meaningful expressions at low bond counts.

### Program synthesis (PSB2)

- String/list/integer fragments with type tags (see Direction 2).
- Conditional and loop primitives: `if`, `for-each`, `while` (or bounded iteration).
- I/O primitives for example-based evaluation.
- Big alphabet (40+ characters). Chemistry needs type-respecting bonding.
- Hardest extension by far; probably requires all of Direction 1 + Direction 2.

### Digital circuits

- Boolean fragments with typed bonding.
- Gate operators (AND, OR, NOT, XOR, NAND, MUX).
- Input/output ports.
- Clean target — truth tables with exact match.
- Compare against CGP, which is the dominant approach in this space.

### Feature engineering (concept-drift ML)

- Aggregation operators: mean, std, min, max, percentile.
- Temporal windowing: last_n, rolling, expanding.
- Data-source alphabet reused from current design.
- Probably the smallest extension from where we are now.

### Business rule synthesis

- Extend current alphabet with `in-range`, `matches-pattern`, string-comparison operators.
- Most similar to current domain — minimal changes needed.

---

## A Comparative Research Program

Rather than picking one direction and committing, the project could formulate a **comparative representations study** as a standalone paper or follow-up work. The template:

1. Define a common test suite: 3–5 tasks spanning filter, reduce, conditional, arithmetic, and string families.
2. Implement minimal-viable variants of the current system extended in each direction (fix 2-arg lambda, add typing, switch to stack-based, etc.).
3. Apply the same evaluation framework — the Altenberg-inspired static/dynamic metrics plus the 1.15-style bounded-claim methodology (reachability check, matched-fitness non-overlap, scoring-geometry dependence).
4. Report: for which direction of change does which metric improve? Where does the 1.15 bounded claim generalize, and where does it break?

This converts "which representation is better?" (unanswerable in the abstract) into "what tradeoffs does each representation choice commit you to?" (answerable with measurement).

---

## Priority Recommendations

Given finite engineering time, the sequence I'd recommend:

**Tier 1 — cheap, directly addresses known blockers:**
1. Add 2-arg fn character (Option A from Direction 1). Measure reachability change. ~1 week of work including experiments.
2. Implement a minimal stack-based development variant (Direction 3.1). Run 1.15 pipeline on it. ~2 weeks. This is the cheapest way to test whether folding's spatial structure is load-bearing for the preservation claim.

**Tier 2 — substantial but unblocks a benchmark:**
3. Domain-specific alphabet for symbolic regression (Direction 5). Enables SRBench and B1 regime-shift SR benchmark (currently blocked). ~3–4 weeks.
4. Type-aware chemistry prototype (Direction 2). Test on current filter-family tasks first; if neutrality and regime-shift metrics hold up, extend to boolean/string domains. ~4–6 weeks.

**Tier 3 — project-scale, answers foundational questions:**
5. Evolvable chemistry revival (Direction 4) with individual-level variation and Pareto-on-chemistry. Tests whether the chemistry can evolve across family boundaries on its own.
6. Comparative representations study (the full program above). Would be a follow-up paper.

**Not recommended now:**
- De Bruijn indices (Option C) — project-level restart, not a fix.
- Combinator-based (Option D) — same.
- 3D folding (Direction 3.3) — speculative benefit, high cost.
- Cellular-automaton development (Direction 3.4) — radically different dynamics, hard to compare.

---

## Relationship to the Current Paper

This document describes *next-project* work. The current paper (from the 1.15 series) should close out with the bounded claim already defended:

> *Within the representation's natural compositional family and scoring-compatible target family, Pareto preservation produces scaffold-rich numeric programs with transferable structure; continuous selection collapses to specialist basins.*

The reachability and scoring-geometry boundaries should be disclosed as explicit scope constraints, not glossed over. That positions the current paper as a *complete* result within its stated bounds, and this document as the research program that would expand those bounds.

The representation-level improvements here are the natural next paper — "Folding GP II: Typed Chemistry and Cross-Family Transfer" or similar — not a revision to the current work.
