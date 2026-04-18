# Methodology & research-rigor skill improvements — TODO for a dedicated session

**Status:** TODO · drafted 2026-04-18 · to be addressed in a standalone work session after the current chem-tape v2 batch stabilises.

**Scope.** Systemic gaps surfaced during the 2026-04-18 session's codex adversarial review + the §v2.4-proxy-5c-tournament-size result. Each gap appeared at least once in recent work and is predicted to recur without an explicit codified guardrail. Genuinely one-off code-review catches are not in this list.

**Principle.** Methodology edits should not be rushed. The items below are collected here as case-referenced proposals so a dedicated session can draft new sub-principles against concrete examples rather than in the abstract.

---

## Session-start checklist

Run these before drafting any new sub-principle text. ~15 min total.

1. **Read in order:**
   - `docs/methodology.md` end-to-end (current 27-principle ledger — know the voice and existing sub-principle style before adding to it).
   - This TODO file end-to-end.
   - `.claude/skills/research-rigor/SKILL.md` (the skill whose `prereg` / `log-result` / `promote-finding` / `scope-check` / `supersession` / `fwer-audit` modes get gate updates per the TODO's "Skill target" fields).
   - `docs/_templates/experiment_section.md` (chronicle template — Gap 3 adds a falsifiability block here).
2. **Stability check against current HEAD.** The TODO's case studies were stable at commit `1165f88`. Run:
   - `git log --oneline 1165f88..HEAD -- docs/chem-tape/experiments-v2.md docs/chem-tape/findings.md Plans/prereg_*.md Plans/fwer_audit_*.md` to see whether any new chronicles / preregs / audits appeared since the TODO was written.
   - If new entries appeared that would add or retire a gap, update the TODO before drafting.
3. **Verify file writeability.** `.claude/skills/research-rigor/` is within the repo (`/Users/andreasronge/projects/folding-evolution/.claude/skills/research-rigor/`) and tracked by git — confirm via `ls -la .claude/skills/research-rigor/` that SKILL.md is present and writeable in the session's permission mode. If not writeable, stop and escalate before drafting.
4. **Confirm single-commit scope.** The TODO's "Sequencing recommendation" bundles all 9 gaps + template update + skill updates into one commit. Verify no in-progress branches or uncommitted work would complicate that before starting.

Once the checklist is clear, follow the "Sequencing recommendation" block at the end of the TODO.

---

## Gap 1 — §2b / §23: "row prose matches, numeric clause fails"

**Case.** `§v2.4-proxy-5a-followup-mid-bp` chronicle claimed it "matched" PLATEAU-MID on the row's prose ("Non-monotone staircase: two regimes or two competing mechanisms") even though the observed adjacent-cell differences {0.144, 0.092} failed the row's numeric tightness clause (<0.05). Codex flagged as §23 drift. Current language of principle 2b and 23 permits this gap because they describe the row-matching check at paragraph level, not at clause level.

**Proposed sub-principle (methodology §23-(iv) or new §23b).** "A pre-registered outcome row matches the observed data only when **every** numeric clause in the row is satisfied. Prose-match plus numeric-clause-fail is a grid-miss by §2b, not a match. When a row's prose anticipates a shape but its numeric clause is tighter than the observed signature, the prereg's outcome table was incomplete and principle 2b triggers: add a row in the next prereg for the prose-match × clause-fail cell, do not narrate the current result as a match."

**Skill target.** Research-rigor `log-result` mode gate: "Before writing 'Matches pre-registered outcome: X', enumerate each clause in row X and verify the observed data satisfies all of them. Prose-only matches fail the gate."

**Estimated effort.** 150-200 words in methodology.md; ~30 words of gate text in the skill.

---

## Gap 2 — §17 / §2: multi-variable confound disclosure

**Case.** `§v2.4-proxy-5b-crosstask` earlier draft proposed `mr=0.005 × gens=9000` as "budget-decoupling" from `mr=0.03 × gens=1500`. Codex noted: varying `mr` and `gens` jointly changes (a) per-tape expected mutation count, (b) selection opportunities per lineage, (c) crossover opportunities, (d) fixation time. Four process variables shift, not two. Calling the outcome "rate-vs-budget decoupling" was overreach; the true discrimination was narrower.

**Proposed sub-principle (methodology §17 sub-principle or §2-(iv)).** "When a prereg varies a nominal config field across cells, explicitly enumerate every derived process variable that changes across those cells at prereg time. If more than one derived variable shifts, the outcome discrimination is narrower than the nominal variable would suggest; the prereg's outcome rows must name the process-variable-bundle being discriminated, not the nominal field."

**Skill target.** Research-rigor `prereg` mode gate: "When the prereg varies a config field non-trivially (not just a seed block or hash-excluded default), list the derived process variables affected by that variation. If > 1, rewrite outcome names to reflect the bundle."

**Estimated effort.** 120-150 words in methodology.md; ~20 words of gate text.

---

## Gap 3 — §16: falsifiability gate for tentative mechanism names

**Case.** `§v2.4-proxy-5a-followup-mid-bp` chronicle introduced the tentative name "non-monotone single-mechanism cloud-destabilisation" (principle 16 renaming cycle). Codex flagged the name as too residual — it would survive any further data by just attaching qualifiers. Post-codex, I added 5 pre-committed falsifiable predictions (P-1..P-5) each tied to a specific upcoming test. This should be the standard pattern, not an ad-hoc codex response.

**Proposed sub-principle (methodology §16 sub-principle).** "When a chronicle commits to a tentative mechanism name (per the renaming cycle anticipated by §16), the chronicle must pre-commit at least 3 falsifiable predictions, each of which if violated would force a rename. Each prediction must name the specific experiment that would test it, even if that experiment is pending. Names without falsifiers are just-so stories — they survive any further data by qualifier-attachment and consume the principle-16 renaming budget without progress."

**Skill target.** Research-rigor `log-result` mode: when the chronicle proposes a mechanism-name rename, require the falsifiability block as a mandatory subsection (template update).

**Estimated effort.** 120-150 words in methodology.md; template update to `docs/_templates/experiment_section.md`.

---

## Gap 4 — §22: per-sweep test counting + authoritative-source rule

**Case.** The 2026-04-17 FWER audit (`Plans/fwer_audit_2026-04-17.md`) under-counted the F1 proxy-basin family by 2 tests. It treated `§v2.4-proxy-4c-replication` as zero contributions (omitted) even though the chronicle explicitly counted its Arm A preserve + BP_TOPK consume sweeps as 2 separate McNemar tests. My 2026-04-18 first-draft audit also miscounted (treated 4c as 1 test, not 2). Both errors flowed from the same gap: principle 22 doesn't explicitly state that a single prereg driving multiple independent sweeps contributes one family member per sweep, and doesn't establish the chronicle-vs-audit precedence rule.

**Proposed sub-principles (methodology §22 additions).**

(a) **Per-sweep counting convention.** "When a prereg produces multiple independent statistical tests (e.g., one McNemar per sweep across different arms / decoders / tasks), each test is a separate family member. The prereg must state its per-sweep test count explicitly. Multi-sweep preregs that omit this state their classification as ambiguous."

(b) **Authoritative-source rule.** "When an audit file's family-member count disagrees with the source chronicle's own FWER bookkeeping, the chronicle wins. Chronicles are commit-anchored to the data; audit files are meta-summaries that can go stale. Audits reconcile to chronicles, not the other way around."

**Skill target.** Research-rigor `fwer-audit` mode: (i) enumerate tests per sweep, not per prereg; (ii) cross-check audit counts against the chronicle layer and report disagreements.

**Estimated effort.** 200-250 words in methodology.md (two sub-principles); ~40 words of audit-mode guidance.

---

## Gap 5 — §4 / §2b: degenerate-success guard "letter vs intent"

**Case.** `§v2.4-proxy-5c-tournament-size` observed ts=2 produces F=20/20 but R_fit_999 ≈ 0.005 (solvers found, don't propagate). The prereg's degenerate-success guard for "tournament_size=2 exploration starvation" used `F < 18/20` as the SWAMPED detection criterion — which letter-passed (F=20/20) but whose intent (solver propagation) failed. The guard missed the regime it was designed to catch.

**Proposed sub-principle (methodology §4 sub-principle or §2b extension).** "A degenerate-success guard that uses a single criterion (e.g., F-only) must state explicitly which aspect of the regime it tests, and must add additional criteria when the guarded regime has multiple failure modes. The guard's criteria should be a conjunction, not a single gate; the prereg should verify at grid-design time that each guard's conjunction covers every failure mode the prose names. Single-criterion guards with multi-failure-mode targets are vulnerable to the 'letter-but-not-intent' failure pattern."

**Skill target.** Research-rigor `prereg` mode gate: "For each degenerate-success guard, check whether the detection criterion is a single gate or a conjunction. If single, list the guarded regime's known failure modes and verify the single gate detects each one. If it doesn't, add criteria."

**Estimated effort.** 100-150 words in methodology.md; ~25 words of gate text.

---

## Gap 6 — §25: grouping-script attribution in prereg §25 gates

**Case.** The 2026-04-18 engineering commit extended `analyze_5ab.py` to handle `ts`, `mr_gens`, `selmode`, `any:FIELD` grouping specs because `analyze_retention.py`'s `summarize_arm` only groups by `(arm, safe_pop_mode, seed_fraction)`. Multiple preregs (5b-crosstask, 5c-tournament-size, 5d) cited `analyze_retention.py` for per-cell grouping that it doesn't provide. Codex caught this. The fix was to update each prereg's §25 gate to cite the correct script (`analyze_5ab.py <axis> --include-holdout`), but principle 25 doesn't explicitly say "if the grouping axis isn't `(arm, spm, sf)`, name the grouping script too."

**Proposed sub-principle (methodology §25 clarification).** "When a prereg's metric commits to a per-cell breakdown, the §25 gate must name both (a) the metric-computing code path (the existing §25 requirement) AND (b) the grouping code path that produces the per-cell table. If the metric module's default `summarize_arm` (or equivalent) groups by axes narrower than the prereg's grid, name the grouping wrapper / script / function that covers the prereg's axis set. 'Produced directly by analyze_retention.py' is incomplete if the prereg's grid axes require a wrapper the module doesn't include by default."

**Skill target.** Research-rigor `prereg` mode §25 check: for each metric, verify both the compute and the grouping script/function; flag if the grouping is implicit.

**Estimated effort.** 60-80 words in methodology.md (clarification, not a new principle); ~20 words of gate text.

---

## Gap 7 — §8 / §23: "confirmatory test that fails to reject is still a family member"

**Case.** `§v2.4-proxy-5d v1` replication was pre-classified confirmatory; its null-rejection failed (FAIL-TO-REPLICATE). Open question: does it still count in the FWER family? Under standard Bonferroni, yes — it consumed α budget. But principle 22 as written doesn't address the "ran but did not reject" case explicitly. Future audits need this clarification.

**Proposed sub-principle (methodology §22 clarification).** "A confirmatory test that ran and failed to reject its null still counts as a family member — it consumed α budget regardless of outcome. The family's corrected α tightens whenever a new confirmatory test is registered, not only when it rejects. A FAIL-TO-REPLICATE outcome does not remove the test from the family; it produces a null finding (principle 24) alongside the unchanged family size."

**Skill target.** Research-rigor `fwer-audit` mode: include non-rejecting confirmatory tests in family count.

**Estimated effort.** 60-80 words in methodology.md; trivial audit-mode update.

---

## Gap 8 — §17: tested-set vs continuous-range smuggling in mechanism-name qualifiers

**Case.** The 2026-04-18 `findings.md#proxy-basin-attractor` entry's ACTIVE status line initially read: mechanism narrowed to "monotone single-mechanism cloud-destabilisation under BP_TOPK preserve **at selection pressure ≥ tournament_size=3**." The `≥ 3` continuous half-line extrapolated from **discrete tested values** ts ∈ {3, 5, 8} — all exploratory evidence from §v2.4-proxy-5c-tournament-size's effect-size classification. All four F1 confirmatory tests ran only at ts=3; ts ∈ {5, 8} was exploratory; ts > 8 was entirely untested. Codex pass 2 flagged this as mechanism-name smuggling: "a tested set gets promoted into an untested half-line." Fixed at commit `1165f88` to "at tested tournament sizes ∈ {3, 5, 8} (ts=2 fails; ts > 8 untested)." Principle 17 currently warns against overreach phrases in the abstract but doesn't name this specific sub-pattern where the smuggling happens **within** a discrete-tested variable by continuous-range rewriting.

**Proposed sub-principle (methodology §17 sub-principle, distinct from Gap 2).** "When a mechanism-name qualifier names a threshold or range on a variable that was tested only at discrete values, the qualifier must scope to the tested set explicitly, not to a continuous range above/below a tested endpoint. 'At tested values ∈ {X, Y, Z}' is honest; 'at ≥ X' smuggles untested values between tested points and extrapolates beyond the tested maximum. This applies especially to integer-valued config fields (tournament_size, topk, budget, etc.) where the between-tested-values are excluded by config type, and to any qualifier that upgrades exploratory evidence into ACTIVE-claim scope — tested-set discreteness must survive that upgrade."

**Skill target.** Research-rigor `log-result` mode gate: "Before writing a mechanism-name qualifier for a tested variable, enumerate the tested values for that variable across the supporting experiments. If the qualifier uses `≥` / `>` / `<` / `≤` against a tested endpoint, rewrite it as `∈ {tested values}` unless a new experiment explicitly tested the range claim. Flag any exploratory-classified evidence that appears in the qualifier — exploratory evidence cannot raise the qualifier's scope above `at tested values`."

**Estimated effort.** 120-150 words in methodology.md; ~30 words of gate text. Falls naturally next to Gap 2 (multi-variable confound) since both are §17 sub-principles about scope-tag integrity on tested vs. extrapolated claims.

---

## Gap 9 — §23 / §2b: status-line fidelity when body flags a grid-miss

**Case.** The 2026-04-18 `§v2.4-proxy-5c-tournament-size` chronicle's initial status line was a bare `PASS`. The chronicle body explicitly flagged that the observed data matched the PRESSURE-MONOTONE-R_FIT row **on the letter of its clauses only** — the actual shape was cliff+plateau (ts=2 at 0.005; ts ∈ {3, 5, 8} at 0.72-0.75), which is a principle-2b grid-miss rather than a clean row match. The chronicle also self-applied Gap 5 (SWAMPED-guard letter-vs-intent) to flag that the prereg's F-only guard missed the ts=2 propagation-failure regime. A reader scanning only the status line saw "PASS" and could easily over-read it as unqualified confirmatory support for the narrowed mechanism name — when in fact the chronicle body was doing the opposite. Codex pass 2 flagged this as letter-vs-intent drift at the **status-line surface**, distinct from Gap 1 which applies at the "Matches pre-registered outcome" surface. Fixed at commit `1165f88` by expanding the status line to "`PASS` (matched on letter of PRESSURE-MONOTONE-R_FIT row clauses; **grid-miss on shape** — observed cliff+plateau signature not pre-registered as its own row; principle-2b flag documented in the Result section)."

**Proposed sub-principle (methodology §23 sub-principle; may fold into Gap 1 if the session deems it a sub-pattern rather than a separate principle).** "When a chronicle's status token would normally be `PASS` but the Result/Interpretation section flags a principle-2b grid-miss, a principle-4 degenerate-success-guard letter-vs-intent failure, or any similar 'matched-on-letter-not-intent' qualification, the status line must carry the qualifier inline (in parentheses on the same line), not only in the Result section. The standardized status vocabulary (PASS / FAIL / INCONCLUSIVE / SUPERSEDED / FALSIFIED) is grep-parsed and indexed — a scan-only reader who never drills into the body must still see the qualifier. Bare status tokens where the body substantively qualifies them fail the gate."

**Skill target.** Research-rigor `log-result` mode gate: "After drafting the Result + Interpretation sections, re-read them for any 'matched on letter,' 'grid-miss,' 'guard-letter-vs-intent,' or similar qualifier on the headline verdict. If present, the status line must repeat that qualifier inline. Bare status tokens with body qualifications fail this gate."

**Estimated effort.** 80-120 words in methodology.md; ~20 words of gate text. Strongly consider folding into Gap 1 as a sub-case of the "numeric clause fail" pattern (both are surface-level letter-vs-intent drift); keeping them separate is justified only if the session concludes status-line-grepability is a distinct enough concern to warrant its own sub-principle.

---

## Meta-gap — research-rigor skill's log-result codex gate is "strongly recommended," not mandatory

**Case.** The codex review in this session caught 6 P1 issues post-draft. Had it been skipped (or the session had no codex binary), those issues would have shipped to disk silently. The skill's log-result mode lists codex review under gate (7) but doesn't make it a strict commit-blocker.

**Proposed clarification (research-rigor skill, log-result mode).** Make codex gate explicit as a BLOCKER for `log-result` mode on any chronicle that will feed a findings.md entry (positive or negative). Add a "codex-unavailable" fallback path that requires an explicit user acknowledgment of the skipped gate, logged in the chronicle's audit trail.

**Estimated effort.** Skill-document edit only; ~100 words of text.

---

## Sequencing recommendation

Do these in a dedicated session, NOT piecemeal. Drafting 9 sub-principles requires consistent language + cross-referencing + template updates — the kind of careful prose that deteriorates when attempted between other tasks.

Suggested order per session:
1. Run the **Session-start checklist** at the top of this document (~15 min).
2. Draft gaps 1, 5, 6 first (§2b / §23 / §4 / §25) — these are the most mechanical and have the clearest case evidence.
3. Draft gaps 2, 3, 8 (§17 / §16) — these introduce new sub-principles that need more careful framing against existing text. Gap 8 is adjacent to Gap 2; consider drafting them in the same pass for consistent §17 voice.
4. Draft gap 4 (§22 additions) — touches FWER machinery; most sensitive to wording drift.
5. Draft gap 7 + gap 9 + meta-gap — short clarifications at the end. Gap 9 may fold into Gap 1's body as a sub-case; decide during drafting.
6. Update `docs/_templates/experiment_section.md` with the falsifiability block (gap 3).
7. Update research-rigor skill modes per targets above (`prereg` / `log-result` / `fwer-audit`).
8. Bundle all changes into one commit with a single `methodology` + `skill` diff.

**Estimated total session effort:** 1.5-2.5 hours uninterrupted (increased from 1.5-2h to account for gaps 8 + 9).

**Prerequisite.** Before the session, confirm the case-studies above are stable in their current form (no additional §v2.4-proxy-5* results have overturned them since the TODO's final state at commit `1165f88`). The §v2.4-proxy-5d v1 FAIL-TO-REPLICATE result + the §v2.4-proxy-5c-tournament-size cliff+plateau result + the codex-pass-2 P1/P2 corrections from 2026-04-18 are the last inputs; no other pending sweeps should shift the evidentiary base for these gaps. Run the stability check from the Session-start checklist before drafting.

## Definition of done

The session is done when **all** of the following are true and committed:

1. `docs/methodology.md` contains the 9 sub-principle additions/clarifications (gaps 1-9) at the target locations named in each gap's "Proposed sub-principle" field. Each addition follows the methodology.md voice (Case + Takeaway pattern or explicit sub-principle with matching style).
2. `.claude/skills/research-rigor/SKILL.md` has gate-text updates in the affected modes (`prereg` / `log-result` / `fwer-audit`) matching the "Skill target" field of each gap. The meta-gap's codex-as-mandatory-gate language is in place in `log-result` mode.
3. `docs/_templates/experiment_section.md` has a falsifiability-block template subsection for use when a chronicle introduces a tentative mechanism name (gap 3).
4. All changes bundled into **one commit** titled "methodology: add sub-principles from 2026-04-18 session (gaps 1-9)" or similar, with the TODO file referenced in the commit message.
5. After committing, mark this TODO's `Status:` line as `DONE · closed by commit <sha>` and leave the file in place for reasoning trail (do not delete — follows methodology §13 retention pattern for the methodology change itself).

**Scope boundary on the dedicated session.** This session is for methodology + skill + template updates only. Do not:
- Open new research questions (P-4 / P-5 / §v2.4-proxy-5d v2 / plasticity-1a engineering unblock — all out of scope).
- Re-chronicle past experiments to apply the new sub-principles retroactively (the existing chronicles remain at their prior state; the new sub-principles apply prospectively to future experiments and to any new same-day amendments).
- Re-run the FWER audit (F1 is size 4 at `fwer_audit_2026-04-18.md`'s post-5d-run addendum; no change needed).

---

## References

- `docs/methodology.md` — the 27-principle ledger being improved.
- `docs/_templates/experiment_section.md` — chronicle template (gap 3 template update).
- `.claude/skills/research-rigor/SKILL.md` — skill modes (multiple gate updates).
- `docs/chem-tape/experiments-v2.md` §v2.4-proxy-5a-followup-mid-bp — case study for gaps 1, 3.
- `docs/chem-tape/experiments-v2.md` §v2.4-proxy-5d v1 — case study for gap 7 (non-rejecting confirmatory).
- `docs/chem-tape/experiments-v2.md` §v2.4-proxy-5c-tournament-size — case study for gaps 5, 9 (SWAMPED letter-vs-intent + bare-status grid-miss).
- `docs/chem-tape/findings.md` `proxy-basin-attractor` entry (post-`1165f88` state) — case study for gap 8 (tested-set vs continuous-range smuggling).
- `Plans/prereg_v2-4-proxy-5b-crosstask.md` — case study for gap 2.
- `Plans/prereg_v2-4-proxy-5c-tournament-size.md` — case study for gap 5.
- `Plans/prereg_v2-4-proxy-5d-followup-cloud-reexpansion.md` — case study for gap 7.
- `Plans/fwer_audit_2026-04-17.md` (superseded) + `fwer_audit_2026-04-18.md` — case studies for gap 4.
- `experiments/chem_tape/analyze_5ab.py` + `analyze_retention.py` — case studies for gap 6.
- Commit `1165f88` — final state of the 2026-04-18 session; commit message documents codex pass 2 P1/P2 findings that introduced gaps 8 and 9. A fresh session can read the commit message as a self-contained description of both gaps.
