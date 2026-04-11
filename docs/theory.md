# Theoretical Framework

## Altenberg's Constructional Selection

The primary theoretical grounding comes from Lee Altenberg's "Genome Growth and the Evolution of the Genotype-Phenotype Map" (1995/2023).

### Key Connections to Our Work

**Bonner's Low Pleiotropy Principle vs Directional Selection**

Bonner (1974) argued low pleiotropy is necessary for evolvability — mutations affecting few traits are less likely lethal. Our static metrics confirmed this: direct encoding's low pleiotropy (87% neutrality, 2% large breaks) looks "safer."

But Altenberg distinguishes *stabilizing* selection (low pleiotropy wins) from *directional* selection (variation aligned with the selection gradient wins, even if pleiotropic). Our regime shift IS directional selection. Folding's high pleiotropy enabled the large phenotypic jumps that direct encoding couldn't achieve.

**Latent Directional Selection (Altenberg Section 2.7)**

Populations stuck on "constrained peaks" — appearing at a fitness maximum, but only because the G-P map can't produce the right variation. This is exactly direct encoding at fitness 0.10. Higher-fitness programs exist, but the representation creates a *kinetic constraint*. The "latent directional selection" is invisible until folding opens the right variational dimensions.

**The Genome as Population (Section 2.4)**

Altenberg proposes treating the genome as a population of genes, where genes with high "constructional fitness" proliferate. For our genotype strings: subsequences that fold into useful active sites should proliferate within evolved genotypes. This predicts measurable **motif enrichment** in evolved populations — a testable prediction (see Experiment 3.1).

**Type I and Type II Effects (Sections 2.4-2.5)**

- **Type I (genic selection)**: Genes that produce good duplicates proliferate within the genome. The planned Phase 3 genotype-level rewriting IS a Type I mechanism.
- **Type II (correlated allelic variation)**: Alleles of established genes tend to be adaptive because the gene's mode of action is correlated between origin and subsequent variation. Our folding chemistry creates Type II effects — a character's phenotypic contribution depends on fold neighbors, and fold topology is heritable.

**Wagner's Linear Model (Section 4)**

Three-layer model: genotype x -> phenotype y = Ax -> fitness. Our fold is a non-linear "A matrix." Under Gaussian stabilizing selection, new genes with low pleiotropy are favored. This predicts: under steady-state conditions (no regime shifts), folding should be at a disadvantage — confirmed by static metrics. The right G-P map depends on environmental stability.

## The Central Prediction

Altenberg's framework makes a clean, testable prediction for our system:

| Selection regime | Predicted winner | Reason |
|-----------------|-----------------|--------|
| Stabilizing (fixed target, 200 gens) | Direct encoding | Low pleiotropy avoids disrupting established fitness |
| Directional (shifting target, every 10 gens) | Folding | Pleiotropic mutations create the large jumps needed to track moving targets |

This is Experiment 2.3 — the single most theoretically informative experiment we can run.

## Protein Folding Analogy

The system is inspired by protein folding:

| Biology | Our System |
|---------|-----------|
| Amino acid chain | Genotype string |
| 3D folding based on local interactions | 2D folding based on fold instructions |
| Adjacent amino acids form active sites | Adjacent characters bond into program fragments |
| One mutation can restructure the fold | One character change can rearrange the grid |
| Neutral mutations in non-structural regions | Mutations in spacer/wildcard characters |
| Frameshift mutations from insertions/deletions | Insertion/deletion shifts downstream fold |

The analogy is structural, not chemical. We're not modeling physics — we're borrowing the key insight that **linear sequence -> spatial arrangement -> function** creates interesting evolutionary properties.

## Related Work

This project sits at the intersection of five research threads. The specific combination — string → spatial fold → local chemistry → executable symbolic program → coevolution — appears to be a novel recombination of several older ideas rather than a direct reimplementation of any one prior model.

### 1. Theory: GP-Map Evolution and Constructional Selection

