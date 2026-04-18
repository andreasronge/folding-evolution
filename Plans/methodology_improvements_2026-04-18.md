# Methodology & research-rigor skill improvements — TODO for a dedicated session

**Status:** TODO · drafted 2026-04-18 · amended 2026-04-18 (pressure-test round 2) · to be addressed in a standalone work session after the current chem-tape v2 batch stabilises.

**Scope.** Systemic gaps surfaced during the 2026-04-18 session's codex adversarial review + the §v2.4-proxy-5c-tournament-size result. Each gap appeared at least once in recent work and is predicted to recur without an explicit codified guardrail. Genuinely one-off code-review catches are not in this list.

**Principle.** Methodology edits should not be rushed. The items below are collected here as case-referenced proposals so a dedicated session can draft new sub-principles against concrete examples rather than in the abstract.

**Amendments (pressure-test round 2, 2026-04-18).** Reviewer Q1–Q5 resolved pre-session:

- **Q1 + Q2** (umbrella): Gaps 1, 5, 9 consolidate into one new principle **"Letter-vs-intent drift across chronicle surfaces"** (§28 or §23b) with three enumerated sub-clauses (a)(b)(c). Decision made pre-session, not mid-draft. Leaves room for future surfaces (e.g., scope-tag grep-parseability) without re-architecting.
- **Q3** (carve-out): Gap 4 sub-principle (b) updated — audit surfaces contestation when it identifies a chronicle-layer error, rather than auto-deferring. Full text in Gap 4 below.
- **Q4** (downscope): Gap 7 reduces to a one-line §22 clarification (~30 words); no dedicated sub-principle. Frees drafting budget.
- **Q5** (descope): Meta-gap (mandatory-codex-gate) deferred to a future skill-workflow session — not shipped in this session. Reframed as a bullet in the "Deferred" block at bottom.

**Net session scope:** 7 methodology additions (1 umbrella + gaps 2, 3, 4, 6, 7-clarification, 8) + skill-gate updates + template update. Single commit preserved. Estimated total effort revised to 1.5–2h uninterrupted (down from 1.5–2.5h) because Q4 + Q5 shed ~1 gap's worth of drafting.

---

## Session-start checklist

Run these before drafting any new sub-principle text. ~15 min total.

