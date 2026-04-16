# Experimental Methodology — Cross-Cutting Lessons

**Scope.** Lessons distilled from the chem-tape v1 line (see [chem-tape/experiments.md](chem-tape/experiments.md) §1 through §v1.5a-internal-control). The learnings here are mostly representation-agnostic — they apply to the folding track ([folding/experiments.md](folding/experiments.md)), the CA track ([ca/experiments.md](ca/experiments.md)), and any v2 work. Saved as a durable reference alongside [theory.md](theory.md) and [coevolution.md](coevolution.md) so future experimental work doesn't re-learn the same lessons under time pressure.

Each principle is paired with the specific case that taught it and a one-line takeaway.

---

## Meta-principles (highest impact)

### 1. Internal controls before external validity

**Case.** §v1.5 + §v1.5a claimed cross-regime compatibility requires basin-width and scaffold-length match. The framework looked clean. §v1.5a-internal-control paired two tasks (`sum_gt_5`, `sum_gt_10`) that matched on basin, scaffold, input type, and slot bindings — and got 0/20 BOTH. Falsified the framework from *inside* the tested task family, cheaper and faster than alphabet expansion would have been.

**Takeaway.** The simplest possible within-family control comes first. If your framework survives the most tightly-matched internal contrast, then external validity tests are worth the cost. If it doesn't, you've caught the overreach for free.

### 2. Pre-register three or four outcomes, not pass/fail

**Case.** §v1.5's initial pre-registration had two outcomes ("cross-regime compatibility" vs "no compatibility"). The actual result (14/20 on has_upper, 6/20 on count_r, 0/20 on sum_gt_10, 0/20 all-three) fit neither. We had to reverse-engineer a third outcome ("canalized generalism") post-hoc. §v1.5a-internal-control was pre-registered with three outcomes (framework scales / partial / framework limited) — the falsification landed cleanly.

**Takeaway.** Enumerate three to four distinct outcome regimes with pre-committed interpretations *before* running the experiment. "Partial" and "swamped" are usually the overlooked categories.

### 3. Zero-compute inspection is routinely the highest-leverage next step

