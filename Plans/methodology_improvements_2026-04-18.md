# Methodology & research-rigor skill improvements — TODO for a dedicated session

**Status:** TODO · drafted 2026-04-18 · to be addressed in a standalone work session after the current chem-tape v2 batch stabilises.

**Scope.** Systemic gaps surfaced during the 2026-04-18 session's codex adversarial review + the §v2.4-proxy-5c-tournament-size result. Each gap appeared at least once in recent work and is predicted to recur without an explicit codified guardrail. Genuinely one-off code-review catches are not in this list.

**Principle.** Methodology edits should not be rushed. The items below are collected here as case-referenced proposals so a dedicated session can draft new sub-principles against concrete examples rather than in the abstract.

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

## Meta-gap — research-rigor skill's log-result codex gate is "strongly recommended," not mandatory

**Case.** The codex review in this session caught 6 P1 issues post-draft. Had it been skipped (or the session had no codex binary), those issues would have shipped to disk silently. The skill's log-result mode lists codex review under gate (7) but doesn't make it a strict commit-blocker.

**Proposed clarification (research-rigor skill, log-result mode).** Make codex gate explicit as a BLOCKER for `log-result` mode on any chronicle that will feed a findings.md entry (positive or negative). Add a "codex-unavailable" fallback path that requires an explicit user acknowledgment of the skipped gate, logged in the chronicle's audit trail.

**Estimated effort.** Skill-document edit only; ~100 words of text.

---

## Sequencing recommendation

Do these in a dedicated session, NOT piecemeal. Drafting 7 sub-principles requires consistent language + cross-referencing + template updates — the kind of careful prose that deteriorates when attempted between other tasks.

Suggested order per session:
1. Read methodology.md end-to-end once (~15 min).
2. Draft gaps 1, 5, 6 first (§2b / §23 / §4 / §25) — these are the most mechanical and have the clearest case evidence.
3. Draft gaps 2, 3 (§17 / §16) — these introduce new sub-principles that need more careful framing against existing text.
4. Draft gap 4 (§22 additions) — touches FWER machinery; most sensitive to wording drift.
5. Draft gap 7 + meta-gap — short clarifications at the end.
6. Update `docs/_templates/experiment_section.md` with the falsifiability block (gap 3).
7. Update research-rigor skill modes per targets above.
8. Bundle all changes into one commit with a single `methodology` + `skill` diff.

**Estimated total session effort:** 1.5-2 hours uninterrupted.

**Prerequisite.** Before the session, confirm the 5 case-studies above are stable in their current form (no additional §v2.4-proxy-5* results overturn them). The §v2.4-proxy-5d v1 FAIL-TO-REPLICATE result + the §v2.4-proxy-5c-tournament-size cliff+plateau result from 2026-04-18 are the last inputs; no other pending sweeps should shift the evidentiary base for these gaps.

---

## References

- `docs/methodology.md` — the 27-principle ledger being improved.
- `docs/_templates/experiment_section.md` — chronicle template (gap 3 template update).
- `.claude/skills/research-rigor/SKILL.md` — skill modes (multiple gate updates).
- `docs/chem-tape/experiments-v2.md` §v2.4-proxy-5a-followup-mid-bp — case study for gaps 1, 3.
- `Plans/prereg_v2-4-proxy-5b-crosstask.md` — case study for gap 2.
- `Plans/prereg_v2-4-proxy-5c-tournament-size.md` — case study for gap 5.
- `Plans/prereg_v2-4-proxy-5d-followup-cloud-reexpansion.md` — case study for gap 7.
- `Plans/fwer_audit_2026-04-17.md` (superseded) + `fwer_audit_2026-04-18.md` — case studies for gap 4.
- `experiments/chem_tape/analyze_5ab.py` + `analyze_retention.py` — case studies for gap 6.