- **Altenberg, L. (1995/2023)**. "Genome Growth and the Evolution of the Genotype-Phenotype Map." In *Evolution and Biocomputation*, Springer LNCS vol. 899, pp. 205-259. — The theoretical backbone. His "constructional selection" view is explicitly about evolution acting on the genotype-phenotype map itself and on the kinds of variation a representation makes available. Closest theoretical match for our shift from "evolve better programs" to "what developmental map produces better evolvability under different regimes?"
- **Wagner, G.P. (1989)**. "The origin of morphological characters and the biological basis of homology." — Linear G-P map model. Three-layer model (genotype → phenotype → fitness) predicts low pleiotropy wins under stabilizing selection — confirmed by our static metrics. The right G-P map depends on environmental stability.
- **Bonner, J.T. (1974)**. *On Development*. — Low pleiotropy principle. Our static metrics confirmed Bonner's prediction; our dynamic results show it fails under directional selection.
- **Manrubia et al., Nichol et al.** — Reviews on GP-map structure emphasizing that neutrality, phenotypic bias, robustness, and accessibility of variation shape evolutionary dynamics. Supports measuring these as properties of the map, not just of individual programs.

### 2. GP-Map Structure: RNA and Neutral Networks

The strongest biological analogue to our folding layer. In RNA, a linear sequence maps to a folded secondary structure, and the structure of that map produces neutrality, robustness, phenotypic bias, and constrained innovation.

- **Dingle, Louis et al.** — RNA GP-map structure strongly constrains evolution. Phenotypic bias and accessibility properties of the map shape evolutionary outcomes. Most relevant for interpreting our neutrality, pleiotropy, and regime-shift findings.
- **Wagner, A.** — Robustness and evolvability via neutral networks. Uses RNA as a core example of how neutral networks coexist with innovation. Our static-vs-dynamic discrepancy (high neutrality looks good statically but is inertia dynamically) maps directly to this framework.
- **Kimura, Huynen** — Neutral evolution theory and how neutral mutations enable exploration of genotype space.

### 3. GP Precedents: Indirect Encodings and Dynamic Environments

- **O'Neill & Ryan** — Grammatical Evolution. Closest GP precedent on the "linear genome indirectly yields executable program" axis. GE uses a grammar-based mapping with neutrality via redundant codons. Our system differs because indirection is spatial and chemistry-like rather than grammatical.
- **Miller** — Cartesian Genetic Programming. Close match on neutrality, inactive genetic material, and many-to-one mappings. Our "spacers / junk-DNA-like regions" are in the same family of ideas, though our phenotype is assembled by spatial adjacency rather than indexed graph decoding.
- **Stanley** — Artificial embryogeny / developmental encodings. Taxonomy of indirect encodings where the genome drives a developmental process. Conceptually close to our fold-and-bond pipeline, though most of that literature grows graphs, circuits, or neural networks rather than symbolic programs.
- **O'Neill et al. (GECCO 2011)** — "Dynamic Environments Can Speed Up Evolution with Genetic Programming." Explicitly tested the Kashtan & Alon hypothesis inside GP using "structurally varying goals" (SVG) where tasks share subproblems. Key comparison point: they tested environmental variation as a property of the task; we test it as an interaction with the representation. Their result was about convergence speed; our result is about representational accessibility (direct encoding never discovers the solution, not just slowly).

### 4. Evolutionary Dynamics: Coevolution and Changing Environments

- **Hillis, W.D. (1990)**. "Co-evolving parasites improve simulated evolution as an optimization procedure." — Foundational reference for coevolution as a way to escape local optima. Direct precedent for our solver/tester/oracle ecology.
- **Zaman et al. (2014)** — "Coevolution Drives the Emergence of Complex Traits and Promotes Evolvability." Host-parasite coevolution in Avida leads to more complex digital organisms vs static environments. Our bond count trajectory is analogous to their instruction count / logic depth metric. Our complexity ceiling at 3 bonds mirrors the early plateau pattern in Avida experiments before scaffolding emerges. Key difference: Avida does not vary the genotype-phenotype map.
- **Lenski et al.** — "The Evolutionary Origin of Complex Features." Complex traits evolve through incremental scaffolding of simpler ones (NOT → NAND → AND → EQU). Our chemistry has a similar scaffolding structure (get+key → comparator → fn predicate → filter) but evolution currently stalls at count+rest. This suggests the complexity ceiling is a property of the developmental map, not just insufficient search time.
- **Kashtan & Alon** — Modularly varying goals. Varying environments speed evolution and promote modular structure. Natural comparison for our regime shift result. Previous work showed that modularly varying environments accelerate evolution in neural networks, logic circuits, and some GP systems — but those studies treated the genotype-phenotype mapping as fixed. Our result shows that the choice of developmental encoding fundamentally alters the system's ability to respond to environmental shifts.
- **Clune, Mouret, Lipson** — "The Evolutionary Origins of Modularity." Changing environments cause evolution to produce modular structures. Complements Kashtan & Alon.
- **Gupta et al.** — Coevolution deforming fitness landscapes to open new innovations. Precedent for our coevolution designs, though our "single shared representation with fluid roles" is a more representation-centric twist.
- **Kauffman, S.A. (1989)**. "Adaptation on rugged fitness landscapes." — NK adaptive landscape model.

