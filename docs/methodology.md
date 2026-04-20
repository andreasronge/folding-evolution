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

### 2b. Outcome tables are grids, not paired rows, when you measure ≥2 axes

**Case.** §v2.4-proxy-4b (2026-04-17) pre-registered a seeded-init probe measuring two axes: F (best-of-run solve rate) and R (full-population canonical retention). The outcome table encoded PASS as "F high AND R ≥ 0.3," PARTIAL as "F high AND R ≥ 0.05," FAIL as "F low." The rows silently assumed F and R would move together (a discoverability-limited mechanism prior: "if selection can reach canonical, it will propagate"). The actual result was (F=20/20, R_exact ≤ 0.036) — F maxed, R below even the PARTIAL floor. No row covered this cell. The overnight write-up initially labeled it PASS; the revision re-read it as INCONCLUSIVE per principle 2 outcome-table incompleteness, and the mechanism narrowed from "pure discoverability-limited" to "best-of-run canonical attractor without population propagation."

**Takeaway.** When a prereg measures two or more independent axes, the outcome table is the **cross-product grid** of those axes' coarse bins, not a stack of paired rows. Every cell needs an assigned outcome token — including the ones you expect not to hit. If you find yourself writing rows where both axes move together, stop and ask whether you are measuring one quantity or two: correlated rows silently smuggle a mechanism hypothesis into what is supposed to be an outcome-space enumeration, and the "impossible" cell is where a falsifying result most often lands. A cleanly enumerated grid has a separate entry for every (A_high, A_low) × (B_high, B_mid, B_low) combination, or an explicit `IMPOSSIBLE/INCONCLUSIVE` token where a cell is genuinely excluded by physics.

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

### 16c. Tentative mechanism names need falsifiable predictions

**Case.** §v2.4-proxy-5a-followup-mid-bp's chronicle introduced the tentative name "non-monotone single-mechanism cloud-destabilisation" under the §16 renaming cycle. Codex pass 2 flagged the name as too residual: it could survive any further data by attaching qualifiers ("under low BP_TOPK," "at specific budgets," etc.) without progressing the mechanism understanding. Post-codex, five pre-committed falsifiable predictions (P-1..P-5) were added, each tied to a specific pending or upcoming test that would force a rename if violated. The rescue was ad hoc — it should have been the standard pattern, not a reaction to review.

**Takeaway.** When a chronicle commits to a tentative mechanism name (per the renaming cycle anticipated by §16), the chronicle must pre-commit at least **three falsifiable predictions**, each of which if violated would force a rename. Each prediction names the specific experiment that would test it — pending experiments are acceptable, unnamed experiments are not. Names without falsifiers are just-so stories: they survive any further data by qualifier-attachment and consume the §16 renaming budget without progress. The chronicle template (`docs/_templates/experiment_section.md`) enforces this via a mandatory falsifiability block whenever a mechanism-name rename is proposed.

> See [Plans/methodology_improvements_2026-04-18.md](../Plans/methodology_improvements_2026-04-18.md) for the drafting rationale behind sub-principle 16c (added 2026-04-18).

---

## Process

### 17. Analyst reviews catch specific overreach patterns

**Case.** Recurrent reviewer pushback targeted the same phrasings: "universal ceiling," "framework confirmed," "established mechanism," "the X axis." Each time these needed softening to scope-qualified variants.

**Takeaway.** These phrases are predictable tells of overreach. Before publishing a claim, search the draft for them and ask whether each is scope-qualified or naked-universal.

### 17a. Multi-variable confounds in "decoupling" claims

**Case.** §v2.4-proxy-5b-crosstask's earlier draft proposed `mr=0.005 × gens=9000` as "budget-decoupling" from `mr=0.03 × gens=1500`. Codex noted that varying `mr` and `gens` jointly changes at least four derived process variables — (a) per-tape expected mutation count, (b) selection opportunities per lineage, (c) crossover opportunities, (d) fixation time — not two. Calling the outcome "rate-vs-budget decoupling" was overreach; the true discrimination was narrower than the nominal variable names suggested.

