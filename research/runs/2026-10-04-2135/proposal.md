---
node: questions/01-map-bias/07-shared-arrival
title: Shared arrival, revised — selection-weighted offspring census plus natural single-copy insertions (§32 J self/0.3)
---

**Why this now.** This is 07's planned last experiment, revised along the critique and the
owner's note on run 2026-10-04-2044. The question is still: in self-mate random-start runs,
are shared endings rare because exact shared children rarely arrive, or because a new copy
rarely establishes? What changed:
- one cohort only;
- offspring drawn the way the engine draws them;
- establishment measured on natural newborn children in their own populations;
- a staged size with an explicit "unresolved" outcome.

**The cohort and what it shows (checked in the saved data).** §32 J, L 64, crossover 0.3,
`crossover_mate: self`: 50 runs, 17 exact final populations.
- **First discovery:** 1 run establishes shared first (seed dir `a81465…`, generation 680).
  15 establish partly shared and 1 duplicated. This experiment does not explain first
  discovery; see Limits.
- **Later replacement:** 1 of the 16 runs that first established a non-shared form ends
  shared. In `017735…`, partly shared is established from generation 1340, and B-shared takes
  over between generations 1600 and 1800 (share 0 → 0.47 → 0.98). That makes about 24M
  offspring in established non-shared phases and 1 replacement. This is the target the readout
  is compared against. The 0.7 cohort is not pooled.

**What would run.** One queue entry in two stages. The source data is §32 J's saved final
populations (`experiments/output/2026-10-04/mapbias_s32_mate/`, the 50 self/0.3/L 64 runs).
Nothing from §31, no hand-built references and no mutation-only arm.

1. **Stage 1: selection-weighted offspring census.**
   - For each final population, recompute the per-case results. Then draw frozen generations
     with the engine's own reproduction step: elites, lexicase over the whole population
     (eligible elites included), a 0.3 crossover coin, self-crossover v2 and tagged mutation at
     μ 0.015. Each frozen generation gives 1022 children, so each parent form is represented in
     proportion to how often it actually reproduces.
   - Record each child's parent and the parent's form: exact shared / partly / duplicated,
     training-perfect but not exact (shortcut), or other.
   - Classify each child: exact, and if so its form. For shared children, record the helper
     type: B-helper, A-only, or other.
   - **A new arrival** is an exact shared child whose parent is not exact shared. Shared →
     shared copies are excluded.
   - **Report denominators per source population and parent stratum:** the number of children
     drawn from partly parents in population k, and so on. Report rates per population and how
     much they vary between populations, not only pooled.
   - **Size by the decision.** In the established phase, an arrival rate r from partly parents
     gives about 24M × r arrivals across the 16 runs:
     - r ≤ 1e-7 means ≤ ~2 arrivals in total;
     - r ≥ 1e-5 means ≥ ~15 per run.
     The target is about 3e7 children from partly parents, enough to resolve about 1e-7. The
     floor is 3e6, enough to resolve about 1e-6. The researcher pilots throughput (clone and
     semantic-key caching, a training-case pre-filter before the full exactness check) and caps
     stage 1 at 2 hours. The result states which bound was reached.
   - **Side check (cheap; drop it if replay is not exact).** Runs are deterministic. Replay 5 of
     the partly runs to the middle of their established phase, after confirming the
     best-genotype hex matches `history.csv` at that generation. Census those populations with
     the same procedure. This tests whether final populations are representative of the whole
     established phase, which is the critic's "changing occupancy" point.