**Case.** §8a (inspect K=3 winners' architectures), §9d (inspect protection-specific winners), §11a (per-island fitness trajectories from existing NPZ files), §v1.5a-scaffold winner-architecture inspection. Each took ~30 minutes of analysis on already-on-disk data and produced mechanism-level findings worth more than any single additional sweep.

**Takeaway.** After a surprising or ambiguous result, default to "inspect before running another experiment." Existing run artifacts usually have more information than the solve-count summary exposes.

### 4. Identify degenerate successes

**Case.** §v1.5a-binary's 20/20 cross-task solve rate looked like strong evidence for body-level task plasticity. §v1.5a-internal-control revealed the 20/20 was specifically enabled by `slot_12` indirection — both tasks used the same body (INPUT CHARS MAP_* ANY); only slot_12's task-bound operator differed. Not body-level plasticity — task-level indirection absorbing regime variation.

**Takeaway.** Ask "what's the mechanism?" explicitly when a result is too clean (zero drop, 20/20, perfect symmetry). Real plasticity mechanisms rarely produce perfect signatures. Clean signatures often indicate a single structural lever doing all the work.

### 5. Framework refinement is a sequence of narrowings, not false→true flips

**Case.** The cross-regime-compatibility claim evolved as data accumulated:
- Initial: "basin width × scaffold length framework" (§v1.5 + §v1.5a)
- After §v1.5a-binary: "basin × scaffold × slot-indirection"
- After §v1.5a-internal-control: "body-invariant-route mechanism" (narrower, still positive)

Each refinement was driven by one specific experiment.

**Takeaway.** Treat claim scope as under active contest. Refinement is the default outcome, not the exception. Write claims with future-narrowing in mind.

---

## Methodology & statistics

### 6. Thresholds should be baseline-relative, not absolute

**Case.** An early draft of §v2.1's pre-registration said "alternation solve rate > v1's 7/20 indicates scaling." But v2's richer alphabet likely raises the fixed-task baseline to ~18/20, which makes "> 7/20" a trivial bar. The revision expressed thresholds as "≥ measured v2 fixed baseline − 1."

**Takeaway.** Anchor intervention thresholds to the measured fixed-task ceiling in the same experimental setup, not to numbers imported from prior experiments with different baselines.

### 7. Paired McNemar, not fixed-null p-values

**Case.** §9b's initial analysis reported p-values against a null `p = 0.3`. The "null" was hand-picked from historical baseline expectations, not the actual comparison. The honest test was paired McNemar on matched seeds between conditions — and it gave different (more conservative) p-values than the null-comparison did.

**Takeaway.** When comparing two conditions on shared seeds, use pairwise McNemar. Fixed-null p-values against historical means overstate significance and miss paired-seed structure.

### 8. Single-seed-half results need independent-seed confirmation

**Case.** §9b's "peak at r=0.5" at n=10 looked striking (6/10, novel seeds). §9c replicated on independent seeds (10-19) and the peak softened to a plateau. The r=0.3 "collapse" from §9b didn't replicate at all.

**Takeaway.** n=10 is for hypothesis generation. Load-bearing mechanism claims need n=20+ on disjoint seed sets before they enter summary bullets.

### 9. Selection-regime changes are not additive

**Case.** §4 showed islands help A/B/BP. §9b showed r=0.5 helps K=3. §11 tested their combination: r=0.5 × islands collapsed to 5/20 — Arm A baseline. The interventions were substitutes (both reduce exploration pressure), and applied together they starved the search.

**Takeaway.** Factor-cross before claiming orthogonality. "Both interventions help independently, so combining them should help more" is a prior that's wrong surprisingly often in evolutionary-GA experiments.

### 10. Aggregate metrics hide mechanism; per-subgroup diagnostics distinguish hypotheses

**Case.** §11's K=3 r=0.5 islands failure had three plausible explanations (diversity collapse / migration disruption / per-island scale). Aggregate fitness trajectories couldn't distinguish them. §11a re-ran with per-island logging and cleanly ruled out diversity collapse and migration disruption — ruled in per-island-selection-scale.

**Takeaway.** When a result has multiple mechanism candidates, add per-subgroup logging (per-island, per-K-value, per-task) and re-run a small diagnostic sweep before claiming a mechanism.

---

## Design & implementation

### 11. Hash-stable config extensions preserve cached results across experiments

**Case.** Adding `topk`, `bond_protection_ratio`, `k_alternating_*`, `evolve_k_*`, `task_alternating_*`, and `alphabet` all happened incrementally. Each new field was excluded from `ChemTapeConfig.hash()` at its default value. Result: v1 cached sweep directories remained addressable as v2 fields were added, saving multiple hours of recompute.

**Takeaway.** Any new config field gets `if <field> == <default>: d.pop(<field>)` in the hash function. Default to backward-compatible extension.

### 12. Commit hashes in findings are non-negotiable

**Case.** Several times during the v1 line we re-examined surprising findings and needed to reconstruct exactly the code state that produced them. The project's "include git commit hash" rule (per [CLAUDE.md](../CLAUDE.md)) let this work every time.

**Takeaway.** Results without commit hashes are a liability. Anchor every reported finding to a specific commit, even for transient "I'll rerun this later" data.

### 13. Retract overreach explicitly in the doc, don't silently remove

**Case.** Across §v1.5 → §v1.5a-binary → §v1.5a-internal-control, the mechanism claim was narrowed twice. Each narrowing kept the superseded framing in place with explicit "superseded by §X" annotation, rather than deleting it. Future readers can trace *why* a claim narrowed, which is itself information.

**Takeaway.** When a later experiment falsifies an earlier claim, rewrite the earlier claim's section with an explicit supersession marker, not a silent deletion. The reasoning trail is a feature.

---

## Chem-tape mechanism lessons that generalize

### 14. Environmental forcing > internal encoding for plasticity-like behaviors

**Case.** §10 (external K alternation) and §v1.5a-binary (external task alternation absorbed by slot indirection) both produced positive cross-regime compatibility. §12 through §12c (genotype-encoded K evolution under four different selection regimes) all produced firm nulls.

**Takeaway.** If you want cross-regime-compatible bodies, force the environment to vary and let selection find the bodies. Encoding the variation-axis into the genotype and selecting for fitness under one regime at a time drives homogenization, not plasticity.

### 15. "Hard floor" seeds are debugging anchors

**Case.** Across all chem-tape sweeps on sum-gt-10 — every arm, every selection regime, every mechanism variant — seeds {4, 11, 17} remained unsolved. They're a representational blind spot that mechanism variation can't reach.

**Takeaway.** Track which seeds are *never* solved, not just which are solved most. Persistently-unsolved seeds are candidates for direct genotype inspection, and their common structure (if any) often points at what the representation genuinely cannot express.

### 16. The mechanism is usually narrower than the first-pass name for it

**Case.** "Decode breadth" → "quarantine via exclusion" → "body-invariant route." Each renaming was driven by an experiment revealing that the earlier name was a correlate, not the mechanism.

**Takeaway.** First-pass mechanism names are correlates. The actual mechanism usually sits one level deeper. Treat the name as a working hypothesis and budget for at least one renaming cycle.

### 16b. Sometimes the mechanism name needs to be *broader*, not narrower

**Case.** §v2.4's "max > 5 proxy attractor" renamed to "single-predicate proxy basin attractor" after §v2.4-proxy showed that under decorrelation, evolution shifts from `max > 5` to `sum > 10` (whichever single-predicate is the next-most-accurate ≥ ~0.9 proxy on the current training distribution). The first-pass name was too specific; the mechanism is broader than the original predicate.

**Takeaway.** Renaming can go in either direction. If an experiment shows the mechanism generalises beyond the original predicate/regime (not just narrows away from it), the rename is *broader*. The skill's log-result mode should prompt for both directions — "is the mechanism narrower than this claim?" and "is the mechanism broader than this specific predicate/condition?"

---

## Process

### 17. Analyst reviews catch specific overreach patterns

**Case.** Recurrent reviewer pushback targeted the same phrasings: "universal ceiling," "framework confirmed," "established mechanism," "the X axis." Each time these needed softening to scope-qualified variants.

**Takeaway.** These phrases are predictable tells of overreach. Before publishing a claim, search the draft for them and ask whether each is scope-qualified or naked-universal.

### 18. Scope tags in summary bullets prevent silent generalization

**Case.** Summary bullets in [chem-tape/experiments.md](chem-tape/experiments.md) are explicitly tagged "within-family exploratory" or "n=20 exploratory." Without those tags, within-family findings would have propagated to paper-level narrative before external-validity tests caught up.

**Takeaway.** Every summary-level claim gets a scope tag. "Within-family," "n=20," "at K=3 r=0.5," "on sum-gt-10-adjacent tasks" — whatever the actual scope was. Tags age well; naked claims age badly.

### 19. The review loop is load-bearing

**Case.** Multiple specific reviewer corrections visibly reshaped the chem-tape line: the McNemar framing (§9c), the mechanism-framing narrowing from "basin × scaffold" to "body-invariant-route" (post-§v1.5a-internal-control), the v2-probe pre-registration tightening, and the overfitting concern that drove §v1.5a-internal-control itself. Each of these review cycles caught an overreach *before* it propagated to downstream experiments.

**Takeaway.** Schedule explicit review checkpoints at natural narrative breakpoints, not just at the end. Each accepted result is a commitment to downstream experiments that will build on it; pay to catch the overreach at the point of commitment, not after.

---

## How to use this document

This isn't a checklist — it's a lessons ledger. Suggested usage:

- **Before pre-registering an experiment:** read principles 1-4 and 6. If the prereg changes the training distribution, also read 20. If the sweep's test will enter a family of related tests, read 22.
- **After a surprising result:** read 3, 10, 14, 16, 16b, 21.
- **Before writing a chronicle:** read 23 — verify every pre-registered outcome row and plan-part was actually executed, or explicitly deferred.
- **When writing a summary bullet:** read 18.
- **When reviewing your own claim language:** read 17.
- **When adding a new config parameter:** read 11.
- **When a previous claim needs revising:** read 13.
- **When a result clusters near a pre-registered threshold (1/20, 3/20, etc.):** read 21 — attractor-category inspection is required, not optional.
- **When a FAIL or INCONCLUSIVE result is load-bearing for scope:** read 24 — null results get their own findings.md entry, not just a chronicle paragraph.

If a future experiment contributes a new lesson worth adding, update this document with a new case + takeaway pair. The point is to avoid re-learning.

---

## Design discipline (added 2026-04-15 from §v2.4-proxy experience)

### 20. Sampler design is a first-class experimental axis

**Case.** The §v2.4-proxy design went through three revisions before the sweep ran: (a) the original doc-draft ("change input range from [0,9] to [0,5]") would have collapsed the AND label to constant-False under the natural sampler — no positives exist. (b) A hybrid "positives from [0,9], negatives from [0,5]" made `max > 5` a **perfect** classifier (worse than the original). (c) A 3-way stratified sampler enforcing P(max>5|+)=1.0 and P(max>5|−)=0.5 achieved the intended ~0.75 proxy accuracy while preserving AND structure in training data. Only (c) was the correct design, and it was identified during scaffolding — not in the original pre-reg. An un-audited (a)/(b) run would have produced uninterpretable data.

**Takeaway.** When a pre-reg changes the **training distribution** (not just hyperparameters or seeds), the degenerate-success guard must include: *(i)* "does the label function remain learnable under the new sampler?" *(ii)* "what does the primary proxy predictor score on the new sampler?" *(iii)* "does the new sampler preserve class balance?" The prereg should report these numbers *before* the sweep runs, on representative seeds. Sampler design deserves the same rigor as fixed-task baselines — the prereg's Gate 3 (degenerate-success) and Gate 6 (baseline-relative thresholds) both apply. Treat the sampler as a dependent-variable carrier, not a neutral backdrop.

### 21. Attractor-category classification is the minimum inspection commitment for any "too clean" OR "near the threshold" outcome

**Case.** §v2.4's 0/20 was initially explained as "refinement bottleneck under 4× compute" based on the 0.859–0.969 baseline fitness distribution. Direct genotype inspection then revealed the `max > 5` attractor (14/20 seeds exactly the same predicate), and the refinement-bottleneck framing was falsified. §v2.4-alt / §v2.4-proxy / §v2.6 all ran genotype-inspection on the best-of-run winners as a standing commitment, and every chronicle interpretation turned on what the classifier showed (same attractor vs new attractor vs distinct assembly).

**Takeaway.** Zero-compute genotype inspection (methodology principle 3) is not optional for load-bearing chronicle entries — it's the difference between "we measured solve count" and "we understand what evolution is doing." Build or maintain a project-local classifier (`experiments/chem_tape/decode_winner.py` for chem-tape) that tags each winner with an attractor category, and run it on every n=20 sweep's winners before writing the interpretation. The classifier should be updated as new attractor categories emerge — it's a growing vocabulary, not a fixed taxonomy.

## Scientific rigor (added 2026-04-16 from project audit)

### 22. Family-wise error rate correction across the sweep portfolio

**Case.** As of 2026-04-16 the chem-tape v2 line had ~16 active §v2.* experiments, each running ≥1 statistical test (paired McNemar, holdout gaps, baseline-vs-intervention solve counts). At α=0.05 per test, the expected false-positive count across the suite is ~0.8 — a coin-flip probability of at least one unearned significant result. No family-wise correction was applied; each test stood alone. Paper-level claims that aggregate across sweeps ("constant-slot-indirection robustly scales across N conditions," "proxy-basin attractor appears under M decorrelation regimes") would overstate significance under uncorrected inference. Principle 7 fixed the *pairing* problem for a single test; this principle fixes the *multiplicity* problem across tests.

**Takeaway.** Treat the active sweep portfolio as a test family. At pre-registration time, classify each planned test as either **confirmatory** (enters the FWER family with Bonferroni α = 0.05 / n_family_tests) or **exploratory** (reported as effect size only, no p-value gate). At promotion time, if a finding rests on multiple tests, compute the corrected α before the chronicler step and include it in the findings.md scope block. Individual exploratory p-values remain fine for hypothesis generation; family-level claims need family-level correction. An `fwer-audit` mode on the research-rigor skill should count outstanding confirmatory tests in queue.yaml and surface the corrected α in the morning digest.

### 23. Pre-registration execution fidelity

**Case.** §v2.6's prereg included a fixed-task baseline sweep that was not executed in the initial session — only the three alternation sweeps ran. The provisional interpretation was corrected in a later commit (`344e4de`) when the baseline was completed and narrowed the claim from "4 pairs" to "1 pair." The research-rigor skill gated *commitment before a run* but had no gate for "did every pre-registered part of the plan actually execute?" This is the **skipped-but-rationalized** pattern: an honest deferral can look identical to a post-hoc redesign from the commit log. The prereg-time gates catch overreach in design; the chronicle-time gate catches overreach in execution.

**Takeaway.** At chronicle time, before writing interpretation, explicitly verify: *(i)* every outcome row in the prereg was tested (none silently added, none silently removed), *(ii)* every part of the plan (Part A baseline, Part B main, etc.) was completed or explicitly deferred with date and reason, *(iii)* if any parameter or sampler was changed mid-run, the new plan was re-pre-registered in a separate commit before interpretation. Add this checklist as a mandatory block to the chronicle template, and enforce it in the research-rigor skill's `log-result` mode. Partial execution is acceptable; silent partial execution is not.

### 24. Null results deserve first-class findings.md entries

**Case.** As of 2026-04-16, findings.md held 4 positive entries and 1 narrowed entry. The major FAIL / INCONCLUSIVE results — §v2.6 (0/3 pairs scale beyond Pair 1), §v2.7 (CONTROL-DEGENERATE), §v2.4-proxy-3 (INCONCLUSIVE split-halves), §v2.12 (FAIL decoder-general) — lived only in experiments-v2.md. A reader scanning findings.md saw the scope where interventions worked but not the matched scope where they didn't. This asymmetry risks paper-level aggregation that cites positive findings against under-weighted nulls, and undercuts principle 13's supersession trail by hiding falsifications in the chronicle layer instead of the claim layer.

**Takeaway.** Promote major FAIL / INCONCLUSIVE results as first-class findings.md entries using the same template as positive findings — status token `FALSIFIED` or `NULL` in the header, scope tag documenting *where the claim does not hold*, supporting-experiments table with commit hashes of the falsification evidence, and a downstream-commitments line documenting what future work should *not* assume. "This doesn't work under X" is a finding. Positive and negative findings belong on equal documentary footing; the research-rigor skill's `promote-finding` mode should accept FAIL/NULL status tokens, not only PASS.

---

## References

- [chem-tape/experiments.md](chem-tape/experiments.md) — v1 experimental record (primary source for most cases).
- [chem-tape/experiments-v2.md](chem-tape/experiments-v2.md) — pre-registered v2-probe suite (applies these lessons).
- [theory.md](theory.md) — Altenberg's constructional selection framework (theoretical frame).
- [CLAUDE.md](../CLAUDE.md) — project-level design principles (includes "commit hash in findings" mandate).
