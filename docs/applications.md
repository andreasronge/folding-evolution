# Future Applications

Assumes the complexity ceiling is solved (5+ bonds routinely evolved). Each application includes what makes folding's regime-shift advantage relevant and what alphabet/chemistry changes are needed.

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

## Recommended Starting Point

**Symbolic regression** is the most pragmatic entry point:
1. Well-benchmarked (SRBench) — results are directly comparable to existing work
2. Useful expressions emerge at lower bond counts than data queries (3-bond `sin(x * c)` is already meaningful)
3. The regime-shift variant (tracking a changing target function) is a novel benchmark contribution
4. The alphabet change is straightforward — arithmetic operators slot into the existing chemistry passes
5. If folding shows an advantage on regime-shift symbolic regression, it's a publishable result on its own
