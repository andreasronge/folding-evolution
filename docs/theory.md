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

## Relevant Literature

### Direct References
- **Altenberg, L. (1995/2023)**. "Genome Growth and the Evolution of the Genotype-Phenotype Map." In *Evolution and Biocomputation*, Springer LNCS vol. 899, pp. 205-259. — The theoretical backbone.
- **Hillis, W.D. (1990)**. "Co-evolving parasites improve simulated evolution as an optimization procedure." — Parasitic coevolution for sorting networks.
- **Bonner, J.T. (1974)**. *On Development*. — Low pleiotropy principle.
- **Wagner, G.P. (1989)**. "The origin of morphological characters and the biological basis of homology." — Linear G-P map model.
- **Kauffman, S.A. (1989)**. "Adaptation on rugged fitness landscapes." — NK adaptive landscape model.

### Related Work (for context)
- **Developmental GP**: Genotype-phenotype mappings in GP (e.g., Banzhaf's linear GP, grammatical evolution). How does folding compare?
- **Cartesian GP (Miller)**: Another spatial encoding — genes have grid positions and connection rules. Shares the spatial adjacency idea.
- **Neutral networks (Kimura, Huynen)**: Theory of neutral evolution and how neutral mutations enable exploration of genotype space.
- **Punctuated equilibrium (Gould & Eldredge)**: Our fitness jumps in folding resemble punctuated dynamics — long stasis interrupted by rapid change.
- **Red Queen hypothesis**: Arms race dynamics in coevolution. Our coevolution designs are testing whether folding enables sustained Red Queen dynamics.

## Open Theoretical Questions

1. **Does constructional selection operate on genotype strings?** If motif enrichment is observed (Exp 3.1), it supports Altenberg's genome-as-population model applied to our linear genotype representation.

2. **Is there an optimal pleiotropy level?** Altenberg discusses the tradeoff but doesn't specify an optimum. Our system could sweep pleiotropy (by varying fold instruction density) and measure evolvability.

3. **Does the G-P map itself evolve?** If evolved genotypes have lower pleiotropy than random genotypes (Exp 3.2), evolution has shaped the map — not just the programs the map produces.

4. **Can rewriting create Type I constructional selection?** Phase 3 (genotype-level rewriting) would let programs edit each other's genotypes. If successful rewriters proliferate, this is constructional selection operating through program-on-program evolution.
