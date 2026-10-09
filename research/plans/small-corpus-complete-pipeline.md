# Can a small exact-source budget acquire the complete useful bias?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 1743](../runs/2026-10-09-1743/strategy.md). This is a direction
and cost plan; the steward supplies the proposal, fixed size and decision rule.

**Question.** Does rebuilding both the context decoder and fragment repertoire from
a small, fixed allocation of source searches retain enough fresh-search performance
to be preferable to the full-corpus procedure at a useful reuse cost? If the cheaper
decoder works, does carrying its fragment library still add anything over its own
chain blocks? This chooses an acquisition target, rather than another operator detail.

Exact-source fitting is the successful procedure. The failed pre-solve fragment test
changed only F's source while retaining the expensive exact-source C. It therefore did
not answer this complete-pipeline question. The libraries' recurring short syntax
suggests possible redundancy, but there is no evidence yet that a small corpus can
teach C, or that a small library helps. This is external acquisition from evolved
programs, not selection or inheritance of decoder parameters.

**One bounded source policy.** Use the first **four attempts per training cell** in
each of 1246's sixteen frozen collection schedules, retaining failures. Each attempt
has the existing 524,288-evaluation cap. This allocates 2,097,152 evaluations per cell,
the same ceiling as 1831's 32 short attempts at 65,536. It is not four successful
solvers, and there is no collection-until-success rule or search over corpus sizes.
The source policy was chosen from that allocation arithmetic before inspecting its
yield. A [read-only audit](../runs/2026-10-09-1743/source-cost-audit.json) found 150
solvers in 256 attempts, with four empty cells in four different corpora. All sixteen
corpora remain in the comparison. These inspected sources are development material.

Reconstruct this prefix from the saved schedule and collection rows, not file arrival
order or a sorted list of successful tapes. Validate unique attempt keys, source-table
hashes, exact solver labels and failure records. No unused source tape, full-corpus
transition count, library or fitted C may enter the cheaper method. Reusing saved
attempts avoids executing them again; charge their original cost to acquisition.

**What to build.** Reuse the reviewed `research/main` implementations of
`solver_corpus_fit.py`, `fragment_library.py`, `fragment_operator.py` and
`fragment_reuse_run.py`, with 1246's source records and 1036's frozen reference
artifacts. Those runners are absent from the current `main` checkout; do not recreate
the harness. Keep D1331 length-three inputs, `v2_rmin_first`, G4, 32-token tapes,
selection, ordinary variation and exact verification unchanged.

Fit C4 only to prefix solvers, preserving equal cell mass (1,600), full-tape treatment,
alpha 50 and support. The existing fitter raises on an empty cell. Add an explicit
fallback: that cell contributes the analytically expected transition counts of
length-32 G4 tapes, normalized to the same cell mass. Other cells retain the existing
normalization. This supplies no learned information from the omitted attempts. Check
that nonempty inputs reproduce the legacy estimator and an all-empty source recovers
the G4 law within quantization tolerance. Record fallback frequency; never drop those
corpora or replenish their sources. Do not tune shrinkage to compensate for the prefix.

Extract F4 from exactly those same prefix solvers with the existing all-active
3–6-token windows, recurrence across at least two source cells, ranking and exclusion
of padded complete training solvers. Keep at most 32 entries; smaller libraries are
valid. Do not force a full library by relaxing recurrence or importing known `gt`
fragments. For an empty library use C4-chain blocks with a fixed uniform 3–6 span law;
the matched chain control uses that same law. Validate this fallback, since the current
operator rejects empty libraries. Report retained sizes and provenance.

Use the existing suffix-preserving block path for both F4 and W4. W4 draws from C4
and matches F4's length/start/rate law; it must not borrow the full library's law.
Question 34 supplies no reason to add another W/R comparison, and retaining the
reviewed path keeps the source intervention narrow.

**First experiment.** Score complete C4+F4 against full-corpus C+F on the complete
then-addition development roster, with C4+W4 as the simpler cheap procedure and G4 as
the no-acquisition reference. Reuse historical full-C+F and G4 rows only with validated
provenance and appropriate seed matching; otherwise include rescoring in the price.
Different decoders intentionally induce different starting programs. Within C4+F4
versus C4+W4, initial programs must match. No source program itself enters evaluation.

The primary comparison asks how much search performance the complete cheap pipeline
retains relative to the full one. The steward should choose a worthwhile tolerated
loss and fixed size that can distinguish retention from collapse; a 20% cost increase
is a candidate resolution, not an established acceptable economic loss. Keep the
G4 and W4 comparisons visible so similarity between ineffective methods cannot pass
as practical success. Preserve source-corpus uncertainty, both families, individual
cells, solve rates, cap sensitivity and an explicit unresolved outcome. More scoring
seeds cannot eliminate between-corpus variability. No T/K/B matrix is needed to choose
between these complete procedures; without it, do not attribute a gain specifically
to context or fragment dependencies.

Report total cost curves A + N*S using arithmetic mean acquisition cost A and fresh
search cost S in consistent units, including failures, verification, fitting and
extraction. Show uncertainty and the crossover against both G4 and full C+F; do not
assume an owner reuse horizon or derive repayment from geometric speed ratios.
The shared corpus is charged once to C+F, not twice or solely against F/W's increment.
Report capped reliability alongside cost: capped effort is not expected uncapped
time to solve. There is no demonstrated break-even when savings are nonpositive.

**Complete cost and exit.** One experiment, **7–10 hours total**, including at most
two hours preparation, roughly 2–4 hours queue work, reviews, analysis and contingency;
**six hours maximum summed queue timeouts**, further reduced against the actual
2026-10-10 08:12 deadline. The source audit measured 3,842 search worker-seconds for
the prefixes versus 48,039 for the full sources, before separate fitting/extraction
charges. These are acquisition prices, not sparse-decoder scoring rates.

For pricing, sixteen corpora × sixteen cells × eight seeds × two new procedures is
4,096 searches. The 1350 two-arm queue ran 8,192 searches in 84 minutes under full C;
the weaker partial fits in 1831 took roughly two hours for 5,120 evaluation searches
plus collection. Sparse C4 may be slower and more variable than either. Measure its
roster-weighted rate at intended concurrency, price reference replay/rescoring and
adequate precision, and freeze the substantive size before efficacy scoring. Eight
seeds is a costing example, not a statistical prescription. A probe-only fallback
must obey the separate 60-minute timeout limit and price confirmation within the
remaining window; feasibility alone does not earn another slot.

Return to strategy after the result or a measured build, validity or full-cost
obstacle. Useful retention with much lower acquisition cost earns consideration of
this source policy. Useful W4 without a worthwhile F4 increment favors acquiring the
decoder alone. A tight loss ends this four-attempt procedure; broad uncertainty needs
a resolution price. No automatic larger prefix, alternate smoothing, fresh bank or
online library engine follows. The result is conditional data-efficiency evidence on
reused sources and tasks, not fresh acquisition replication or inherited map evolution.

The current fragment line is closest to [Keijzer, Ryan and Cattolico, *Run Transferable
Libraries* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
[Ellis et al., *DreamCoder* (PLDI 2021)](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf)
jointly learns a library and search policy. These papers motivate evaluating all
acquired components together; neither establishes sample efficiency for our literal
windows, nor is this a reproduction of their algorithms.
