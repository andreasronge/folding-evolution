# Future Applications

Assumes the complexity ceiling is solved (5+ bonds routinely evolved). Each application includes what makes folding's regime-shift advantage relevant and what alphabet/chemistry changes are needed.

**Caveat on "solved":** The ceiling is broken via Pareto-based preservation of compositional intermediates. Experiment 1.11 showed hand-coded `Pareto(scaffold_stage)` achieves S5 in 90% of seeds. Experiment 1.13 then showed `Pareto(structural_pattern)` — a field-agnostic, target-family-general AST objective — nearly matches the hand-coded version on price (18/20 S5) and transfers cleanly to a different target family (amount: 17/20 filter programs). The "semigeneric preservation" claim is defended within compositional program structure (higher-order function + predicate lambda + data source). **The remaining caveat is per-domain, not per-task:** applications that live in a different compositional family (arithmetic expressions for symbolic regression, gate composition for circuits, string/list manipulation for PSB2) each need their own structural_pattern definition — not per-target hand-coding. That is real scope, but far cheaper than a per-problem classifier, and the pattern for defining it is now well-understood from 1.13.

## Tier 1: Minimal Changes to Current System

### Data Transformation Rules / ETL Logic

Evolve transformation rules for data pipelines where the schema or data distribution changes over time.

**Why folding fits**: Upstream data changes shape regularly (new fields, renamed columns, shifted distributions). Static rules break. Folding's regime-shift adaptation means the population can reorganize when the data contract changes, rather than getting stuck on a now-invalid program.

**Changes needed**: Expand the current alphabet with more data types (dates, strings, nested maps). Add chemistry passes for string operations and date arithmetic. The core fold pipeline stays the same.

**Evaluation**: Run candidate transformations against input/output example pairs. Fitness = fraction of examples producing correct output. Coevolution: testers generate edge-case data distributions.

**Benchmark**: Compare against hand-written transformation rules on schema migration scenarios. Measure time-to-correct-output after a schema change vs rewriting rules manually.

### Feature Engineering for ML

Evolve feature expressions (compositions of filter, map, group-by, count, reduce) over tabular data to serve as inputs to a downstream model.

**Why folding fits**: Feature relevance shifts with concept drift. A feature that was predictive last quarter may be noise now. Folding populations can reorganize to track shifting data distributions rather than requiring manual feature re-engineering.

**Changes needed**: Add aggregation fragments (mean, std, min, max, percentile). Add temporal windowing (last_n, rolling). Fitness = downstream model accuracy improvement when the feature is included.

**Coevolution angle**: Testers generate data distributions that expose overfitting features. Oracles define ground truth. The data-dependence gate already prevents constant-output collapse.

**Benchmark**: Compare against AutoFeat, tsfresh, or Featuretools on tabular datasets with temporal splits.

### Business Rule Synthesis

Given input/output examples, evolve the rule that explains the classification. "Why were these orders flagged?"

**Why folding fits**: Business rules change with policy updates, regulatory shifts, seasonal patterns. The population can adapt to new ground truth without starting from scratch.

**Changes needed**: The current fragment types (filter, contains?, match, if, comparators) already map to business logic. Add domain-specific predicates as needed (e.g., `in-range`, `matches-pattern`).

**Evaluation**: Fitness = classification accuracy on labeled examples. Parsimony pressure (shorter rules preferred) via lexicographic selection: accuracy first, then simplicity.

**Benchmark**: Compare against decision tree extraction and RIPPER rule learning on UCI/OpenML classification datasets.

## Tier 2: New Alphabet, Same Fold Architecture

### Symbolic Regression

Replace the data-query alphabet with arithmetic operators and fit mathematical expressions to data.

**Why folding fits**: Symbolic regression under distribution shift (the target function changes over time) is an open problem. Standard GP converges to a fixed expression and cannot reorganize. Folding's pleiotropic mutations enable the structural jumps needed to track a moving target.

**Alphabet**:
```
Functions: sin, cos, exp, log, sqrt, abs
Operators: +, -, *, /, ^
Terminals: x, y, z (variables), constants (0.1, 0.5, 1, 2, pi, e)
Spacers: same role as current Z
```

