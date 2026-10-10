---
next: strategy
---
# Decision — run 2026-10-10-0145 (question 38)

**Close [38](../../questions/10-compositional-map-transfer/38-cheap-bias-source-replication/question.md);
return to strategy; no proposal written.**

**Result.** The unchanged A8 recipe was rebuilt 16 times (8 per family) from fresh G4 searches on
the complementary source roster, the four former comparison-gate holdouts per family. New seeds
were used, and the legacy build was replayed exactly. The artifacts were scored on `two-sum-v1`
with the 2303 keys. Primary cost(G4)/cost(A8′) was **2.50× [2.17, 2.85]**. It also cleared the
pre-set 1.5× margin per family (BE 3.14×, PA 1.99× [1.66, 2.32]) and at a 1× cap penalty (2.06×
[1.84, 2.28]). All 16 builds beat G4. Pre-registered label: **useful replication**. Reported
without a rule:
- δ = A8′/historical A8 on identical keys was 1.09× [0.90, 1.32], unresolved.
- PA was weaker than its historical builds: 217 vs 249 of 512 solved, and PA1, PA6 and PA7 cost
  about 2× more. First-batch yield does not explain this.
- Acquisition was 4.5 M evaluations (historical 6.5 M). Measured in evaluations, A8′ repays G4
  after 35 [30, 43] searches.

The code review passed, and the data are complete: 1 024 rows, all timing rows replayed.
([analysis](analysis.md))

**Why close.** The question was whether A8's usefulness depended on the source cells it was
developed on. The answer at this scope is no. A fall below the usefulness bar is excluded, so the
*recipe* is what to carry forward, not only the 2033 artifacts. Neither δ nor the PA deficit
would change that choice. Scoring the 16 S8′ artifacts that were built but not scored would place
the PA deficit. It is cheap (~35 min of queue) but would not change a decision now, so it is
recorded as a reopen condition, not proposed.

**What this does not settle.** We tested one alternative roster inside the same two families.
Both rosters, and two-sum-v1, are development data. This is not robustness to arbitrary source
sets and not a new-family result. Equality with the historical builds is not shown: δ allows 10%
cheaper to 32% costlier. Decoder vs library, and yield vs content, remain bundled. This is
external fitting, not inherited adaptation.

**Two harness defects, for the next researcher.**
1. *Timing admission is biased against the second arm.* The 32-job timing batch ran at 6.1
   effective workers; scoring reached ≥ 9.4. That rejected both arms (7 188 s projected against a
   7 080 s ceiling) when they would have fit in about 4 800 s, and it lost σ′. Time at least 64
   searches, or take throughput from the collection batches.
2. *Worker-second calibration.* The calibration came from two uncontended G4 replays (0.558).
   Evaluation throughputs were equal across runs, so the runner's "never repays in worker-seconds"
   is an artifact. Calibrate under load, or report evaluations only.

**Why `next: strategy`.** Root 10 has used 30 of 30 slots. Strategy 0145 granted one slot and
said to return whatever the outcome. No other open question has budget. Parked questions were
re-checked and none has its reopen condition met:
- Root 23 needs a selectable inherited signal; this run was external fitting.
- Root 01's children are unchanged.
- 37's reopen conditions (a decision needing the sign vs full F, or a different shape) are unmet.

**Tree edits this cycle.**
- 38 closed (summary, scope, reopen condition, log).
- Root 10: summary, slot line, sub-question list, Related and log entry.
- Digest: new 38 bullet; root header 30/30; "Overall" and "Not shown" updated.
- Critique 0145 digest-check notes applied:
  - Note 7: "cheapest at every horizon" is now "below S8 and full F; repays G4 after about 47
    searches", in the digest and the root summary, with a correction appended to the root log.
  - Note 8: 37's "no size of top-up would change the choice" is corrected in 37's log.

**For the strategist: candidates this result makes concrete (not proposals).** About five hours
remain before 08:12; 17 of 40 experiments are used.
- **Carry the recipe to a genuinely new family.** This is what the result licenses. It needs a new
  family with its own sources and a fresh target bank frozen before scoring. For example, predicate
  addition on a domain where it survives the screen. The bank design and the semantic screen come
  first, and no price exists yet; probably too long for this window.
- **Place the PA deficit.** Score the built S8′ artifacts (~35 min of queue, ~1.5 h cycle). This is
  a diagnostic only: no current choice depends on it.
- **Evolutionary instead of fitted acquisition** (root 23, owner note). This is still the core gap.
  The reopen condition is unmet, and there is no changed rule with a selectable signal yet.
- **Stop the run.** Root 10's acquisition line is answered at its scope. If no candidate has a
  complete price within the window, ending here is reasonable.
