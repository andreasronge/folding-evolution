---
verdict: pass
---
# Code review: 2026-10-08-1046 (recovery of 0918, then frozen scoring)

Reviewed `git diff b19a1d1..a804f4f` (three files: `inherited_bias.py` operational edits, new
`inherited_bias_recovery.py`, tests), proposal.md, critique.md, plan.md, queue.yaml, and the
0918 source directory the recovery reads. Ran `tests/test_inherited_bias.py` in the worktree
(33 passed), `run_queue.py --validate` on queue.yaml (OK, 17 100 s), and timed the bootstrap at
10 000 draws (0.3 s per family, so the 300 s analysis stage is safe).

## Blocking issues

None.

## What I checked and why it holds

1. **Seeds and arm wiring are unchanged.** Recovery jobs come from `acquisition_jobs(..., "main")`
   with the original phase, so program, modifier and case seeds are the 0918 streams. The
   selective replays write under `selective/` and `load_acquisitions` globs only
   `acquisition/main/*/*/*.json`, so no duplicates reach scoring. Scoring and analysis code is
   untouched except the continuation wording.
2. **Hidden deadlines are gone.** `acquire()` and `score()` now default to an infinite deadline;
   `run_one` has no other cutoff beyond the evaluation cap. The only remaining explicit limits are
   the selective 3 600 s, the shared 9 000 s recovery envelope and the 900 s timing limit, all
   listed in plan.md.
3. **The replay gate cannot fail for a spurious reason I could find.** JSON round-trips floats
   exactly (`json.dumps` default repr), so exact `probs`/`theta` equality against the loaded 0918
   rows is sound. The Rust evaluation uses order-preserving `par_chunks_mut.zip(par_iter)`, so
   0918's unpinned Rayon threads cannot change outputs. `first_exact` iterates in index order with
   a deterministic bounded cache; the only `set` uses in `evolve.py`/`tagged.py` are membership
   tests. `evolve_bias.py`, `tagged.py` and `evolve.py` are byte-identical to 511711c, and
   `source_rows` enforces that at runtime.
4. **The selective timeout has real headroom.** From the cut row: every slow episode is an
   even-indexed max1 episode (unsolved ones cost 100–165 s of verifier time; max5 episodes cost
   5 s). The 18 remaining episodes are 9 max1 + 9 max5; even if all 9 max1 go unsolved at 165 s the
   replay needs about 2 730 s, under 3 600 s, and it runs at 3 workers instead of 10. So the
   stop-for-wrong-reason path (selective timeout, then fallback refused because 9 000 − 3 600 <
   5 450 s) is unlikely. On the expected 1 900–2 700 s path the fallback fits in the remaining
   envelope.
5. **Completeness gates.** `check_acquisitions` runs on the merged roster before the sentinel;
   timeouts raise `Deadline` and leave `complete=false`, which blocks the sentinel; scoring and
   analysis refuse incomplete rosters. A stale sentinel is unlinked at the start of `recover()`.
6. **Queue plumbing.** `research.py` launches the queue with the worktree as cwd and the main
   checkout's `experiments/output` as output root, so `$RUN_DIR/../<id>` siblings and the absolute
   `--source` path both resolve; the date directory is fixed once at queue start. `RAYON_NUM_THREADS=1`
   is on every command and checked in code for the recovery modes.
7. **Critique disposition.** Notes 1–5 are implemented (frozen timing roster written before
   observation, references priced separately, tails retained, phase `main` preserved, runtime
   excluded from equality, cumulative budget with fallback refusal, development-bank continuation
   wording in code). Notes 6–7 concern digest/question/log wording outside the researcher's
   write scope and are relayed to the steward in preparation.md. Acceptable.

## Minor notes (non-blocking)

- **Max scoring timeout is the real risk in this queue, not a gate.** The 4 067 s point estimate
  is tail-dominated: the max1 inherited cell is 10 searches, mean 72.8 s, max 260 s, and 5/40
  learned searches had verifier tails. A 30–35 % underestimate of the max1 cells would exceed
  5 400 s, and `--mode score` has no resume, so a timeout loses the whole stage. If the queue is
  still editable, rebalancing within the same 17 100 s total (sum 2 400 → 1 500 s, still ~2× its
  779 s estimate; max 5 400 → 6 300 s) would cost nothing scientifically. Otherwise accept the
  risk; the recovered acquisition directory survives a scoring timeout and can be rescored.
- The replayed max/inherited/14 row will carry a 3-worker `seconds` beside 79 ten-worker values.
  `analyze()` averages these into `exposure` and `break_even` (descriptive only). The analysis
  should note it.
- The fallback branch re-runs the two control replays as part of the 80; harmless.
- Preparation ran 92 timing searches on indices 2000–2002 plus the earlier 28 on 1000–1001; none
  are scoring indices 0–15 and the plan excludes them from inference. Fine.
