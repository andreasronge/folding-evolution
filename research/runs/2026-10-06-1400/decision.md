---
next: proposal
---
# Decision: run 2026-10-06-1400 (14, saved-map shape-shift check) — blocked before running

**Continue 14; re-propose the same design as run 1419.**

What happened: strategy 1400 raised root 10's budget from 5 to 7 and asked for one bounded
check of 0811's only contextual lead. I opened sub-question 14 and proposed scoring the
unscored "b" continuations (plus "a", G and M1–M6) on the eight frozen off-family cells, with
R's residual ablation and a frequency-matched token-only control (R_fm). The critic
approved with notes; the loop auto-approved. The driver then stopped at prepare: merging main
into research/main conflicts. No plan, code or data exists, and no slot was used (root 10:
4 of 7; 14: 0 of 1).

The conflict is a single add/add file, `research/runs/2026-10-06-0811/code_review.md`. main
holds the second-pass review (`verdict: pass`, range `f413e47..0709104`); research/main holds
the first-pass review (`verdict: fail`). The correct resolution is to keep main's version
(when merging main into research/main: `git checkout --theirs` on that file). I have not
touched git. The owner or driver needs to resolve this before 1419 can prepare, or 1419 will
block in the same way.

Why continue rather than park: nothing was learned, so no belief changed. The question, its
feasibility numbers and the critic's view are unchanged. The blocker is bookkeeping, not
design. Strategy 1400 put this check ahead of the four-reducer feasibility study because it
decides how much weight the contextual arm gets there. That reasoning still holds.

What changes in 1419: the critic's five notes are applied. These are a solve-count forecast;
interpreting a shift through the BE and LIN R/R_fm intervals; scoping "beyond token
frequencies" to the matched quantity; precedence between D-a and D-b and a rule for row 1 +
D-c; requiring all six starts; and BE wins counted as 5/6. G is scored once and serves as both
harness check and reference.

Tree changes this cycle (no new evidence):
- Wording fixes from the critique's digest check (items 5–9) in `digest.md`, root 10's and
  13's `question.md`, and correction entries appended to both logs. The unresolved ablation is
  no longer read as absence. Operator acceptance near 25% no longer claims that selection fails
  to rank steps. "No training gain" became "no resolved training gain". Attribution of "every
  resolved gain" to token retuning became "token-only gains demonstrated; residual
  contribution not established". "As much faster" became "similar point estimates".
- Parked questions re-checked (02, 04, 07, 08, 09): no new data, so no reopen condition is met.
