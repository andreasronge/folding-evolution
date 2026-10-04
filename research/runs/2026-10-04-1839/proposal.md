---
node: questions/01-map-bias/06-self-mate-establishment
title: Self-mate contest — can a rare shared form establish when crossover is with the parent itself?
---

**Why this now.** The shared-helper line ends on one untested question. Crossover v2 with a
selected mate removes a rare shared form at rates of 0.3 and above (§30, §31 D). The
explanation we have is hybrids: shared × competitor children stop being shared (§30, §32 K).
But §32 J showed that discovery does not need a selected mate: crossing a parent with itself
still solves 68–80% of random-start runs, though about three times more slowly. Self-mating
makes no hybrids. So this contest tests the hybrid account directly, and it also decides
whether discovery and establishment can work under one operator. Fable proposed it as the
next step (§32 "Next"). It is cheap, and either result lets us close or park the
shared-helper establishment thread. I opened a new question, 06, for it: it is a seeded
contest, not a random-start run, so it does not belong in 04.

**What would run.** Repeat §31 D's contest with `crossover_mate: self`. Keep everything else
as in `s31_dose.yaml`: L 64, population 1024, lexicase, μ 0.015, 300 generations, seed_split,
the same seed tapes, and seeds 0–29.
- Contests: shared vs duplicated, and shared vs partly shared.
- Start: 1/32 and 1/10 shared.
- Crossover 0.3 and 0.7, self-mate.
- That is 2 × 2 × 2 × 30 = **240 runs**. At about 40 s per run (K pilot) this takes **about
  20 minutes on 10 workers**.
- For comparison we already have the same cells with crossover 0 (§30) and with a selected
  mate at 0.3 and 0.7 (§31 D, §30). No new code is needed beyond the sweep YAML:
  `crossover_mate` exists and is only rejected with `track_lineage`, which is off here.
- Readouts:
  - shared wins out of 30, using the §31 verdict rule;
  - the shared share at generations 5, 10 and 20, to compare with K's "halves within 5
    generations";
  - a one-crossover census: self-crossover each hand-built form about 10,000 times and count
    the children's forms (exact shared / partly / duplicated / broken). This is the self-mate
    version of Fable's §30/§32 enumeration and tells us how fragile each form is to
    rearrangement alone. It is a small analysis script, not an evolution run.

**What each outcome would mean.** The reference rows are crossover off (vs duplicated 19/29,
vs partly 8/19, from 1/32 / 1/10) and a selected mate (vs duplicated 10/24 at 0.3 and 0/0 at
0.7; vs partly 0/0 at both rates).
- **A — the hybrid account holds, and the two can coexist.** Self-mate wins reach at least
  about two thirds of the crossover-off counts at both rates. For example, from 1/10:
  ≥ 19 vs duplicated and ≥ 12 vs partly. Then the trade-off between discovery and
  establishment is not forced. But arrival remains the limit: self-mated random starts ended
  shared in only 2/50, 0/50 and 2/50 runs (§32 J). If A holds, I would close 06. I would then
  stop the shared-helper line with "shared forms are kept once common, and are rare because
  they rarely arrive". Spending more on arrival would need a new argument.
- **B — rearrangement itself costs the shared form.** Self-mate wins stay near the
  selected-mate counts (0–3 of 30 vs partly; at 0.7 well below crossover off vs duplicated),
  and the census shows shared children broken more often than competitors. Then the hybrid
  account is incomplete, and "self-mating as a route to sharing" is dead. I would close 06
  and park the shared-helper line with that explanation.
- **C — in between,** e.g. self-mating rescues shared vs duplicated but not vs partly shared.
  The census should show which child type causes the gap. One follow-up from 06's budget
  (2) at most, then park.

In every case this is the last establishment experiment I would propose for this task.

**Alternatives considered.**
- *Duplication-only companion* (crossover 0 + `run_duplication_rate`, random starts; Fable).
  This asks which part of self-mating does the discovering. It is interesting, but it does not
  decide anything about the trade-off. It stays as a low-priority item under 04.
- *Crossover schedule* (selected mate early, off or self later). This only makes sense after
  this result: under A it would be the natural engineering follow-up, and under B it would be
  pointless.
- *Rarity ladder* (02, parked). Its reopen condition is "the shared-helper line stalls". The
  line has not stalled yet: this result is what decides that.
- *Root part 2, evolving the map's bias across a task family.* This is the larger untested
  half of the core question, and it is the natural next direction once the shared-helper line
  closes. It needs its own plan, so it is not a one-night experiment.

**Tree edits made with this proposal.**
- Opened `06-self-mate-establishment` (budget 2).
- Logged in 04 that the self-mate test moved to 06, and lowered 04's priority.
- Confirmed the close of 05.
- Updated the open-questions list in the digest.