**Chemistry**: Same multi-pass structure. Pass 1: constants and variables as leaves. Pass 2: binary operators bond to adjacent operands. Pass 3: unary functions bond to adjacent expressions. Pass 4: composition.

**Evaluation**: Fitness = 1 / (1 + MSE) on sample points. Regime shift = change the target function.

**Benchmark**: SRBench (standardized symbolic regression benchmark). Compare folding GP vs DEAP tree GP, PySR, gplearn. The regime-shift variant has no established benchmark — this would be a novel contribution.

**Note**: A 3-bond arithmetic expression like `sin(x * 3.14)` is already useful, making this the most accessible Tier 2 application even before the complexity ceiling is fully broken.

### Digital Circuit Design

Evolve combinational logic circuits from gate primitives.

**Why folding fits**: The 2D fold naturally creates spatial structure analogous to circuit layout. Wire routing emerges from adjacency. This is structurally closest to Hillis's sorting networks but with the fold topology adding a developmental layer Hillis didn't have.

**Alphabet**:
```
Gates: AND, OR, NOT, XOR, NAND, NOR, MUX
Inputs: I0-I7 (input wires)
Outputs: O0-O3 (output wires)
Wires: W (pass-through)
Spacers: Z
```

**Chemistry**: Pass 1: inputs as leaves. Pass 2: NOT bonds to adjacent signal. Pass 3: binary gates bond to two adjacent signals. Pass 4: output wires bond to adjacent gates. Multi-output circuits emerge from multiple output terminals on the grid.

