# Theoretical Framework — Cellular Automata

Reading list and conceptual framing for the CA branch of this project. Focused on cellular automata evolved with genetic algorithms, parity / global computation, and representation changes affecting evolvability. Papers are grouped so they map directly to the mechanisms tested in the §11 experiments (`docs/ca/experiments.md`).

## 1. Foundations: Evolving CA to Perform Computation

The core papers that established the field.

- **Mitchell, M., Hraber, P., & Crutchfield, J. P. (1993)**. "Revisiting the Edge of Chaos: Evolving Cellular Automata to Perform Computations." *Complex Systems* 7:89–130. https://arxiv.org/abs/adap-org/9303003 — Introduced GA-evolved CA for global tasks and analyzed how computational strategies emerge.
- **Mitchell, M., Crutchfield, J. P., & Hraber, P. T. (1994)**. "Evolving Cellular Automata to Perform Computations: Mechanisms and Impediments." *Physica D* 75:361–391. https://melaniemitchell.me/PapersContent/MitchellCruchfieldHraber1994.pdf — Detailed analysis of evolutionary dynamics and symmetry-breaking effects in evolved CA.
- **Crutchfield, J. P., Mitchell, M., & Das, R. (1998)**. "The Evolutionary Design of Collective Computation in Cellular Automata." https://arxiv.org/abs/adap-org/9809001 — Introduced the "particle computation" framework for understanding evolved CA.
- **Mitchell, M., Crutchfield, J. P., & Das, R. (1996)**. "Evolving Cellular Automata with Genetic Algorithms: A Review of Recent Work." *Proceedings of EvCA'96*. — Survey of early evolutionary CA research.

## 2. Emergent Computation and Particle Systems

How CA actually perform computation once evolved.

- **Das, R., Mitchell, M., & Crutchfield, J. P. (1994)**. "A Genetic Algorithm Discovers Particle-Based Computation in Cellular Automata." *PPSN III*.
- **Hordijk, W., Crutchfield, J. P., & Mitchell, M. (1998)**. "Mechanisms of Emergent Computation in Cellular Automata." *PPSN V*.

Key idea from this line of work:

> CA computation = information-carrying particles + collisions implementing logic

This is the conceptual framework most relevant for parity and global tasks.

## 3. Parity Problem in Cellular Automata

Theoretical limits and explicit constructions.

- **Betel, H., Oliveira, P., & Flocchini, P. (2012)**. "On the Parity Problem in One-Dimensional Cellular Automata." https://arxiv.org/abs/1208.2758 — Key result: radius-2 CA cannot solve parity; radius-4 CA can. Parity requires significant information propagation.
- **Wolnik, B., Nenca, M., et al. (2025)**. "Cellular Automata Can Really Solve the Parity Problem." https://arxiv.org/abs/2501.08684 — Provides a corrected proof that a single CA rule can solve parity globally.
- **Lee, J., Xu, X., & Chau, H. (2001)**. "Parity Problem with a Cellular Automaton Solution." https://arxiv.org/abs/nlin/0102026 — Key result: parity can be solved by a *sequence* of CA rules. Directly motivates multi-phase CA schedules.

## 4. Representation and Evolvability

How CA rule representations affect evolutionary search.

- **Sipper, M. (1997)**. *Evolution of Parallel Cellular Machines: The Cellular Programming Approach.* Springer. — Introduced non-uniform cellular automata evolved with genetic algorithms. Key insight: uniform CA enforce a symmetry constraint; non-uniform CA allow specialization. Highly relevant for banded CA experiments.
- **Stone, C., & Bull, L. (2009)**. "Solving Density Classification Using Cellular Automata with Memory." *Turkish Journal of Electrical Engineering & Computer Sciences.* — Adding memory improves evolvability. Relevant for second-order CA experiments.

## 5. Dynamical Systems Context

Why CA capable of computation appear near critical dynamics.

- **Langton, C. (1990)**. "Computation at the Edge of Chaos." *Physica D.* — Introduced the idea that complex computation occurs near phase transitions in CA behavior.
- **Mitchell, M., Crutchfield, J. P., & Hraber, P. (1993)**. "Dynamics, Computation, and the Edge of Chaos: A Re-Examination." https://arxiv.org/abs/adap-org/9306003 — Revisited Langton's hypothesis and examined how evolution navigates rule space.

## Key Insights Relevant to §11 Experiments

### 1. Computation emerges from particle systems

Evolved CA strategies rely on information particles, domain boundaries, and particle collisions. If a rule language cannot support stable carriers, evolution cannot discover computation.

### 2. Uniform rules impose symmetry constraints

Uniform CA force every cell to perform the same function. Non-uniform CA allow specialization — transducer cells, transport cells, logic cells, reduction cells.

Prediction: **banded CA > uniform CA**.

### 3. Sequential rule application increases computational power

Parity can be solved with rule sequences even when single rules fail.

Prediction: **phase schedule CA > stationary rule CA**.

### 4. Memory enables persistence of information

Without memory, each CA update overwrites all state. Memory allows partial information to survive.

Prediction: **memory CA > memoryless CA**, but likely smaller effect than specialization.

### 5. Global tasks require long-range information transport

Parity requires information propagation across the lattice. Mechanisms that increase effective propagation radius:

- specialization (banding)
- temporal staging (phases)
- memory persistence

All three correspond exactly to the §11 experiments.

## Mechanism → Experiment Mapping

| Mechanism | Literature support | §11 experiment |
|-----------|-------------------|----------------|
| Specialization across cells | Sipper 1997 (non-uniform CA) | banded CA vs uniform CA |
| Sequential rule application | Lee/Xu/Chau 2001 (rule sequences solve parity) | phase schedule CA vs stationary CA |
| Memory persistence | Stone & Bull 2009 (memory improves evolvability) | second-order / memory CA vs memoryless |
| Information propagation radius | Betel/Oliveira/Flocchini 2012 (radius-2 cannot, radius-4 can) | sweep over neighborhood radius |
| Particle-based computation | Crutchfield/Mitchell/Das 1998 | diagnostic analysis of evolved rules |
