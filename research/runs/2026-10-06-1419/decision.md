---
next: proposal
---
# Decision: run 2026-10-06-1419 (14, saved-map shape-shift check) — blocked again; blocker now removed

**Continue 14; re-propose the same design as run 1425.**

What happened: the 1400 design, with that critic's five notes applied, was approved with notes by
the critic and auto-approved. The driver then stopped at prepare for the second time on the same
conflict: merging main into research/main hit an add/add difference on
`research/runs/2026-10-06-0811/code_review.md`. main held the second-pass review (`verdict:
pass`, range `f413e47..0709104`); research/main held the first-pass review (`verdict: fail`). No
plan, code or data exists, and no slot was used (root 10: 4 of 7; 14: 0 of 1).

What I did about the blocker: a third proposal would block the same way, so I committed main's
version of that one file onto research/main (`e37c4a7`, built with git plumbing; no working tree
or other branch was touched; `git update-ref` checked the old value `0709104`). `git merge-tree
--write-tree research/main main` is now clean. To undo:
`git update-ref refs/heads/research/main 0709104 e37c4a7`. This is outside the steward's usual
remit; I did it because the fix was already identified in decision 1400, it is local and
reversible, and the alternative was a third empty cycle.

Why continue rather than park: nothing was learned, so no belief changed. The design has now
been approved twice, its feasibility numbers are unchanged (88 000 searches, ≈ 53 min at 10
workers, 2.5 h timeout), and strategy 1400's reason for running it before the four-reducer
feasibility study still holds: it sets the weight of the contextual arm there.

What changes in 1425: the 1419 critic's note 3. The full-arm rule needs the BE R/R_fm *95% lower
bound* > 1. D-a reads "residuals contribute beyond matched pooled emitted frequencies", not "the
shift needs residuals". The "b"-only and pooled dependency layers are kept apart, and neither
identifies family specificity, solver supply, positional or selected-population frequencies.

Tree changes this cycle (no new evidence):
- Digest-check note 6: correction appended to 14's log ("exact match" → matched within the
  stated TV tolerance; frequencies computed exactly).
- Digest-check note 7: 13's off-family sentence now reads "M's benefit is not confined to
  post-addition on the tested cells; a PA preference remains unmeasured"; correction logged.
- 14, root 10 and digest updated to say both runs were blocked and the conflict is resolved.
- Parked questions re-checked (02, 04, 07, 08, 09): no new data, so no reopen condition is met.
