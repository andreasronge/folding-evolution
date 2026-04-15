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

- **Before pre-registering an experiment:** read principles 1-4 and 6.
- **After a surprising result:** read 3, 10, 14, 16.
- **When writing a summary bullet:** read 18.
- **When reviewing your own claim language:** read 17.
- **When adding a new config parameter:** read 11.
- **When a previous claim needs revising:** read 13.

If a future experiment contributes a new lesson worth adding, update this document with a new case + takeaway pair. The point is to avoid re-learning.

## References

- [chem-tape/experiments.md](chem-tape/experiments.md) — v1 experimental record (primary source for most cases).
- [chem-tape/experiments-v2.md](chem-tape/experiments-v2.md) — pre-registered v2-probe suite (applies these lessons).
- [theory.md](theory.md) — Altenberg's constructional selection framework (theoretical frame).
- [CLAUDE.md](../CLAUDE.md) — project-level design principles (includes "commit hash in findings" mandate).