### 5. Mechanism: Fold-Dependent Assembly of Executable Structure

- **Morris, H. — Typogenetics** (from Hofstadter's *Gödel, Escher, Bach*). Closest historical precursor. A strand encodes operations on itself, and the strand's derived "enzyme" has a 2D tertiary structure with left/right/straight folding inclinations; that folded structure determines binding preference and where operations act. Overlaps on: linear symbolic sequence, folding-derived structure, local binding/adjacency effects, executable consequences, ALife framing. Key difference: Typogenetics is about self-transforming/self-reproducing strands; our system uses a folded string to assemble a *separate* executable symbolic phenotype via local chemistry rules. Self-modification vs program synthesis.
- **Fontana & Buss — Algorithmic Chemistry (AlChemy)**. Molecules are computational objects whose interactions generate new computational objects. Strong precedent for our "chemistry yields computation" framing, but not spatial in the same way and does not use folding-derived geometry to assemble programs.
- **Buliga — chemlambda / molecular computers**. Molecules as graphs of atoms and bonds, computation via local graph rewrites interpreted as chemical reactions. Close to our "chemistry rules assemble behavior" intuition, but the executable structure is already graph-like, whereas our system starts from a 1D sequence that must first acquire geometry through folding.

### Novelty Assessment

The general idea is not unprecedented; the nearest ancestor is Typogenetics. But the specific use of protein-like folding as a genotype-phenotype map that assembles runnable symbolic programs appears to be a novel combination. No prior system we found implements the full chain: string genome → fold into space → adjacency/bond rules → assembled executable symbolic program. The literature has pieces in separate traditions: folding and binding in artificial genetics (Typogenetics), chemistry as computation (AlChemy), local graph rewrites (chemlambda), digital organism dynamics (Avida).

### Positioning Summary

This project is closest to RNA-style genotype-phenotype map research and indirect/developmental encodings in evolutionary computation, with coevolutionary pressure borrowed from Hillis/Avida-style adversarial evolution. Its main novelty is replacing grammar or graph decoding with a protein-inspired fold-and-bond developmental process that assembles symbolic programs from local spatial interactions. The strongest comparison axes are:

| Result | Compare against |
|--------|----------------|
| Static metrics vs dynamic adaptation | RNA GP-map, robustness/evolvability theory |
| Direct vs indirect encoding | GE, CGP, developmental encoding surveys |
| Regime shift response | O'Neill GECCO 2011, Kashtan & Alon |
| Coevolution for escaping plateaus | Hillis, Zaman/Avida, Gupta |
| Complexity ceiling as map property | Lenski/Avida scaffolding, Zaman complexity trajectories |
| Fold-dependent program assembly | Typogenetics, AlChemy, chemlambda |

## Open Theoretical Questions

1. **Does constructional selection operate on genotype strings?** If motif enrichment is observed (Exp 3.1), it supports Altenberg's genome-as-population model applied to our linear genotype representation.

2. **Is there an optimal pleiotropy level?** Altenberg discusses the tradeoff but doesn't specify an optimum. Our system could sweep pleiotropy (by varying fold instruction density) and measure evolvability.

3. **Does the G-P map itself evolve?** If evolved genotypes have lower pleiotropy than random genotypes (Exp 3.2), evolution has shaped the map — not just the programs the map produces.

4. **Can rewriting create Type I constructional selection?** Phase 3 (genotype-level rewriting) would let programs edit each other's genotypes. If successful rewriters proliferate, this is constructional selection operating through program-on-program evolution.
