# §31: crossover dose, reciprocal, few copies, and stage 4 (map-bias)

Status: planned 2026-10-03 from Fable's nineteenth review of §30
(`experiments/output/2026-10-03/s30/fable_review.md`). Hobby notebook, not pre-registered.
The user allowed up to 10 hours of compute, launched right away, with at most two Codex
reviews of the code changes.

## Why

§30: with crossover at 0.7, a shared form starting at 1/32 or 1/10 is lost in 294 of 300 runs.
Without crossover it often establishes, but at only about 1–3% per copy. Fable's probes
suggest two things:
- the barrier is symmetric (majority rule between incompatible forms);
- random starts do solve the task, and solutions arrive partly shared.

The open questions are:
1. Is the barrier graded in crossover rate?
2. Is it symmetric?
3. Is establishment from one copy as rare as independence predicts?
4. From random starts, which form is found first, does it stay, and does a shared form ever
   appear?

## Arms (settings as §30 unless listed; generator `experiments/chem_tape/s31_make_sweeps.py`)

| arm | file | what | cells | seeds | generations | runs |
|---|---|---|---|---|---|---|
| D | `s31_dose.yaml` | crossover 0.1 / 0.3 / 0.5; shared from 1/32 and 1/10 vs duplicated (L 64), partly shared (L 64, 32) | 18 | 30 | 300 | 540 |
| E | `s31_reciprocal.yaml` | shared at 768 / 922 / 992 of 1024 vs duplicated (L 64), partly shared (L 64, 128), crossover 0.7 | 9 | 30 | 300 | 270 |
| F | `s31_few_copies.yaml` | 1 or 8 shared copies vs duplicated and partly shared, L 64, crossover off | 4 | 100 | 300 | 400 |
| G | `s31_stage4.yaml` | random starts, L 32 / 64 / 128 × crossover 0.7 / 0.3 / 0 | 9 | 50 | 3000 | 450 |

- New option `seed_counts` (exact copies per seed tape) for E and F. It is off by default,
  and the hash and initial population are unchanged when empty.
- Order: D, E, G, F.
- Trim rule (Fable): if the G pilot median is over 500 s per run, drop crossover 0.3 at
  L 32 and 128.

## Readouts (`experiments/chem_tape/s31_report.py`)

Final outcomes come from the non-elite final population, classified by knockout. A form
verdict needs at least 20 fully exact individuals; elite forms are listed separately.
- **D:** wins per cell, plotted next to §30's 0 and 0.7.
- **E:** seeds where shared stays above 90%.
- **F:** wins out of 100, against the independence prediction from §30 (about 3 and 1 from
  one copy; 22 and 7 from eight).
- **G:**
  - seeds with a fully exact individual (ever and at the end) and the median first
    generation;
  - the form at the first census with a fully exact individual, and the final verdict;
  - any shared individual at any log point;
  - runs that lose the solution.

## Reading it

- **D:** wins rise smoothly as crossover falls → a graded barrier. Wins only at 0 → any
  crossover blocks establishment.
- **E:**
  - the rare competitor is removed → majority rule; rewrite §30's claim as symmetric;
  - rare partly shared invades → crossover works specifically against sharing.
- **F:**
  - matches independence → about 1–3% per copy;
  - many more wins → copies help each other.
- **G:**
  - all partly shared, no shared, at every rate → discovering a B helper is the obstacle;
  - shared at first solve and kept → a founder effect;
  - crossover off solves far less → a trade-off: crossover finds solutions but removes rare
    forms.

## Process

Pilot (2 seeds per cell for D, E and F; 1 for G), at most two `codex review` rounds, commit
and push, launch `queue_s31.yaml` (10 workers). Write-up as notebook §31 with the commit
hash, marked "Fable review pending".
