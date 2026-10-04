# Briefing: shared helpers, stages 1–3 (map-bias §29), 2026-10-02

> **Revised after Fable's eighteenth review** (`fable_review.md`). The original reading
> ("discovery is the obstacle") was premature: only retention from 100% and 50% was tested.
> The crossover-asymmetry mechanism was wrong, and two seed-dup runs that lost the solution
> were missed. Corrections are inline below and in notebook §29.

**What was tested and why.** Can tagged runs hold, and does evolution keep, a functional part
that several outputs use? Three outputs on tags 0/1/2: A = max > 5, A and B, A or B
(B = sum > 10). The setting is leftmost-wins with the `tagged` alphabet.
- Stage 1 hand-builds a shared form (A and a B helper read by RECV, 24 cells), a partly
  shared form (27) and a duplicated form (33). The duplicated form does not fit in 32 cells.
- Stage 2 applies variation alone to each form.
- Stage 3 seeds populations with the forms and runs 1000 generations, 30 seeds per cell
  (settings as §25: crossover v2, lexicase, balanced fitness, population 1024).

**What happened.**
- **Stage 1:** all forms are fully exact on all 10,000 lists. Knockout gives the expected
  consumer counts: A feeds 3 outputs and B feeds 2 in the shared form, 1 each in the
  duplicated form. The plan's stop rule did not apply.
- **Stage 2** (figure `docs/map-bias/figures/s29_stage2_survival.png`):
  - Under mutation and random-partner crossover, shared and duplicated survive about
    equally (e.g. mutation at 64 cells: 0.26 vs 0.24 of children fully exact).
  - Shared × duplicated crossover is lopsided: 0.80 fully exact children with shared as
    parent A, 0.38 with duplicated as parent A.
- **Stage 3**, 210/210 runs complete:
  - **seed-mixed** (main readout, figure `s29_mixed_shared_fraction.png`): the shared form
    takes over in 30/30 seeds at both 64 and 128 cells. At generation 20 it is a mean of
    96% / 94% of fully exact individuals (lowest seed 81%), and the mean stays ≥ 94% from
    then on. The neutral expectation was 50%.
  - **seed-shared:** stays 100% shared at 32, 64 and 128 cells; fully exact individuals are
    present at every logged generation.
  - **seed-dup:** 60/60 runs turn partly shared. Tags 1 and 2 replace their copy of A with
    `RECV0`, crossing 50% at a median of generation 80. This may be helped by the seeds'
    tag-0 latent tags. A pure B helper practically never appears: 4/60 runs, one individual
    each time, never at the end.
  - **In 2/60 seed-dup runs** (seed 9, both lengths) the population lost the fully exact
    solution to a shorter training-perfect body (sum > 15).

**What it teaches, within this scope.**
- Retention from a majority or an equal share is not the obstacle. The shared form wins
  against an equal share of duplicated solutions at 64 and 128 cells; at 32 only
  persistence was tested.
- The likely cause is the smaller mutation target (24 vs 33 critical cells), not crossover.
  Crossover between the forms lowers the shared share.
- Fable's 3-seed probe suggests that a *rare* shared form (10% or 1/32) is wiped out when
  crossover is on, and wins when it is off. Establishment is therefore the open question.

**Failures, missing data and doubts.**
- **No missing data:** 3/3 queue entries done with exit 0, 210/210 runs. Nothing was
  scaled or skipped.
- **Started early:** the prompt was pasted at about 13:00. The queue ran 13:39–14:35; you
  were present and chose to let it finish. Heavy runs will wait for 23:00–08:00 from now on.
- **Replay check:** the stored §25 outputs were not on the Mini. It compared against a
  fresh baseline at `fa36ac7` instead (identical).
- **Codex:** two reviews, two P2s, no P1, both fixed before launch:
  - a run-memo bug for outputs that read each other in a cycle;
  - task alternation with multi-output tracking, now rejected.
- **Clean-tree flag:** the queue metadata records `git_dirty: true` because of the runner's
  own untracked lock and status files. No tracked file was modified.
- **Why the shared form wins is not established.** Fable's model and probe point to the mutation
  target, not crossover.
- **Census resolution:** it logs every 20 generations on 256 individuals, so the seed-mixed
  takeover happens before the first logged point after generation 0.
- **"Partly" is broad:** it includes genomes where only one consumer reads A.
- **Elites:** they keep the seeded genome frozen and are excluded from the inspection
  tallies.
- **Fable:** not consulted (0/6).

**Which reading applies.** None of the three yet. Retention from a majority holds, but
establishment from a small share is untested, and the probe hints that crossover blocks it.

**Suggested next steps.** The establishment experiment (notebook §30): shared vs duplicated
and shared vs partly shared from 1/32 to 1/2, crossover 0.7 and 0, plus seed-dup with
random latent tags. Then stage 4, with a crossover-off arm if crossover is the barrier.

Commits: `9848d08` (stages 1–2), `7141ecf` (stage 3, queue), write-up commit in STATE.md.
Full tables: `report/s29_report.md`, `stage2/preserve.md`, notebook §29.
