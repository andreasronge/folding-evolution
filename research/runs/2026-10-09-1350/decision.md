---
next: strategy
---
# Decision: run 2026-10-09-1350 — close question 33, return to strategy

**Result.** The 0843 fragment extractor was applied to 1831's parents archived before their source
search first solved (E). It was scored against C-chain blocks with E's length law (W_E) on 1036's
harness and seeds (commit `e9a04f8`), then-addition-v1, 16 corpora × 16 cells × 16 seeds. The
roster was complete: 8 192 searches, 84 min. All 16 libraries filled 32/32 with no fallback, and
0 padded hits in 8 192 checks. The 1036 F/W/C rows replayed bit-exactly (48/48), so all five arms
are paired.
- **E/W_E 0.981× [0.911, 1.057]**, 7/16 corpora above 1. The same holds under 1 × cap,
  both-solved and each family alone.
- E/F **0.843× [0.795, 0.892]**, 0/16 corpora above 1. E/W 1.007× [0.948, 1.070];
  W_E/W 1.026×. E/C 1.235× is the same as 1036's W/C (1.227×), so it is the block operator's gain.
- Descriptive: no pre-solve library contains `gt`. The exact libraries' comparison joins are
  replaced by reducer→`if_gt` windows.

Pre-registered rule 3 fired: `no_worthwhile_increment_ends_source`, with upper bound 1.057 < 1.10.
I expected E/W_E between 1.0 and 1.10 and E/F 0.85–0.95. The routing was right; both points came
in slightly lower. ([analysis](analysis.md))

**Decision: close 33 and return to strategy (`next: strategy`); no proposal written.** Because:
1. **The question is answered at its scope.** A gain above about 1.06× over length-matched chain
   blocks is excluded for this source and extractor on then-addition. More seeds would only narrow
   an interval that already excludes the worthwhile increment.
2. **The pre-set routing says so.** Rule 3 ends this source/extractor at this scope. Strategy
   1350 asked for a return after this comparison under every outcome.
3. **No slots are left.** Root 10 has used 25 of 25, and 33 has used 1 of 1.

The limits stay attached:
- One source selection (lowest-slot parents at generations 64/128/256) and one extractor; C is
  still fitted from exact solvers.
- Development bank.
- Not a verdict on pre-solve learning in general.
- Not a harm finding: the interval includes 1.
- E/W_E ≈ 1 together with E/F < 1 fits "gate joins carry F's increment", but E differs from F in
  source, content and length law at once, so no mechanism is identified.

**Tree changes.**
- [33](../../questions/10-compositional-map-transfer/33-pre-solve-fragment-source/question.md)
  is closed, with a summary, a new log and a reopen condition.
- Root 10: summary sentence, budget line, sub-question entry, Related and log updated.
- Digest: a new bullet ("the same extractor applied to pre-solve parents gave no worthwhile gain
  over C-chain blocks on then-addition") and an Overall clause. Bullets 15, 22 and 24 were
  shortened to stay near the word limit (3 031 words); their old wording is kept verbatim in root
  10's log.

**Digest check (critique 1350, notes 7–8): both fixed in
[32](../../questions/10-compositional-map-transfer/32-learned-fragment-operator/question.md).**
- Note 7: explanation (a) now says that across shape the fragment procedure beats W, but joint
  content versus token supply is unresolved there (no B).
- Note 8: r −0.67 is now descriptive. Substitution is a hypothesis, not separated from the
  shared log cost(W) term.
- The digest itself had neither claim. Logged in 32's log.

**Parked questions.** No reopen condition is met.
- Root 23 needs a changed inheritance rule with a measured selectable signal; this run used
  external extraction.
- Root 01's 02/04/07/08/09 are untouched by this run.
- Closed 32's reopen condition covers "F built from fewer or cheaper source tapes"; 33 has now
  measured that comparison (E), so nothing remains for 32 to add.

**For the strategist to weigh.** This is my ranking, not priced designs. The run has used 12 of 40
experiments, and the deadline is 2026-10-10 08:12, about 16 h away.
1. **Do the `gt` joins carry F's increment? (mechanism, on 1036's paired rows)** One arm would be
   F with its `gt`-containing fragments removed and refilled from the next-ranked non-`gt`
   windows; the comparison is against F and W, reusing 1036's rows. The cost is about the same as
   this run (about 85 queue min, 5 h total). It would tell any acquisition design what a source
   must supply, and whether a cheap source can be screened for it. A read-only probe should come
   first: how often are `gt` tokens knockout-active in pre-solve tapes at later checkpoints? If
   never, the pre-solve route is closed by content, not just this extractor.
2. **Why W beats C (mechanism, library-free).** W/C is 1.23–1.38× on every bank, and E/C here just
   reproduces it. This is the one block-edit gain that needs no library and so no acquisition.
   The test is a suffix-preserving point edit against C and W, priced at about 3–4 h in strategy
   1350.
3. **Ending the run is reasonable.** Neither option is acquisition by evolution. The fragment
   line now has a clean stopping point: exact-solver fragments help (32), and this cheap
   pre-solve source does not (33).