2. **Stage 2: natural single copies in their own populations.**
   - **Source children:** shared children from stage 1 with a non-shared parent, from
     non-shared final populations. Use as many source populations and distinct child genotypes
     as stage 1 provides, with at most 1/5 of the insertions from any one population.
   - **Insertion:** continue the source population with its own config (self-mate, 0.3,
     μ 0.015) for 500 generations. In the first continued generation, the child replaces one
     random non-elite offspring slot.
   - **Matched control:** the same population and continuation seed, with no insertion. This
     measures spontaneous shared arrival, and shows the effect is the insertion's.
   - **Outcome at the horizon, never forced into two classes:**
     - established: shared is ≥ 50% of the exact non-elite population;
     - extinct: no exact shared individual left, checked on the full population every
       10 generations;
     - unresolved: still present but below 50%.
     Also report time to extinction, and whether the established copy is the inserted lineage's
     B-helper or A-only form.
   - **Staged and capped:**
     - 100 insertions first.
     - Stop there if ≥ 5 establish (p is then clearly not ≪ 1%), or if stage 1 already put
       arrivals at ≤ ~1 per run.
     - With < 5 established and ≥ ~10 arrivals per run, extend to 300 insertions. That is the
       size where 0 wins bounds p below about 1%, the level needed to call it
       fixation-limited.
     - Hard cap: 300 insertions plus 300 controls.
   - **If stage 1 yields no natural shared children:** run 100 labelled *transfer controls*.
     Insert single copies of evolved shared genomes from the two shared-ending runs into partly
     final populations. This measures an evolved layout in a foreign population, not a newborn
     mutant, and is reported as such.

**Runtime.** Stage 1 takes at most 2 h. Stage 2 is 200–600 continuations of 500 generations.
At roughly 80 s each on 10 workers (scaled from 06's 49 s per 300 generations), that is
30–80 min. The whole run fits one overnight queue.

**What each outcome would mean.** The bottleneck is read from the two factors separately: E =
arrivals per run in the established phase (stage 1), and p = natural single-copy
establishment (stage 2). Matching their product to the single observed replacement is only a
consistency check, because 1/16 has a 95% interval of roughly 0.2–30% and agreement could be
accidental.
- **A, arrival-limited.** E ≲ 1, and p is not near zero (≳ 10%), or E is so low that p does
  not matter. Close 07: "In self-mate L 64 / 0.3 runs, established non-shared populations
  seldom produce exact shared children. Late replacement by a shared form is limited by
  arrival, not by establishment." This is the shared-helper line's evidence for the root's
  explanation A, scoped to late replacement.
- **B, fixation-limited.** E ≳ 10 and natural copies mostly go extinct, with p ≲ 1/E (the
  300-insertion stage resolves about 1%). Close 07 with "newborn shared children arrive but
  rarely establish". This contrasts with seeded 3–10% shares (06): one copy is not a share.
- **Both.** E is about 1–10 and p is about 10–50%. Each factor alone falls short, and the
  product is compared with 1/16. Close 07 with both factors stated.
- **Unresolved.** This is a real outcome, not C by elimination. Any of:
  - zero arrivals with a stage-1 bound looser than about 1e-6;
  - stage 2 dominated by unresolved persistence at 500 generations;
  - the side check shows mid-phase populations produce shared children at a rate very
    different from final populations;
  - E·p is off from the observed rate by > 10× without a visible cause.
  Park 07 with the reopen condition "instrumented replay of the random-start runs (they are
  deterministic), recording arrivals and their fates in situ".

**Limits stated up front.**
- **Late replacement only, not first discovery.** This covers late replacement inside
  established populations. It does not cover first discovery, 1 of 17 runs here; that would
  need instrumented replay from generation 0. Whatever the outcome, the brief says so, and the
  claim "shared helpers are rare because they rarely arrive" stays scoped to established
  populations.
- **Narrow scope.** One task, one cell (L 64, self, 0.3), final populations plus a 5-run
  mid-phase check.
- **One replacement.** The observed target is a single event.

**Alternatives considered.**
- **The previous design** (equal K per non-elite, §31 selected-mate populations, hand-built
  single-copy contests): set aside for the reasons in the critique.
- **Instrumented replay from generation 0 for all 17 exact runs.** It would cover first
  discovery too, but it costs more and needs logging code in the engine's hot loop. I keep it
  as the reopen condition rather than commissioning it now; the critic agrees it is not needed
  to close the line.
- **Root part 2** (letting the map's bias evolve across a task family) and **02's rarity
  ladder**: unchanged. Part 2 is next after 07 and needs a plan file. I again suggest the owner
  commission one now.

**Budget and stop rule.** 07 has 2 experiments and the root has 5 left. This is one experiment.
07's stop rule stands: whatever this shows, 07 is closed or parked afterwards, and the
shared-helper line stops.

**Tree edits made with this proposal.** Appended the revision and the observed late
replacement (`017735…`) to 07's log.