1. **Read in order:**
   - `docs/methodology.md` end-to-end (current 27-principle ledger — know the voice and existing sub-principle style before adding to it).
   - This TODO file end-to-end, **including the amendments block above**.
   - `.claude/skills/research-rigor/SKILL.md` (the skill whose `prereg` / `log-result` / `promote-finding` / `scope-check` / `supersession` / `fwer-audit` modes get gate updates per each gap/sub-clause's "Skill target" field).
   - `docs/_templates/experiment_section.md` (chronicle template — Gap 3 adds a falsifiability block here).
2. **Stability check against current HEAD.** The TODO's case studies were stable at commit `1165f88`. Run:
   - `git log --oneline 1165f88..HEAD -- docs/chem-tape/experiments-v2.md docs/chem-tape/findings.md Plans/prereg_*.md Plans/fwer_audit_*.md` to see whether any new chronicles / preregs / audits appeared since the TODO was written.
   - Also check for new entries in `docs/methodology.md` or `docs/_templates/` that would affect target-location calculations.
   - If new entries appeared that would add or retire a gap, update the TODO before drafting.
3. **Verify file writeability.** `.claude/skills/research-rigor/` is within the repo (`/Users/andreasronge/projects/folding-evolution/.claude/skills/research-rigor/`) and tracked by git — confirm via `ls -la .claude/skills/research-rigor/` that SKILL.md is present and writeable in the session's permission mode. If not writeable, stop and escalate before drafting.
4. **Confirm single-commit scope.** The TODO's "Sequencing recommendation" bundles the umbrella + 6 standalone gap additions/clarifications + template update + skill updates into one commit. Verify no in-progress branches or uncommitted work would complicate that before starting. (Partial-ship permission per sequencing step below is a valid fallback if any single gap over-runs.)

Once the checklist is clear, follow the "Sequencing recommendation" block at the end of the TODO.

---

## Umbrella principle — Letter-vs-intent drift across chronicle surfaces (consolidates original gaps 1, 5, 9)

**Rationale.** Gaps 1, 5, 9 are three instances of the same failure pattern at different chronicle surfaces: a surface-level token or clause matches the letter of a pre-registered check while the underlying intent fails. Drafted as one new principle (§28 or §23b) with three enumerated sub-clauses — more coherent than three scattered §-additions, and extensible (future surfaces added by supersession per §13).

**Proposed principle (§28 or §23b — "Letter-vs-intent drift across chronicle surfaces").** "A chronicle must detect and flag letter-vs-intent drift at every surface where a token, clause, or numeric criterion can match the letter of a pre-registered check while the underlying intent fails. The following surfaces are enumerated; future surfaces must be added by supersession (methodology §13) when discovered. Sub-clauses (a), (b), (c) describe the currently-enumerated surfaces with their guard rules."

### Sub-clause (a) — Row-match clauses (originally Gap 1)

**Case.** `§v2.4-proxy-5a-followup-mid-bp` chronicle claimed it "matched" PLATEAU-MID on the row's prose ("Non-monotone staircase: two regimes or two competing mechanisms") even though the observed adjacent-cell differences {0.144, 0.092} failed the row's numeric tightness clause (<0.05). Codex flagged as §23 drift.

**Rule.** "A pre-registered outcome row matches the observed data only when **every** numeric clause in the row is satisfied. Prose-match plus numeric-clause-fail is a grid-miss by §2b, not a match. When a row's prose anticipates a shape but its numeric clause is tighter than the observed signature, the prereg's outcome table was incomplete and principle 2b triggers: add a row in the next prereg for the prose-match × clause-fail cell, do not narrate the current result as a match."

**Skill target.** Research-rigor `log-result` mode gate: "Before writing 'Matches pre-registered outcome: X', enumerate each clause in row X and verify the observed data satisfies all of them. Prose-only matches fail the gate."

### Sub-clause (b) — Degenerate-success-guard criteria (originally Gap 5)

**Case.** `§v2.4-proxy-5c-tournament-size` observed ts=2 produces F=20/20 but R_fit_999 ≈ 0.005 (solvers found, don't propagate). The prereg's degenerate-success guard for "tournament_size=2 exploration starvation" used `F < 18/20` as the SWAMPED detection criterion — which letter-passed (F=20/20) but whose intent (solver propagation) failed. The guard missed the regime it was designed to catch.

**Rule.** "A degenerate-success guard that uses a single criterion (e.g., F-only) must state explicitly which aspect of the regime it tests, and must add additional criteria when the guarded regime has multiple failure modes. The guard's criteria should be a conjunction, not a single gate; the prereg should verify at grid-design time that each guard's conjunction covers every failure mode the prose names. Single-criterion guards with multi-failure-mode targets are vulnerable to the 'letter-but-not-intent' failure pattern."

**Skill target.** Research-rigor `prereg` mode gate: "For each degenerate-success guard, check whether the detection criterion is a single gate or a conjunction. If single, list the guarded regime's known failure modes and verify the single gate detects each one. If it doesn't, add criteria."

### Sub-clause (c) — Status-line tokens (originally Gap 9)

**Case.** The 2026-04-18 `§v2.4-proxy-5c-tournament-size` chronicle's initial status line was a bare `PASS`. The chronicle body explicitly flagged that the observed data matched the PRESSURE-MONOTONE-R_FIT row **on the letter of its clauses only** — the actual shape was cliff+plateau (ts=2 at 0.005; ts ∈ {3, 5, 8} at 0.72–0.75), which is a principle-2b grid-miss rather than a clean row match. The chronicle also self-applied sub-clause (b) to flag the F-only guard's letter-pass at ts=2. A reader scanning only the status line saw "PASS" and could easily over-read it as unqualified confirmatory support for the narrowed mechanism name. Codex pass 2 flagged this as letter-vs-intent drift at the **status-line surface**. Fixed at commit `1165f88` by expanding the status line to "`PASS` (matched on letter of PRESSURE-MONOTONE-R_FIT row clauses; **grid-miss on shape** — observed cliff+plateau signature not pre-registered as its own row; principle-2b flag documented in the Result section)."

**Rule.** "When a chronicle's status token would normally be `PASS` but the Result/Interpretation section flags a principle-2b grid-miss, a sub-clause (b) letter-vs-intent failure, or any similar 'matched-on-letter-not-intent' qualification, the status line must carry the qualifier inline (in parentheses on the same line), not only in the Result section. The standardized status vocabulary (PASS / FAIL / INCONCLUSIVE / SUPERSEDED / FALSIFIED) is grep-parsed and indexed — a scan-only reader who never drills into the body must still see the qualifier. Bare status tokens where the body substantively qualifies them fail the gate."

**Skill target.** Research-rigor `log-result` mode gate: "After drafting the Result + Interpretation sections, re-read them for any 'matched on letter,' 'grid-miss,' 'guard-letter-vs-intent,' or similar qualifier on the headline verdict. If present, the status line must repeat that qualifier inline. Bare status tokens with body qualifications fail this gate."

### Umbrella — estimated effort

250–350 words in methodology.md for the umbrella (framing prose + three sub-clauses); ~75 words of gate text across three skill-mode entries. Net roughly equal to 3 separate sub-principles but with one framing block, so expected to read more coherently.

---

## Gap 2 — §17 / §2: multi-variable confound disclosure

**Case.** `§v2.4-proxy-5b-crosstask` earlier draft proposed `mr=0.005 × gens=9000` as "budget-decoupling" from `mr=0.03 × gens=1500`. Codex noted: varying `mr` and `gens` jointly changes (a) per-tape expected mutation count, (b) selection opportunities per lineage, (c) crossover opportunities, (d) fixation time. Four process variables shift, not two. Calling the outcome "rate-vs-budget decoupling" was overreach; the true discrimination was narrower.

**Proposed sub-principle (methodology §17 sub-principle or §2-(iv)).** "When a prereg varies a nominal config field across cells, explicitly enumerate every derived process variable that changes across those cells at prereg time. If more than one derived variable shifts, the outcome discrimination is narrower than the nominal variable would suggest; the prereg's outcome rows must name the process-variable-bundle being discriminated, not the nominal field."

**Skill target.** Research-rigor `prereg` mode gate: "When the prereg varies a config field non-trivially (not just a seed block or hash-excluded default), list the derived process variables affected by that variation. If > 1, rewrite outcome names to reflect the bundle."

**Estimated effort.** 120–150 words in methodology.md; ~20 words of gate text.

---

## Gap 3 — §16: falsifiability gate for tentative mechanism names

**Case.** `§v2.4-proxy-5a-followup-mid-bp` chronicle introduced the tentative name "non-monotone single-mechanism cloud-destabilisation" (principle 16 renaming cycle). Codex flagged the name as too residual — it would survive any further data by just attaching qualifiers. Post-codex, I added 5 pre-committed falsifiable predictions (P-1..P-5) each tied to a specific upcoming test. This should be the standard pattern, not an ad-hoc codex response.

**Proposed sub-principle (methodology §16 sub-principle).** "When a chronicle commits to a tentative mechanism name (per the renaming cycle anticipated by §16), the chronicle must pre-commit at least 3 falsifiable predictions, each of which if violated would force a rename. Each prediction must name the specific experiment that would test it, even if that experiment is pending. Names without falsifiers are just-so stories — they survive any further data by qualifier-attachment and consume the principle-16 renaming budget without progress."

**Skill target.** Research-rigor `log-result` mode: when the chronicle proposes a mechanism-name rename, require the falsifiability block as a mandatory subsection (template update).

**Estimated effort.** 120–150 words in methodology.md; template update to `docs/_templates/experiment_section.md`.

---

## Gap 4 — §22: per-sweep test counting + authoritative-source rule (with chronicle-layer-error carve-out)

**Case.** The 2026-04-17 FWER audit (`Plans/fwer_audit_2026-04-17.md`) under-counted the F1 proxy-basin family by 2 tests. It treated `§v2.4-proxy-4c-replication` as zero contributions (omitted) even though the chronicle explicitly counted its Arm A preserve + BP_TOPK consume sweeps as 2 separate McNemar tests. My 2026-04-18 first-draft audit also miscounted (treated 4c as 1 test, not 2). Both errors flowed from the same gap: principle 22 doesn't explicitly state that a single prereg driving multiple independent sweeps contributes one family member per sweep, and doesn't establish the chronicle-vs-audit precedence rule.

**Proposed sub-principles (methodology §22 additions).**

(a) **Per-sweep counting convention.** "When a prereg produces multiple independent statistical tests (e.g., one McNemar per sweep across different arms / decoders / tasks), each test is a separate family member. The prereg must state its per-sweep test count explicitly. Multi-sweep preregs that omit this state their classification as ambiguous."

(b) **Authoritative-source rule (with carve-out for chronicle-layer errors — Q3 resolution).** "When an audit's family-member count disagrees with the source chronicle's FWER bookkeeping, the chronicle is the default authority provided its bookkeeping appeals to standard Bonferroni conventions and is internally consistent. When the audit identifies a specific chronicle-layer error (overcount, misclassification of exploratory-as-confirmatory, non-standard counting convention), the audit's role is to surface the contestation for explicit resolution — not to defer automatically. Resolution requires either (i) a chronicle amendment (methodology §13 supersession if load-bearing) or (ii) an explicit audit-layer override documented with the contested count's grounding."

**Skill target.** Research-rigor `fwer-audit` mode: (i) enumerate tests per sweep, not per prereg; (ii) cross-check audit counts against the chronicle layer and report disagreements; (iii) when a disagreement is identified as a chronicle-layer error (not a methodology convention difference), flag for explicit resolution (amendment or audit-layer override) rather than auto-deferring to the chronicle.

**Estimated effort.** 250–300 words in methodology.md (two sub-principles; (b) expanded by ~80 words for the carve-out); ~50 words of audit-mode guidance (expanded by ~10 words for the error-handling path).

---

## Gap 6 — §25: grouping-script attribution in prereg §25 gates

**Case.** The 2026-04-18 engineering commit extended `analyze_5ab.py` to handle `ts`, `mr_gens`, `selmode`, `any:FIELD` grouping specs because `analyze_retention.py`'s `summarize_arm` only groups by `(arm, safe_pop_mode, seed_fraction)`. Multiple preregs (5b-crosstask, 5c-tournament-size, 5d) cited `analyze_retention.py` for per-cell grouping that it doesn't provide. Codex caught this. The fix was to update each prereg's §25 gate to cite the correct script (`analyze_5ab.py <axis> --include-holdout`), but principle 25 doesn't explicitly say "if the grouping axis isn't `(arm, spm, sf)`, name the grouping script too."

**Proposed sub-principle (methodology §25 clarification).** "When a prereg's metric commits to a per-cell breakdown, the §25 gate must name both (a) the metric-computing code path (the existing §25 requirement) AND (b) the grouping code path that produces the per-cell table. If the metric module's default `summarize_arm` (or equivalent) groups by axes narrower than the prereg's grid, name the grouping wrapper / script / function that covers the prereg's axis set. 'Produced directly by analyze_retention.py' is incomplete if the prereg's grid axes require a wrapper the module doesn't include by default."

**Skill target.** Research-rigor `prereg` mode §25 check: for each metric, verify both the compute and the grouping script/function; flag if the grouping is implicit.

**Estimated effort.** 60–80 words in methodology.md (clarification, not a new principle); ~20 words of gate text.

---

## Gap 7 — §22 one-line clarification: confirmatory family membership at commit-time (downscoped per Q4)

**Case.** `§v2.4-proxy-5d v1` replication was pre-classified confirmatory; its null-rejection failed (FAIL-TO-REPLICATE). Open question: does it still count in the FWER family? Under standard Bonferroni, yes — it consumed α budget. Principle 22 as written doesn't address the "ran but did not reject" case explicitly.

**Proposed clarification (methodology §22 inline, no new sub-principle — Q4 resolution).** "§22 clarification: confirmatory family membership is determined at prereg-commit time, not at result-rejection time. A confirmatory test that runs counts in the family regardless of rejection outcome."

**Skill target.** Research-rigor `fwer-audit` mode: include non-rejecting confirmatory tests in family count.

**Estimated effort.** ~30 words inline in §22; trivial audit-mode update. (Down from 60–80 words + a separate sub-principle block per Q4 downscope.)

---

## Gap 8 — §17: tested-set vs continuous-range smuggling in mechanism-name qualifiers

**Case.** The 2026-04-18 `findings.md#proxy-basin-attractor` entry's ACTIVE status line initially read: mechanism narrowed to "monotone single-mechanism cloud-destabilisation under BP_TOPK preserve **at selection pressure ≥ tournament_size=3**." The `≥ 3` continuous half-line extrapolated from **discrete tested values** ts ∈ {3, 5, 8} — all exploratory evidence from §v2.4-proxy-5c-tournament-size's effect-size classification. All four F1 confirmatory tests ran only at ts=3; ts ∈ {5, 8} was exploratory; ts > 8 was entirely untested. Codex pass 2 flagged this as mechanism-name smuggling: "a tested set gets promoted into an untested half-line." Fixed at commit `1165f88` to "at tested tournament sizes ∈ {3, 5, 8} (ts=2 fails; ts > 8 untested)." Principle 17 currently warns against overreach phrases in the abstract but doesn't name this specific sub-pattern where the smuggling happens **within** a discrete-tested variable by continuous-range rewriting.

**Proposed sub-principle (methodology §17 sub-principle, distinct from Gap 2).** "When a mechanism-name qualifier names a threshold or range on a variable that was tested only at discrete values, the qualifier must scope to the tested set explicitly, not to a continuous range above/below a tested endpoint. 'At tested values ∈ {X, Y, Z}' is honest; 'at ≥ X' smuggles untested values between tested points and extrapolates beyond the tested maximum. This applies especially to integer-valued config fields (tournament_size, topk, budget, etc.) where the between-tested-values are excluded by config type, and to any qualifier that upgrades exploratory evidence into ACTIVE-claim scope — tested-set discreteness must survive that upgrade."

**Skill target.** Research-rigor `log-result` mode gate: "Before writing a mechanism-name qualifier for a tested variable, enumerate the tested values for that variable across the supporting experiments. If the qualifier uses `≥` / `>` / `<` / `≤` against a tested endpoint, rewrite it as `∈ {tested values}` unless a new experiment explicitly tested the range claim. Flag any exploratory-classified evidence that appears in the qualifier — exploratory evidence cannot raise the qualifier's scope above `at tested values`."

**Estimated effort.** 120–150 words in methodology.md; ~30 words of gate text. Falls naturally next to Gap 2 (multi-variable confound) since both are §17 sub-principles about scope-tag integrity on tested vs. extrapolated claims — draft them in the same pass for consistent §17 voice.

---

## Deferred — mandatory-codex-gate (originally meta-gap; deferred per Q5)

**Not shipped in this session.** The original meta-gap proposed making codex review a strict BLOCKER for `log-result` mode on any chronicle feeding a findings.md entry. Pressure-test round 2 (Q5) concluded this is a workflow change exceeding the ~100-word estimate and needs actual design, not just a mention:

- Audit-trail format (e.g., required chronicle line: `Codex review: {DONE sha=<shortsha> | DEFERRED reason=<reason> acknowledged=<user>}`).
- Trigger conditions (findings-layer-bound chronicle = blocker; exploratory chronicle = recommended).
- Fallback qualifications (binary missing vs. network failure vs. rate-limit vs. user-declined — same treatment or different?).
- Escalation if deferred (queue a later codex-review commit before findings promotion).

**Reframed action.** This is now a standalone item for a later skill-workflow session. The present session does **not** touch `log-result` mode's codex gate; it remains "strongly recommended" as currently written. A follow-up TODO should be opened once a draft design exists for the audit-trail format and trigger conditions.

**Estimated effort for later session.** 300–400 words of skill-document text + test cases; one dedicated session, not bundled with methodology edits.

---

## Sequencing recommendation

Do these in a dedicated session, NOT piecemeal. Drafting the umbrella + standalone sub-principles requires consistent language + cross-referencing + template updates — the kind of careful prose that deteriorates when attempted between other tasks.

Suggested order per session (revised for umbrella + Q-endorsed sub-steps):

1. Run the **Session-start checklist** at the top of this document (~15 min).
2. **Draft the umbrella principle first** (§28 or §23b — framing + sub-clauses (a)(b)(c)). This is the largest single prose block (250–350 words) and sets the voice for the mechanical drafts that follow. Includes 3 skill-gate updates (one per sub-clause).
3. Draft gap 6 (§25 clarification) — mechanical, short. Updates `prereg` mode gate.
4. **Mid-session checkpoint (Q-endorsed #2).** 5-minute re-read of the umbrella + gap-6 draft prose before moving to §17/§22. Voice drift discovered at the last gap is expensive to unwind.
5. Draft gaps 2 + 8 together (§17 sub-principles) for consistent §17 voice. Gap 2 (multi-variable confound) and Gap 8 (tested-set vs. continuous-range smuggling) are both about scope-tag integrity on extrapolated claims.
6. Draft gap 3 (§16 falsifiability gate) — needs careful framing against the existing §16 renaming-cycle text.
7. Draft gap 4 (§22 additions: per-sweep counting + authoritative-source rule **with the chronicle-layer-error carve-out**) — touches FWER machinery; most sensitive to wording drift.
8. Draft gap 7 (§22 one-line clarification). Inline addition; no new sub-principle block.
9. Update `docs/_templates/experiment_section.md` with the falsifiability block (gap 3).
10. Update research-rigor skill modes per targets above (`prereg` / `log-result` / `fwer-audit`). **Codex-blocker meta-gap explicitly NOT touched** (deferred — see Deferred block).
11. Add **methodology → TODO back-ref (Q-endorsed #4).** One-line pointer in methodology.md's new §28 (or wherever the umbrella lands): `> See Plans/methodology_improvements_2026-04-18.md for the drafting rationale and case studies behind this principle.` Same for each modified §17 / §22 / §25 sub-principle. Provenance trail makes future methodology audits tractable.
12. Bundle all changes into one commit with a single `methodology` + `skill` diff.

**Gate-against-case validation (Q-endorsed #1) — ongoing throughout steps 2, 3, 5, 6, 7, 8, 10.** After drafting each skill-gate sentence, mentally apply it to the case study that motivated the gap/sub-clause. If the gate as written wouldn't visibly flag that case, rewrite. This is the cheapest catch-drift mechanism available and must be done inline, not batched at session end.

**Partial-ship permission (Q-endorsed #3).** If any gap turns harder than estimated, ship the completed subset + the remaining gaps as a follow-up TODO entry. **Don't rush drafts to hit the single-commit goal.** The single-commit scope is a preference, not a constraint; voice coherence matters more. If invoked, update the Status line (see Definition of done #6).

**Estimated total session effort:** 1.5–2h uninterrupted (revised down from 1.5–2.5h after Q4 + Q5 scope reduction; umbrella is net-neutral vs. three separate drafts).

**Prerequisite.** Before the session, confirm the case-studies above are stable in their current form (no additional §v2.4-proxy-5* results have overturned them since the TODO's final state at commit `1165f88`). The §v2.4-proxy-5d v1 FAIL-TO-REPLICATE result + the §v2.4-proxy-5c-tournament-size cliff+plateau result + the codex-pass-2 P1/P2 corrections from 2026-04-18 are the last inputs; no other pending sweeps should shift the evidentiary base for these gaps. Run the stability check from the Session-start checklist before drafting.

---

## Definition of done

The session is done when **all** of the following are true and committed:

1. `docs/methodology.md` contains:
   - The umbrella principle (§28 or §23b) with three enumerated sub-clauses (a)(b)(c) replacing what would have been separate gaps 1, 5, 9 sub-principles.
   - Gap 2 (§17 sub-principle or §2-(iv)): multi-variable confound disclosure.
   - Gap 3 (§16 sub-principle): falsifiability gate for tentative mechanism names.
   - Gap 4 (§22 additions): per-sweep counting + authoritative-source rule **with the chronicle-layer-error carve-out**.
   - Gap 6 (§25 clarification): grouping-script attribution.
   - Gap 7 (§22 inline clarification, ~30 words): confirmatory family membership at commit-time.
   - Gap 8 (§17 sub-principle, distinct from Gap 2): tested-set vs. continuous-range qualifier smuggling.
   - A methodology → TODO back-ref line next to the umbrella and next to each modified §17 / §22 / §25 entry.
   Each addition follows the methodology.md voice (Case + Takeaway pattern or explicit sub-principle with matching style).
2. `.claude/skills/research-rigor/SKILL.md` has gate-text updates in the affected modes (`prereg` / `log-result` / `fwer-audit`) matching the "Skill target" field of each gap/sub-clause. **The codex-blocker meta-gap is explicitly NOT touched in this session** (deferred — see Deferred block).
3. `docs/_templates/experiment_section.md` has a falsifiability-block template subsection for use when a chronicle introduces a tentative mechanism name (gap 3).
4. Gate-against-case validation (Q-endorsed #1) has been run for every skill-gate sentence drafted in this session. No skill-gate change ships without a mental replay against the case that motivated it.
5. All changes bundled into **one commit** titled "methodology: add sub-principles from 2026-04-18 session (umbrella + gaps 2/3/4/6/7/8)" or similar, with the TODO file referenced in the commit message. (If partial-ship permission per sequencing is invoked, title the partial commit accordingly and open a follow-up TODO entry for the remaining gaps.)
6. After committing, mark this TODO's `Status:` line as `DONE · closed by commit <sha>` — or `PARTIAL · <completed items> closed by commit <sha>; <remaining items> deferred to <follow-up TODO>` if partial-ship — and leave the file in place for reasoning trail (do not delete — follows methodology §13 retention pattern for the methodology change itself).

**Scope boundary on the dedicated session.** This session is for methodology + skill + template updates only. Do not:

- Open new research questions (P-4 / P-5 / §v2.4-proxy-5d v2 / plasticity-1a engineering unblock — all out of scope).
- Re-chronicle past experiments to apply the new sub-principles retroactively (the existing chronicles remain at their prior state; the new sub-principles apply prospectively to future experiments and to any new same-day amendments).
- Re-run the FWER audit (F1 is size 4 at `fwer_audit_2026-04-18.md`'s post-5d-run addendum; no change needed).
- Touch the codex-blocker meta-gap (deferred per Q5; see Deferred block above).

---

## References

- `docs/methodology.md` — the 27-principle ledger being improved.
- `docs/_templates/experiment_section.md` — chronicle template (gap 3 template update).
- `.claude/skills/research-rigor/SKILL.md` — skill modes (multiple gate updates; codex-blocker deferred).
- `docs/chem-tape/experiments-v2.md` §v2.4-proxy-5a-followup-mid-bp — case study for umbrella sub-clause (a) and gap 3.
- `docs/chem-tape/experiments-v2.md` §v2.4-proxy-5d v1 — case study for gap 7 (non-rejecting confirmatory).
- `docs/chem-tape/experiments-v2.md` §v2.4-proxy-5c-tournament-size — case study for umbrella sub-clauses (b) and (c) (SWAMPED letter-vs-intent + bare-status grid-miss).
- `docs/chem-tape/findings.md` `proxy-basin-attractor` entry (post-`1165f88` state) — case study for gap 8 (tested-set vs. continuous-range smuggling).
- `Plans/prereg_v2-4-proxy-5b-crosstask.md` — case study for gap 2.
- `Plans/prereg_v2-4-proxy-5c-tournament-size.md` — case study for umbrella sub-clause (b).
- `Plans/prereg_v2-4-proxy-5d-followup-cloud-reexpansion.md` — case study for gap 7.
- `Plans/fwer_audit_2026-04-17.md` (superseded) + `fwer_audit_2026-04-18.md` — case studies for gap 4.
- `experiments/chem_tape/analyze_5ab.py` + `analyze_retention.py` — case studies for gap 6.
- Commit `1165f88` — final state of the 2026-04-18 session; commit message documents codex pass 2 P1/P2 findings that introduced original gaps 8 and 9 (now umbrella sub-clause (c)). A fresh session can read the commit message as a self-contained description of both.
