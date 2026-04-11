# Reading Guide: Key Papers

A "what matters" guide for the key papers behind this project. For each paper: the core insight, why it matters here, and what to look for while reading.

## 1. Genome Growth and the Evolution of the Genotype-Phenotype Map

**Altenberg, L. (1995/2023)**

### Core Idea

Evolution acts not only on phenotypes but also on the structure of the genotype-phenotype (GP) map itself.

```
genotype -> developmental process -> phenotype -> fitness
```

Selection can favor GP maps that produce useful variation.

### Key Insight

There are two types of evolutionary forces:

1. **Selection on traits** — variation -> fitness -> selection
2. **Constructional selection** — selection on *how variation is produced*

Examples of constructional selection:
- Gene duplication
- Modular developmental systems
- Reduced pleiotropy

### Important Concept: Latent Directional Selection

Sometimes populations appear stuck at a local optimum because the GP map cannot generate the right variation.

```
Target phenotype exists
but mutations cannot reach it
```

When the GP map changes (or a new representation appears), evolution suddenly jumps.

### Connection to This Project

Our results match this exactly.

Direct encoding:
- Too canalized
- Mutations affect tail only
- Root expression locked by position 0

Folding encoding:
- Pleiotropic mutations
- Non-local effects through fold topology changes
- Structural jumps via punctuated reorganization

This is almost a textbook case of latent directional selection being released by a different GP map. Direct encoding at fitness 0.10 is a constrained peak — higher-fitness programs exist but the representation creates a kinetic constraint.

---

## 2. Spontaneous Evolution of Modularity and Network Motifs

**Kashtan, N. & Alon, U. (2005)**

### Core Idea

Changing environments that reuse subproblems cause evolution to produce modular structures. They call this **Modularly Varying Goals (MVG)**.

### Experimental Setup

They evolved networks solving tasks like:

```
(A XOR B) OR (C XOR D)
```

Then changed the task to:

```
(A XOR B) AND (C XOR D)
```

Same modules, different combinations.

### Result

Evolution in changing environments was **orders of magnitude faster**.

Why? Because modular solutions can be reused. The key condition:

```
environmental change ~ recombination of modules
```

Not completely random changes.

### Connection to This Project

Our regime shift experiment is similar but simpler. Our environments change:

```
count(products) -> count(employees) -> count(orders)
```

Rather than completely unrelated tasks. The same principle applies: evolution can reuse substructure across regime shifts. This also predicts that regime shifts sharing structural subproblems should show faster recovery than shifts to unrelated targets — a testable prediction.

---

## 3. Coevolution Drives the Emergence of Complex Traits and Promotes Evolvability

**Zaman, L. et al. (2014) — Platform: Avida**

### Core Idea

Arms races drive complexity.

- Static tasks: complexity increases then **plateaus**
- Coevolution: complexity **keeps increasing** because parasites constantly create new pressure

### What They Measure

They track organism genome size, number of logic operations, and task complexity over evolutionary time.

### Result

```
Static environment:   complexity increases -> plateau
Coevolution:          complexity increases -> keeps increasing
```

### Connection to This Project

Our bond-count metric is almost the same measurement as their logic depth / instruction count. Our complexity ceiling at 3 bonds is exactly the phenomenon they were studying — the early plateau pattern before scaffolding emerges.

Key difference: Avida does not vary the genotype-phenotype map. Our system adds a developmental layer (folding) that Avida lacks, which means the complexity ceiling may be a property of the developmental map, not just insufficient search time.

---

## 4. The Structure of the Genotype-Phenotype Map Strongly Constrains the Evolution of Phenotypes

**Dingle, K., Louis, A.A. et al.**

### Core Idea

The GP map determines which phenotypes are accessible. Not all phenotypes are equally reachable. Some appear much more often than others.

### Key Discovery

Random genotypes produce a very biased distribution of phenotypes.

Example in RNA folding:
- Many sequences fold into a few common structures
- Rare structures require extremely specific sequences

### Important Implication

Evolution tends to discover **high-frequency phenotypes**, not necessarily **best phenotypes**, because rare ones are hard to reach through random variation.

### Connection to This Project

Our chemistry likely creates strong phenotype bias. Simple programs like:

```
count + data          (high frequency, few adjacency requirements)
```

appear often. Complex programs like:

```
filter + fn + predicate + data    (low frequency, requires specific 4-way adjacency)
```

require very specific spatial arrangements. So evolution converges to high-frequency phenotypes. This reframes the complexity ceiling: it may not be a search problem but a **phenotype accessibility** problem — 4+ bond programs are rare phenotypes in the fold-chemistry map.

---

## 5. Typogenetics

**Morris, H. (from Hofstadter's Godel, Escher, Bach)**

### Core Idea

A sequence encodes an enzyme that acts on sequences. The strand folds into a structure with:

- Left / right / straight angles
- Binding sites

This folded structure determines how it interacts with other strands.

### Operations

```
copy, cut, insert, delete, splice
```

These are basically genotype editing operations — the enzyme modifies strands based on its folded shape.

### Key Insight

```
sequence -> fold -> behavior
```

This is extremely similar to:

```
genotype -> fold -> chemistry -> program
```

### Main Difference from This Project

Typogenetics focuses on self-replication and strand manipulation. Our system focuses on assembling executable programs from spatial interactions. But the core mechanism — linear sequence folds into spatial structure, spatial structure determines function — is shared.

Typogenetics is the closest historical precursor to our fold-and-bond pipeline.

---

## The Big Picture

These five papers form a coherent story when combined:

| Paper | Contribution |
|-------|-------------|
| Altenberg | Why genotype-phenotype maps matter |
| Dingle / RNA | How GP maps constrain reachable phenotypes |
| Kashtan & Alon | Why changing environments favor modular solutions |
| Zaman / Avida | Why coevolution drives increasing complexity |
| Typogenetics | How spatial folding can determine computational function |

### How This Project Sits Among Them

This system tests all these ideas together:

```
folding GP map + coevolution + regime shifts + complexity measurement
```

That combination is unusual in the literature. Most studies isolate only one of these.

### The Evolvability Balance

One meta-insight across all five papers: the most evolvable systems balance three things:

```
neutrality      too much -> no exploration (evolutionary inertia)
pleiotropy      too much -> catastrophic mutations
modularity      too little -> no scalable complexity
```

Our folding representation increases pleiotropy relative to direct encoding, which explains the superior exploration under regime shifts. The open question is whether evolution can tune the balance — whether evolved genotypes converge toward an optimal pleiotropy level (Experiment 3.2).