**Takeaway.** When a prereg varies a nominal config field across cells, explicitly enumerate every derived process variable that changes across those cells *at prereg time*. If more than one derived variable shifts, the outcome discrimination is narrower than the nominal variable would suggest: the prereg's outcome rows must name the process-variable-bundle being discriminated, not the nominal field. "Rate vs. budget" silently smuggles a two-variable assumption into what is actually a multi-variable contrast; the naming must reflect the bundle.

### 17b. Tested-set vs continuous-range smuggling in mechanism-name qualifiers

**Case.** The 2026-04-18 `findings.md#proxy-basin-attractor` ACTIVE status line initially read: mechanism narrowed to "monotone single-mechanism cloud-destabilisation under BP_TOPK preserve **at selection pressure ≥ tournament_size=3**." The `≥ 3` half-line extrapolated from discrete tested values ts ∈ {3, 5, 8}. All four F1 confirmatory tests ran only at ts=3; ts ∈ {5, 8} was exploratory; ts > 8 was entirely untested. Codex pass 2 flagged this as mechanism-name smuggling: a tested set gets promoted into an untested half-line. Fixed at commit `1165f88` to "at tested tournament sizes ∈ {3, 5, 8} (ts=2 fails; ts > 8 untested)."

**Takeaway.** When a mechanism-name qualifier names a threshold or range on a variable that was tested only at discrete values, the qualifier must scope to the tested set explicitly, not to a continuous range above or below a tested endpoint. "At tested values ∈ {X, Y, Z}" is honest; "at ≥ X" smuggles untested values between tested points and extrapolates beyond the tested maximum. This applies especially to integer-valued config fields (`tournament_size`, `topk`, `budget`, etc.) where between-tested-values are excluded by config type, and to any qualifier that upgrades exploratory evidence into ACTIVE-claim scope — tested-set discreteness must survive that upgrade.

> See [Plans/methodology_improvements_2026-04-18.md](../Plans/methodology_improvements_2026-04-18.md) for the drafting rationale behind sub-principles 17a and 17b (added 2026-04-18).

### 18. Scope tags in summary bullets prevent silent generalization

**Case.** Summary bullets in [chem-tape/experiments.md](chem-tape/experiments.md) are explicitly tagged "within-family exploratory" or "n=20 exploratory." Without those tags, within-family findings would have propagated to paper-level narrative before external-validity tests caught up.

**Takeaway.** Every summary-level claim gets a scope tag. "Within-family," "n=20," "at K=3 r=0.5," "on sum-gt-10-adjacent tasks" — whatever the actual scope was. Tags age well; naked claims age badly.

### 19. The review loop is load-bearing

**Case.** Multiple specific reviewer corrections visibly reshaped the chem-tape line: the McNemar framing (§9c), the mechanism-framing narrowing from "basin × scaffold" to "body-invariant-route" (post-§v1.5a-internal-control), the v2-probe pre-registration tightening, and the overfitting concern that drove §v1.5a-internal-control itself. Each of these review cycles caught an overreach *before* it propagated to downstream experiments.

**Takeaway.** Schedule explicit review checkpoints at natural narrative breakpoints, not just at the end. Each accepted result is a commitment to downstream experiments that will build on it; pay to catch the overreach at the point of commitment, not after.

---

## How to use this document

This isn't a checklist — it's a lessons ledger. Suggested usage:

- **Before pre-registering an experiment:** read principles 1-4 and 6. If the prereg measures ≥2 independent outcome axes (e.g., solve-rate AND retention), also read 2b — the outcome table is a grid, not paired rows. **If the prereg measures any axis at per-seed resolution (including axes labeled diagnostic), also read 26 — diagnostic axes still get coarse-bin outcome grid rows.** For every metric the prereg commits to, read 25 — verify both the producing code and (if the prereg commits to a per-cell breakdown) the grouping wrapper covering the prereg's axis set actually exist — and read 27 — cite the producing module's `METRIC_DEFINITIONS` entry verbatim. **For every row clause whose satisfaction gates an escalation path with material consequences, read 25b (routing-critical metric discipline — occupancy guard, CI bound, or chronicle-time demotion; plain cell-means fail the gate) and 25c (single-purpose clause discipline — a clause cannot be both a routing gate and a mechanism discriminator when the discriminator's distribution is uncertain).** If the prereg changes the training distribution, also read 20. If the sweep's test will enter a family of related tests, read 22 (FWER basics), 22a (per-sweep counting convention), and 22b (chronicle-vs-audit authority when counts disagree).
- **After a surprising result:** read 3, 10, 14, 16, 16b, 16c (tentative mechanism names need falsifiable predictions), 21. If the result doesn't match any pre-registered outcome row, also read 2b — the outcome table was probably missing the cell you landed in.
- **Before writing a chronicle:** read 23 (execution fidelity — every pre-registered outcome row and plan-part executed or explicitly deferred) and 28 (letter-vs-intent drift at row-match, degenerate-success-guard, and status-line surfaces). If the observed result is close to a pre-registered row's prose but fails a numeric clause, 28a applies; if a degenerate-success guard letter-passes on a multi-mode regime, 28b; if the body qualifies the headline verdict, 28c.
- **When writing a summary bullet:** read 18.
- **When reviewing your own claim language:** read 17 (overreach phrases), 17a (multi-variable confounds in "decoupling" claims), and 17b (tested-set vs continuous-range qualifiers on mechanism names).
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

### 22a. Per-sweep counting convention

**Case.** The 2026-04-17 FWER audit (`Plans/fwer_audit_2026-04-17.md`) under-counted the F1 proxy-basin family by two tests. It treated §v2.4-proxy-4c-replication as zero contributions (omitted) even though the chronicle explicitly counted its Arm A preserve + BP_TOPK consume sweeps as two separate McNemar tests. The 2026-04-18 first-draft audit also miscounted (treated 4c as 1 test, not 2). Both errors flowed from the same gap: §22 as originally written didn't state explicitly that a single prereg driving multiple independent sweeps contributes one family member per sweep.

**Takeaway.** When a prereg produces multiple independent statistical tests — e.g., one paired McNemar per sweep across different arms, decoders, tasks, or seed blocks — each test is a separate family member, not one collective test under the prereg's umbrella. The prereg must state its per-sweep test count explicitly in the confirmatory/exploratory classification block; multi-sweep preregs that omit this count state their classification as **ambiguous** until amended. At audit time, enumerate tests per sweep, not per prereg.

### 22b. Authoritative-source rule (chronicle vs. audit, with carve-out for chronicle-layer errors)

**Case.** The 2026-04-17 audit (above) disagreed with the source chronicle's per-sweep count. No methodology rule existed to break the tie; the audit and the chronicle each could plausibly claim primacy. An "audit always wins" rule would lock in any audit-layer miscount (as happened in the 2026-04-18 first-draft audit). A "chronicle always wins" rule would lock in any chronicle-layer bookkeeping error. Neither is safe by default.

**Takeaway.** When an audit's family-member count disagrees with the source chronicle's FWER bookkeeping, the chronicle is the default authority *provided its bookkeeping appeals to standard Bonferroni conventions and is internally consistent*. When the audit identifies a specific chronicle-layer error — overcount, misclassification of exploratory-as-confirmatory, non-standard counting convention — the audit's role is to surface the contestation for explicit resolution, not to defer automatically. Resolution requires either (i) a chronicle amendment (§13 supersession if load-bearing) or (ii) an explicit audit-layer override documented with the contested count's grounding. Silent audit-deferral and silent chronicle-override both fail this gate.

**Membership-at-commit-time (2026-04-18 clarification).** Confirmatory family membership is determined at prereg-commit time, not at result-rejection time. A confirmatory test that runs counts in the family regardless of rejection outcome: a FAIL-TO-REPLICATE confirmatory test consumed α budget and remains a family member; its null finding is recorded under §24 but does not remove the test from the family. The family's corrected α tightens whenever a new confirmatory test is registered.

> See [Plans/methodology_improvements_2026-04-18.md](../Plans/methodology_improvements_2026-04-18.md) for the drafting rationale behind sub-principles 22a, 22b, and the commit-time-membership clarification (added 2026-04-18).

### 23. Pre-registration execution fidelity

**Case.** §v2.6's prereg included a fixed-task baseline sweep that was not executed in the initial session — only the three alternation sweeps ran. The provisional interpretation was corrected in a later commit (`344e4de`) when the baseline was completed and narrowed the claim from "4 pairs" to "1 pair." The research-rigor skill gated *commitment before a run* but had no gate for "did every pre-registered part of the plan actually execute?" This is the **skipped-but-rationalized** pattern: an honest deferral can look identical to a post-hoc redesign from the commit log. The prereg-time gates catch overreach in design; the chronicle-time gate catches overreach in execution.

**Takeaway.** At chronicle time, before writing interpretation, explicitly verify: *(i)* every outcome row in the prereg was tested (none silently added, none silently removed), *(ii)* every part of the plan (Part A baseline, Part B main, etc.) was completed or explicitly deferred with date and reason, *(iii)* if any parameter or sampler was changed mid-run, the new plan was re-pre-registered in a separate commit before interpretation. Add this checklist as a mandatory block to the chronicle template, and enforce it in the research-rigor skill's `log-result` mode. Partial execution is acceptable; silent partial execution is not.

### 24. Null results deserve first-class findings.md entries

**Case.** As of 2026-04-16, findings.md held 4 positive entries and 1 narrowed entry. The major FAIL / INCONCLUSIVE results — §v2.6 (0/3 pairs scale beyond Pair 1), §v2.7 (CONTROL-DEGENERATE), §v2.4-proxy-3 (INCONCLUSIVE split-halves), §v2.12 (FAIL decoder-general) — lived only in experiments-v2.md. A reader scanning findings.md saw the scope where interventions worked but not the matched scope where they didn't. This asymmetry risks paper-level aggregation that cites positive findings against under-weighted nulls, and undercuts principle 13's supersession trail by hiding falsifications in the chronicle layer instead of the claim layer.

**Takeaway.** Promote major FAIL / INCONCLUSIVE results as first-class findings.md entries using the same template as positive findings — status token `FALSIFIED` or `NULL` in the header, scope tag documenting *where the claim does not hold*, supporting-experiments table with commit hashes of the falsification evidence, and a downstream-commitments line documenting what future work should *not* assume. "This doesn't work under X" is a finding. Positive and negative findings belong on equal documentary footing; the research-rigor skill's `promote-finding` mode should accept FAIL/NULL status tokens, not only PASS.

## Measurement fidelity (added 2026-04-17 from §v2.4-proxy-4b experience)

### 25. Measurement-infrastructure gate: a metric is only as real as the code that produces it

**Case.** §v2.4-proxy-4b's prereg committed `R_2` as "full-population retention at edit-distance ≤ 2 from canonical." But `sweep.py` serializes only per-generation aggregate stats to `history.npz` — it does not dump final populations. When the chronicle was written, the actually-reportable quantity was an **exact-match upper bound** on R inferred indirectly from `mean_fitness=0.845` and `unique_genotypes=987/1024`, giving `R_exact ≤ 0.036`. The prereg's nominal edit-distance-2 metric was unmeasured and remains unmeasured. The initial overnight write-up reported the bound as if it satisfied the prereg; the revision had to explicitly label the reading as a bound-from-aggregate-stats and mark the prereg's actual R_2 as "pending a `sweep.py dump_final_population` extension." The misclassification was not a scope-tag issue (principle 17) or an execution-fidelity issue (principle 23) but a **metric-fidelity** issue — the code that produces the committed metric did not exist at prereg time, and nobody checked.

**Takeaway.** Before a prereg commits to a metric, verify the infrastructure can actually produce it at the committed resolution. Every metric named in the prereg must record one of three states: *(i)* **produced directly** — name the file, column, or routine that emits the metric (e.g., "`history.npz:final_pop_exact_match` emitted by `sweep.py:dump_final_population=True`"); *(ii)* **produced as an explicitly-labeled bound or proxy** — name the proxy, the direction of the bound, and why the bound is informative (e.g., "R_exact ≤ (pop − unique_genotypes)/pop is an *upper* bound; a low value is conclusive, a high value is not"); *(iii)* **pending an infra extension** — name the extension, rough effort estimate, and commit to either completing it before the sweep or re-scoping the prereg's metric to what the current code can emit. A prereg that names a metric whose producing code does not exist, without one of these three labels, fails this gate. The check is cheap at prereg time (5 minutes of grep); silent reinterpretation at chronicle time is expensive — either the sweep has to be rerun, or the claim has to be weakened, and both carry review-cost that the prereg exists to prevent.

**Grouping attribution (2026-04-18 clarification).** A prereg's §25 gate names both (a) the metric-computing code path *and* (b) the grouping code path that produces the per-cell table. If the metric module's default aggregator groups by axes narrower than the prereg's grid — e.g., `summarize_arm` in `analyze_retention.py` groups by `(arm, safe_pop_mode, seed_fraction)`, which a prereg varying `ts`, `mr×gens`, or `selmode` cannot use directly — the prereg must also name the grouping wrapper / script / function covering its axis set (e.g., `analyze_5ab.py <axis> --include-holdout`). "Produced directly by `analyze_retention.py`" is incomplete when the grid axes require a wrapper the module doesn't include by default: the metric exists, but the per-cell table does not. Case: §v2.4-proxy-5b / 5c / 5d preregs cited `analyze_retention.py` for per-cell grouping that required the `analyze_5ab.py` wrapper (engineering commit 2026-04-18).

> See [Plans/methodology_improvements_2026-04-18.md](../Plans/methodology_improvements_2026-04-18.md) for the drafting rationale behind this clarification.

### 25b. Routing-critical metric discipline (added 2026-04-20 from §v2.5-plasticity-2a v1→v8 amendment cycle)

**Case.** §v2.5-plasticity-2a's row-1 classical-Baldwin-exclusion clause gated a specific escalation path (selection-deception viable → EES next vs. classical-Baldwin grid-miss → new prereg). v5 used `max(Baldwin_gap_h0_mean, Baldwin_gap_h1_mean) < 0.05` — a cell-mean of two Hamming bins with no occupancy guard and no CI. v5 → v8 then tried to fix this by tightening the rule: v6 CI with 20/20 non-nan floor (inherited from the primary axis); v7 relaxed to a soft 5/20 floor with vacuous-satisfaction-by-absence below; v8 three-tier n_valid=0/1-9/≥10. Each amendment fixed one edge case and created a new one at a finer grain of aggregation (across seeds → across individuals → per-bin). Five codex-FAIL rounds pre-data before the pattern became visible: the metric's modal occupancy at sf=0.0 was not known well enough from precedent to pre-register any routing rule on, and each rule-tightening was fitting against an imagined distribution rather than an observed one.

**Takeaway.** A pre-registered row clause is **routing-critical** if its satisfaction gates a specific escalation path and differentiates verdicts with material consequences for downstream experiments. Routing-critical clauses must take one of three treatments, not a plain cell-mean:

- **(a) Minimum-N occupancy guard** calibrated to the metric's expected modal occupancy on this specific axis. Parallel construction is not parallel parameterization — a floor that is right for a modally-populated axis is wrong for a modally-empty one; sibling-axis guards do not inherit.
- **(b) Uncertainty quantification** — CI bound (seed-bootstrap, permutation, equivalent) with the bootstrap-reliability threshold made explicit. The threshold is stated against the CI bound, not a point estimate.
- **(c) Advisory-only, confirmed at chronicle-time with pre-committed per-seed inspection criteria.** The clause is demoted from routing to diagnostic: the row fires on the remaining clauses; the advisory metric is reported for inspection but does not gate routing. A pre-registered chronicle-time discipline (e.g., "per-seed top-1 Hamming distribution inspection with attractor-category classifier") takes the mechanism-discrimination role.

Option (c) is not a fallback — it is the principled choice when the metric's data-generating distribution at the tested cells is not yet known. No pre-registered rule can correctly handle a distribution the author has not yet observed; chronicle-time inspection with pre-committed criteria is the honest substitute. When in doubt between (a)/(b) and (c), prefer (c).

> See [Plans/prereg_v2-5-plasticity-2a.md](../Plans/prereg_v2-5-plasticity-2a.md) amendment history block for the v1→v8 case evidence.

### 25c. Single-purpose clause discipline (added 2026-04-20 from §v2.5-plasticity-2a v1→v8 amendment cycle)

**Case.** §v2.5-plasticity-2a's row-1 classical-Baldwin clause was doing two jobs: (i) **routing gate** — firing on every cell in the outcome grid per principle 28a; (ii) **mechanism discriminator** — distinguishing "selection-deception operated under shortcut removal" from "classical-Baldwin operated under shortcut removal." A routing gate must handle every data state (empty bins, partial nan, sparse occupancy); a mechanism discriminator only has signal where the candidate mechanism could have operated. Those jobs have incompatible evidential requirements. Trying to serve both with one clause drove five amendment rounds of increasingly elaborate tier/threshold/vacuous-satisfaction logic — each fixing one failure mode and creating another at a different grain of aggregation.

**Takeaway.** A single pre-registered clause cannot simultaneously be a routing gate and a mechanism discriminator when the discriminator's data-generating distribution is uncertain or axis-specific. Split the jobs:

- **Routing** stays in row-clause fidelity (§28a). Use only metrics whose occupancy is well-understood from precedent experiments — typically the primary confirmatory axis, whose modal state is known.
- **Mechanism discrimination** goes to chronicle-time discipline (§25b option c). Pre-commit per-seed inspection criteria that distinguish the candidate mechanisms; apply after row-match to refine the interpretation, not to gate it.

**Amendment-count divergence as the tell.** When an amendment cycle does not converge to PASS over ≥3 rounds and P1 finding counts oscillate (not monotonically decreasing) with structurally similar findings across rounds (e.g., "missingness = emptiness" at across-seeds then across-individuals grain), the likely cause is a clause doing double duty or fit against an unknown distribution. Stop amending; either (i) run a small empirical probe on the relevant distribution before re-prereg'ing, or (ii) demote the clause per §25b option (c). Continuing to refine the rule against an imagined distribution is the sunk-cost path. Case: §v2.5-plasticity-2a v5→v8 — P1 counts 3, 2, 2, 2 across four rounds with the same "below-floor = absence-established" error class recurring at finer grains each time.

> See [Plans/prereg_v2-5-plasticity-2a.md](../Plans/prereg_v2-5-plasticity-2a.md) amendment history block for the v1→v8 case evidence and amendment-cycle tally.

## Measurement coverage (added 2026-04-17 from §v2.4-proxy-4d experience)

### 26. Diagnostic axes can become load-bearing — grid them at coarse bins

**Case.** §v2.4-proxy-4d pre-registered the outcome grid over one axis (`R₂_active` — erosion) and labeled `R_fit` (fitness-≥-0.999 fraction) as "Diagnostics to log." Both axes were measured at per-seed resolution. The observed cell `(R₂ low, R_fit high under BP_TOPK; R₂ low, R_fit low under Arm A)` did not correspond to any pre-registered outcome row on the R_fit dimension, because R_fit was axially under-scoped. The cross-cell R_fit differential carried decoder-specific mechanism signal — potentially a narrowing of the §v2.4-proxy-4c broadening — but it had to be demoted to "diagnostic flag, mechanism interpretation deferred" in the chronicle because no pre-registered row accepted it. This is principle 2b recurring on an axis the prereg labeled *diagnostic*: paired rows silently smuggled a correlation prior ("R₂ is the outcome axis; R_fit just decorates"), when both axes carried mechanism-level information.

**Takeaway.** Any axis a prereg measures at per-seed resolution is a candidate outcome axis. The outcome grid must include a coarse-bin row for every such axis, even if the axis is primarily labeled "diagnostic." Bins can be permissive (2–3 levels per diagnostic axis) but must be non-blank: every `(primary bin × diagnostic bin)` cell gets an explicit outcome token (PASS/PARTIAL/INCONCLUSIVE/IMPOSSIBLE). This is 2b extended: "grid every measured axis, not only the axes you labeled outcome." If a diagnostic axis is genuinely too noisy or too slow to gridify, the prereg must explicitly demote it to "effect-size-only, no outcome-table row" and cite the reason — silent diagnostic demotion fails this gate. At chronicle time, check: did any measured axis co-vary with an outcome in a way the grid didn't anticipate? If yes, update the next prereg's grid — don't narrate the missing cell.

## Metric definition discipline (added 2026-04-17 from §v2.4-proxy-4d experience)

### 27. Metric definitions live in code and are cited verbatim

**Case.** §v2.4-proxy-4d's `analyze_retention.py` docstring initially described its "active" view as an "extracted BP_TOPK-style view," but the implementation computed the permeable-all superset of BP_TOPK decode. The chronicle initially described the measurement as "direct edit-distance-2 retention" without the active-view-vs-decoded-view caveat. Codex adversarial review caught the mismatch; without it, the chronicle would have misrepresented what the measurement actually was — a silent principle-25 measurement-fidelity failure at the description layer rather than the code layer.

**Takeaway.** Each analysis module exposes a module-level `METRIC_DEFINITIONS: dict[str, str]` mapping metric name to a one-line specification of what the code actually computes (view, distance function, boundary conditions). Chronicle "Metric definition" blocks and prereg metric declarations cite entries from that dict verbatim — copy/paste, not paraphrase. The prereg-time check becomes: does the metric named in the prereg match the `METRIC_DEFINITIONS` entry in the producing module? The chronicle-time check becomes: does the cited definition still match the code at this commit? Both are 30-second checks that protect against description-vs-implementation drift — the most expensive failure mode to catch after a sweep has run.

## Chronicle-surface discipline (added 2026-04-18 from §v2.4-proxy-5* experience)

### 28. Letter-vs-intent drift across chronicle surfaces

**Case.** Three 2026-04-18 codex-pass-2 findings showed the same shape at different chronicle surfaces: a surface-level token or clause matched the letter of a pre-registered check while the underlying intent failed. Each looked locally like its own drift, but all three were instances of one pattern — writing them as one principle with enumerated sub-clauses is more coherent than three scattered §-additions, and extensible as new surfaces emerge.

**Takeaway.** A chronicle must detect and flag letter-vs-intent drift at every surface where a token, clause, or numeric criterion can match the letter of a pre-registered check while the underlying intent fails. Sub-clauses 28a, 28b, 28c below enumerate the currently known surfaces; new surfaces are added by supersession (§13) when discovered — do not let them drift silently.

### 28a. Row-match clauses — prose match must be clause match

**Case.** §v2.4-proxy-5a-followup-mid-bp claimed PLATEAU-MID "matched" on the row's prose ("Non-monotone staircase: two regimes or two competing mechanisms") even though observed adjacent-cell differences {0.144, 0.092} failed the row's numeric tightness clause (<0.05). Codex pass 2 flagged this as §23 drift: prose-match without clause-match is a §2b grid-miss, not a match.

**Takeaway.** A pre-registered outcome row matches the observed data only when *every* numeric clause in the row is satisfied. Prose-match plus numeric-clause-fail is a §2b grid-miss, not a match. When a row's prose anticipates a shape but its numeric clause is tighter than the observed signature, the outcome table was incomplete: add a row in the next prereg for the prose-match × clause-fail cell; do not narrate the current result as a match.

### 28b. Degenerate-success guards — single-criterion guards miss multi-mode regimes

**Case.** §v2.4-proxy-5c-tournament-size observed ts=2 with F=20/20 but R_fit_999 ≈ 0.005 — solvers found, not propagated. The prereg's SWAMPED guard for "tournament_size=2 exploration starvation" used `F < 18/20` as its detection criterion, which letter-passed at F=20/20 but missed the propagation-failure regime entirely. The guard's single F-only criterion could not catch a regime whose failure mode sits on a different axis from the criterion.

**Takeaway.** A degenerate-success guard that uses a single criterion must state explicitly which aspect of the regime it tests, and must add additional criteria when the guarded regime has multiple failure modes. Guard criteria should be a conjunction, not a single gate; at grid-design time, verify the conjunction covers every failure mode the guard's prose names. Single-criterion guards over multi-failure-mode regimes are vulnerable to the letter-vs-intent pattern — passing the letter while missing the intent.

### 28c. Status-line tokens — body qualifier must surface on the headline

**Case.** §v2.4-proxy-5c-tournament-size's initial status line was a bare `PASS`. The body explicitly flagged that the data matched PRESSURE-MONOTONE-R_FIT *on the letter of its clauses only* — the actual shape was cliff+plateau (ts=2 at 0.005; ts ∈ {3, 5, 8} at 0.72–0.75), a §2b grid-miss. The body also self-applied §28b to flag the F-only guard's letter-pass at ts=2. A reader scanning only the status line saw "PASS" with no qualifier. Codex pass 2 flagged this as the status-line surface of the same pattern. Fixed at commit `1165f88` by expanding the status line to carry the qualifier inline.

**Takeaway.** When a chronicle's status token would normally be `PASS` but the Result/Interpretation section flags a §2b grid-miss, a §28b letter-vs-intent failure, or any similar matched-on-letter-not-intent qualification, the status line must carry the qualifier inline (in parentheses on the same line), not only in the Result section. The standardized status vocabulary (`PASS | FAIL | INCONCLUSIVE | SUPERSEDED | FALSIFIED`) is grep-parsed and indexed; a scan-only reader who never drills into the body must still see the qualifier. Bare status tokens where the body substantively qualifies them fail this gate.

> See [Plans/methodology_improvements_2026-04-18.md](../Plans/methodology_improvements_2026-04-18.md) for the drafting rationale and case studies behind this principle.

### 29. Diagnose the failure class before designing the escalation

When a confirmatory experiment returns FAIL or `INCONCLUSIVE — grid-miss`, the next-step design depends on **which failure class** it is. Escalating the wrong class wastes compute.

Four classes, each with a canonical literature-term pairing:

| class | project-term | literature-term | signature | escalation |
|-------|--------------|-----------------|-----------|------------|
| 1 | `measurement-artifact` | (none — methodology-local) | infrastructure gate (§25) fails: F_train below ceiling on seeded cells OR frozen-control anchor diverges from baseline | fix the code, do not redesign the experiment |
| 2 | `mechanism-weak` | "capacity-insufficient" plasticity regime (Soltoggio-Stanley-Risi 2018 EPANN review) | mechanism capacity *not* exercised (latent state flat across budget; tail cells show no adaptation) | escalate capacity (rank-2 memory, deeper mechanism) |
| 3 | `grid-miss` | (none — methodology-local, §2b) | observed pattern fits no pre-registered row | update grid *pre-commit* (§2b), then re-interpret |
| 4 | `selection-deception` | "deception of learning-to-learn" (Risi & Stanley 2010); "objective deception" (Lehman & Stanley 2011, novelty-search lineage) | mechanism capacity *is* exercised, but selection doesn't need it (F_train at ceiling on seeded cells; static shortcut satisfies fitness) | change **selection regime**, not mechanism — Evolvability ES → novelty search / MAP-Elites with pre-registered BC → or strip the static shortcut (drop seed, add regime shift) |

**Pre-commit rule (extension of §2b).** The diagnosis tag must be dated and written *before* any escalation prereg is drafted. Retrofitting the diagnosis to whichever escalation path is cheapest is disallowed. Invoke the research-rigor `diagnose` mode to produce the dated diagnosis doc at `Plans/diagnosis_<§X>_<date>.md`.

**Terminology discipline.** Chronicle entries and escalation preregs must use the project-term / literature-term pair above (e.g., `selection-deception (Risi & Stanley 2010)`), not ad-hoc synonyms. If a diagnosis invokes a literature concept not yet cited in `docs/theory.md`, add the reference to "References to Obtain" (or the relevant Related Work subsection if the PDF is already read) *before* closing the diagnosis. This keeps the project's theoretical grounding moving in lockstep with its empirical findings.

**Prereg reference pattern.** Any escalation prereg must include, in its Setup section:
> *This prereg follows from diagnosis `Plans/diagnosis_<§X>_<date>.md` (class: `<project-term>` / `<literature-term>`). Escalation path is pre-committed; scope is restricted to the path identified there.*

---

## References

- [chem-tape/experiments.md](chem-tape/experiments.md) — v1 experimental record (primary source for most cases).
- [chem-tape/experiments-v2.md](chem-tape/experiments-v2.md) — pre-registered v2-probe suite (applies these lessons).
- [theory.md](theory.md) — Altenberg's constructional selection framework (theoretical frame).
- [CLAUDE.md](../CLAUDE.md) — project-level design principles (includes "commit hash in findings" mandate).