**Coevolution**: Testers generate input patterns that expose circuit failures (exactly Hillis's parasites). Oracles define the target truth table.

**Benchmark**: Evolve N-bit adders, multiplexers, parity circuits. Compare gate count and depth against known optimal circuits and standard CGP results.

### Scheduling / Dispatching Heuristics

Evolve priority rules for job-shop scheduling, task assignment, or resource allocation.

**Why folding fits**: Workload profiles shift (seasonal demand, infrastructure changes, new job types). Static heuristics like shortest-job-first break when assumptions change. Folding populations can reorganize dispatching logic to track shifting workload distributions.

**Alphabet**:
```
Job attributes: processing_time, deadline, priority, resource_req, arrival_time
Queue attributes: queue_length, utilization, avg_wait
Operators: +, -, *, /, >, <, min, max
Conditionals: if, and, or
```

**Chemistry**: Same multi-pass assembly. The evolved expression is a priority function: higher score = higher dispatch priority.

**Evaluation**: Simulate a job queue with the evolved dispatching rule. Fitness = weighted combination of makespan, tardiness, and utilization. Regime shift = change the job arrival distribution or add new job types.

**Benchmark**: Compare against standard dispatching rules (SPT, EDD, WSPT) and hyper-heuristic GP on well-known job-shop scheduling instances (Taillard, OR-Library).

### Evolving Test Oracles / Property-Based Tests

Evolve executable properties that a system should satisfy — essentially evolving QuickCheck-style property tests.

**Why folding fits**: As the system under test evolves (new features, refactored internals), the properties that matter shift. A static test suite becomes stale. Coevolution naturally produces an arms race between the system and its tests.

**Alphabet**:
```
Assertions: equals, not_equals, contains, is_sorted, is_subset, length_eq
Generators: random_int, random_list, random_map, edge_case
Combinators: for_all, implies, and, or, not
Accessors: get, first, last, count
```

**Coevolution**: Solvers are the system under test; testers generate inputs; oracles define expected properties. The frontier scoring function already rewards tests that fail ~50% of candidates — this is exactly what good property tests do.

## Tier 3: Extended Architecture

### Graph Transformation Rules

Extend the 2D grid to represent graph rewrite rules (match pattern -> replacement pattern).

**Why folding fits**: Graph rewriting is inherently spatial — match patterns need adjacency structure. The fold naturally creates the spatial topology for pattern matching. Applications: compiler optimization passes, network protocol rules, chemical reaction rules.

**Changes needed**: Significant. The chemistry needs to distinguish "match side" from "replace side" of the grid. Fragments need graph-structural semantics (node, edge, wildcard-node, wildcard-edge).

**Evaluation**: Apply evolved rewrite rules to a graph; fitness = quality of the transformed graph (e.g., reduced operation count for compiler optimization, improved routing cost for networks).

### Evolving Loss Functions / Reward Shaping

The phenotype is a mathematical expression serving as a loss function or reward signal for training agents.

**Why folding fits**: The optimal loss function changes as the agent improves — easy rewards early, nuanced shaping later. This is a natural regime shift. Coevolution: agents trained with evolved loss functions compete against test environments that expose failure modes.

**Alphabet**: Arithmetic operators + RL-specific terms (state_value, action_prob, entropy, advantage, td_error).

**Evaluation**: Train an agent for N steps using the evolved loss function. Fitness = agent's performance on evaluation episodes. Expensive per-evaluation, so small populations and strong selection pressure.

**Risk**: Each fitness evaluation requires training a model. Computationally heavy. May need surrogate fitness models or very small agent architectures.

### Evolving Communication Protocols

Evolve message-handling rules for distributed agents.

**Why folding fits**: Network conditions shift (node failures, latency changes, topology changes). Protocols need to adapt. The fold representation enables structural reorganization of message-handling logic.

**Alphabet**: Message types, conditions (msg_type, sender, timestamp, payload), actions (forward, store, aggregate, respond, drop), and routing logic.

**Coevolution**: Testers generate adverse network conditions (partitions, delays, Byzantine nodes). Solvers must maintain correctness. Oracles define consistency requirements.

## What Makes a Problem a Good Fit

| Property | Why it matters |
|----------|---------------|
| Compositional solutions from small parts | The chemistry assembles from fragments — monolithic solutions can't emerge |
| Shifting evaluation criteria | The regime-shift advantage is the main differentiator over standard GP |
| Objectively verifiable fitness | Coevolution needs clear pass/fail signals |
| Solution complexity in the 5-20 bond range | Below 5 bonds nothing interesting; above ~20 the search may be intractable |
| Incremental improvement path | The chemistry's multi-pass structure provides natural scaffolding |
| Spatial structure in the solution | The 2D fold adds value when adjacency/topology matters in the phenotype |

## Benchmark Strategy

The applications above describe *where* folding could be useful. This section describes *which benchmarks to run and in what order* to produce publishable claims. Precondition (now met): experiment 1.13 succeeded — `Pareto(structural_pattern)` works as a semigeneric preservation objective, removing the per-task classifier dependency within a compositional family. Per-domain structural_pattern definitions are still required for application areas outside filter/map/reduce (e.g., symbolic regression needs an arithmetic-tree variant), but that is one-time domain setup, not per-problem overhead.

Benchmarks are ranked by what they answer, not by application area.

### Tier A — Competitive credibility

**A1. PSB2 (Program Synthesis Benchmark Suite 2).** Helmuth & Kelly's 25-problem suite is the de facto GP program-synthesis benchmark. Tree GP, PushGP, grammar-guided GP all have published numbers.
- *Why run it:* gets head-to-head numbers with real GP systems, problems span trivial to very hard, success is pass/fail per problem and easy to report.
- *What it shows:* whether folding is competitive at all on standard problems.
- *Risk:* may favor canalized representations on easier problems. Report honestly.
- *Alternative:* PSB1 if PSB2's infrastructure is too heavy.

**A2. Ablation study: representation × preservation mechanism × motif supply.** The single most scientifically important benchmark in this plan because no one else can run it.
- *Design:* 2×2×2 — {folding, tree GP} × {continuous selection, Pareto(scaffold)} × {with, without motif insertion} — on 3–5 hard PSB2 problems.
- *What it answers:* is the advantage from the folding representation, the preservation mechanism, the motif supply, or interactions between them?
- *Possible outcomes:* (a) Pareto(scaffold) rescues tree GP too — preservation is the general insight, folding is incidental. Still a paper, just reframed. (b) Pareto(scaffold) only rescues folding — strong interaction claim. Best outcome. (c) Motif insertion is the dominant factor — shifts the story toward building-block supply.
- *Priority:* high. This is the experiment that tells you what the paper is actually about.

### Tier B — Unique selling point

**B1. Regime-shift variant of SRBench.** Take SRBench's Feynman and Black-Box problems, periodically switch the ground-truth expression every N generations. No standardized regime-shift benchmark exists in symbolic regression — this is a novel contribution, not a reproduction.
- *Compare against:* folding+Pareto(scaffold), PySR, Operon, DEAP tree GP, gplearn.
- *Measure:* mean fitness over time, recovery after shift, number of distinct solutions discovered, fitness jumps.
- *Why it matters:* this is the paper headline if folding wins. Static SRBench is dominated by PySR/Operon — folding likely loses there. The regime-shift variant is where folding's pleiotropy advantage should dominate.
- *Risk:* if folding doesn't win on regime shift, the core project claim needs re-examination.

**B2. Concept-drift tabular feature engineering.** Practical-usefulness angle with a real user base beyond GP researchers.
- *Datasets:* Electricity, Airline Delay, Weather, CoverType — all have known concept drift, all have temporal splits.
- *Compare against:* AutoFeat, Featuretools, tsfresh.
- *Fitness:* downstream model AUC or RMSE improvement with evolved feature added.
- *Regime shift:* train on early time window, evaluate on later — natural temporal drift.
- *Why it matters:* "is this useful" is more compelling to applied reviewers than clean GP benchmarks.

**B3. Transfer / generalization benchmark.** Not listed in the applications above but follows directly from 1.12 Level 2.
- *Design:* evolve on task A with Pareto(scaffold_A), then evaluate unmodified population on related tasks B, C, D without further adaptation.
- *What it answers:* does scaffold preservation build *reusable* modular structure, or does it overfit to the classifier?
- *Ties to:* the Altenberg constructional-selection claim — if evolved populations transfer, the GP map has been reshaped. If not, Pareto is task-specific and the modularity claim needs softening.

### Tier C — Skip or defer

- **Static SRBench as headline result.** PySR and Operon dominate this space. Run only as a ceiling check, not as the main comparison.
- **Digital circuits.** CGP has ~20 years of tuning on this problem family. Narrow comparison, unlikely to win.
- **Scheduling heuristics.** Niche; hyper-heuristic GP literature is small.
- **Loss function evolution.** Each fitness evaluation requires training a model. Computational blocker for 50-seed studies.

### Recommended Ordering

With 1.13 complete and structural_pattern Pareto validated:

1. **Experiment 1.15 (cryptic variation assay)** — runs on existing preserved populations. Closes the evolvability loop before external benchmarks.
2. **A2 ablation on 3–5 hard problems** — answers the scientific question about what the paper is about. Now cleaner because structural_pattern needs no per-problem classifier.
3. **Engineering: structural_pattern v2 for arithmetic** — unlocks SR benchmarks. Parallel track with A2.
4. **B1 regime-shift SRBench** — the paper headline if it works. Requires arithmetic structural_pattern and a tree GP baseline.
5. **A1 PSB2 static** — establishes competitive credibility. May require per-compositional-family structural_pattern definitions (filter, accumulator, mapper).
6. **B2 concept-drift features** — practical-usefulness story for applied reviewers.
7. **B3 transfer/generalization** — tightens the Altenberg claim; 1.15 is a partial preview.

If only two external benchmarks can be run: **A2 + B1.** The ablation tells you what the paper is actually about. The regime-shift benchmark tells you whether the paper is worth writing.

### Symbolic Regression Note

Symbolic regression remains the most pragmatic entry point for a first real-world application because useful expressions emerge at lower bond counts (3-bond `sin(x * c)` is already meaningful) and the alphabet change is straightforward — arithmetic operators slot into the existing chemistry passes. But the headline result is the regime-shift variant (B1), not the static benchmark.
