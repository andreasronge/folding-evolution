---
name: research-rigor
description: |
  Enforce the experimental methodology in docs/methodology.md at the three
  natural checkpoints of the folding-evolution research lifecycle:
  pre-registering a new experiment, recording a result, and promoting a
  claim to findings.md. Also handles scope-check sweeps on draft claim
  language and supersession rewrites when a later experiment narrows an
  earlier one.

  Use when the user says: "pre-register", "prereg", "design this experiment",
  "write up the result", "record this sweep", "log to experiments.md",
  "promote to findings", "promote this null", "record a negative finding",
  "scope check", "review my claim language", "narrow this", "supersede §X",
  "retract §X", "family-wise correction / FWER audit", or "diagnose §X" /
  "escalation check" / "what's next after FAIL" / "pivot / grid-miss
  follow-up".
---

# research-rigor

## Codex note

In Codex, this skill is used manually. Detect the user's intent, read this file, select the matching mode, and execute that mode's steps. Do not assume automatic skill dispatch.

Project-local skill that enforces `docs/methodology.md` at the three checkpoints where overreach silently accumulates:

1. **Before running** — pre-registration (principles 1, 2, 2b, 4, 6, 17a, 20, 22, 22a, 25, 28b)
2. **After running** — chronicle entry (principles 3, 10, 12, 13, 16c, 17b, 18, 23, 28a, 28c)
3. **When consolidating** — findings-ledger promotion (principles 5, 16, 16b, 16c, 17, 17b, 18, 19, 24 — null results promote on equal footing)

Plus two maintenance modes:
- **Scope check** — scan draft text for overreach (principle 17)
- **Supersession rewrite** — explicit retraction, not silent deletion (principle 13)

## How to invoke

The skill triggers on intent, not a literal command. Match the user's phrasing to a mode below and follow that mode's steps.

| user intent | mode |
|-------------|------|
| "pre-register X", "new experiment on X", "design experiment for Y" | **prereg** |
| "record result of §X", "log the sweep", "write up X", "add §X to experiments.md" | **log-result** |
| "promote §X to findings", "consolidate this claim", "add to findings.md", "record a null finding", "promote this FAIL" | **promote-finding** |
| "scope check", "review this claim", "is this overreaching", "check my language" | **scope-check** |
| "supersede §X", "retract §X", "narrow §X based on §Y" | **supersession** |
| "FWER audit", "family-wise correction", "how many tests are open" | **fwer-audit** |
| "what's next after §X FAIL", "should we try rank-2 / escalate", "diagnosis check", "pivot", "§X grid-miss, now what", "escalation check" | **diagnose** |

If the user's intent is ambiguous between modes, ask which one — do not guess.

---

## Mode: prereg

**Goal:** produce `Plans/prereg_<slug>.md` that could not pass review without enforcing principles 1, 2, 2b, 4, 6, 20, 22, and 25.

**Steps:**

1. **Read `docs/methodology.md` sections 1, 2, 2b, 4, 6, 20, 22, and 25** to refresh the binding principles.
2. **Read `docs/_templates/prereg.md`** and copy it to `Plans/prereg_<short-slug>.md`. Slug should be kebab-case, ≤30 chars.
3. **Fill with the user** — section by section, in order. Do not skip ahead.
4. **Enforce the hard gates** (refuse to finish until satisfied):
   - **Outcome table has ≥3 rows** including at least one "partial" outcome (principle 2). If the user proposes only pass/fail, ask: "what would a *partial* result look like on this experiment, and what would it mean?" If they insist it's pass/fail, flag that the outcome table is incomplete and record that explicitly.
   - **Outcome table is a grid when ≥2 axes are measured (principle 2b).** List the independent quantities the prereg will measure (e.g., F = solve rate, R = population retention; or solve rate × attractor-category mix; or fitness × diversity). If there are two or more, the outcome table must be the **cross-product** of each axis's coarse bins — not paired rows that move together. Ask: "what is the outcome if axis A is high and axis B is low?" If the user's table does not have a row for that cell, the table is incomplete. Cells that are genuinely excluded by physics still need an explicit `IMPOSSIBLE` or `INCONCLUSIVE` token — they must not be left blank, because blank cells are where surprising results land. Paired rows (A_high+B_high = PASS, A_low = FAIL) silently smuggle a correlation prior into the outcome space; decompose them.
   - **Thresholds are baseline-relative** (principle 6). If an absolute number appears without a `F_baseline`-style referent, challenge it.
   - **Internal-control contrast is identified** (principle 1). If the user plans external-validity work without a tighter internal contrast, ask why the internal contrast isn't run first.
   - **Degenerate-success candidates are enumerated** (principle 4). What would a 20/20 / zero-drop / too-clean signature mean mechanistically? This must be written before running, not after.
   - **Sampler-design audit (principle 20).** If the prereg changes the **training input distribution** — sampler range, balanced-class fractions, stratification scheme, or the label function operating on the new sample — the prereg must include three measured numbers on a representative seed *before* the sweep runs:
     - (i) class balance under the new sampler (positives ÷ total)
     - (ii) accuracy of the primary suspected proxy predictor on training (e.g., "max > 5 → 0.75 train acc")
     - (iii) at least one verification that the label function is non-degenerate under the new sampler (positives exist; predicting constant-0 doesn't trivially win)

     If any of (i)–(iii) is missing, the prereg fails this gate. Sampler design is a dependent-variable carrier, not a neutral backdrop.
   - **Family-wise test classification (principle 22).** If the prereg includes a statistical test, classify it explicitly as either **confirmatory** (enters the FWER family — its p-value gates a claim and must be compared against a Bonferroni-corrected α) or **exploratory** (effect-size only, no p-value gate, used for hypothesis generation). Confirmatory tests must name the family they belong to (e.g., "proxy-basin family", "constant-slot-indirection family") and the current corrected α = 0.05 / n_family. Run the **fwer-audit** mode if the family size isn't obvious. A prereg with a test but no classification fails this gate.
   - **Measurement-infrastructure gate (principle 25).** For every metric the prereg commits to — solve rate, retention, fitness curves, attractor category shares, diversity indices, whatever — the prereg must record one of three states: *(i)* **produced directly** (name the file / column / routine that emits it — e.g., "`history.npz:final_pop_edit_dist_2` via `sweep.py:dump_final_population=True`"); *(ii)* **produced as an explicitly-labeled bound or proxy** (name the proxy, the direction of the bound, and why the bound is informative for the claim — e.g., "R_exact is an upper bound on R_edit_2; low values are conclusive, high values are not"); *(iii)* **pending an infra extension** (name the extension, rough effort estimate, and commit to either completing it before the sweep or re-scoping the metric to what current code emits). A metric named without one of these three labels — i.e., the producing code may or may not exist — fails this gate. The test is a 5-minute grep at prereg time; skipping it produces expensive chronicle-time rework.
   - **Multi-variable confound disclosure (principle 17a).** When the prereg varies a nominal config field across cells (e.g., `mr`, `gens`, `tournament_size`, `seed_fraction`, `mr × gens`), enumerate every derived *process* variable that changes across those cells — per-tape expected mutation count, selection opportunities per lineage, crossover opportunities, fixation time, etc. If more than one derived variable shifts, the outcome discrimination is narrower than the nominal variable names suggest: the outcome rows must name the process-variable-bundle being discriminated, not the nominal field. "Rate vs. budget" silently smuggles a two-variable assumption into what is actually a multi-variable contrast. Case: §v2.4-proxy-5b-crosstask's `mr × gens` change shifted four derived variables, not two.
   - **Conjunction-guard check for multi-mode regimes (principle 28b).** For each degenerate-success guard enumerated above (principle 4), check whether the detection criterion is a single gate (one condition) or a conjunction (two or more AND-ed conditions). If single, list the guarded regime's known failure modes and verify the single gate detects each one — especially modes on a different axis from the criterion (e.g., an `F < 18/20` guard cannot detect a propagation-failure mode where F=20/20 but R_fit low). If any named failure mode is not covered by the criterion, add criteria. Single-criterion guards over multi-failure-mode regimes fail this gate. Case: §v2.4-proxy-5c-tournament-size's SWAMPED guard letter-passed at ts=2 despite missing the propagation-failure mode.
   - **Per-sweep test counting (principle 22a).** When the prereg produces multiple independent statistical tests (e.g., one paired McNemar per sweep across different arms, decoders, tasks, or seed blocks), each test is a separate family member under principle 22. The prereg must state its per-sweep test count explicitly in the confirmatory/exploratory classification block. Multi-sweep preregs that omit this count state their classification as **ambiguous** until amended — and the FWER family size cannot be correctly computed at audit time. Case: §v2.4-proxy-4c-replication's 2-sweep prereg was miscounted (as 0 and as 1 test) by two different audits before the rule was codified.
   - **Grouping-script attribution (principle 25 clarification).** For each metric committed to above under principle 25, verify both (a) the metric-computing code path *and* (b) the grouping code path that produces the per-cell table. If the metric module's default aggregator groups by axes narrower than the prereg's grid — e.g., `summarize_arm` in `analyze_retention.py` groups by `(arm, safe_pop_mode, seed_fraction)` — the prereg must name the grouping wrapper / script / function covering its axis set (e.g., `analyze_5ab.py <axis> --include-holdout`). "Produced directly by `analyze_retention.py`" fails this gate when the grid axes require a wrapper the module doesn't include by default.
5. **Capture the decision rule.** Under each outcome row, what experiment runs next? This is the commitment that prevents post-hoc rerouting (principle 19).
6. **Commit the prereg.** `git add Plans/prereg_<slug>.md` and ask the user whether to commit now or after the sweep finishes. A prereg committed after the sweep is no longer a prereg.

**Output:** path to the prereg file + a one-paragraph summary confirming the five gates were met.

---

## Mode: log-result

**Goal:** append a section to `docs/<track>/experiments.md` using `experiment_section.md`, with the status line exactly standardized.

**Steps:**

1. **Identify the track.** Ask or infer from recently-edited sweeps: chem-tape, folding, ca, or a new track.
2. **Capture the commit hash:** `git rev-parse --short HEAD`. If the working tree is dirty at the time of the sweep, warn the user — commit-hash discipline (principle 12) requires a clean commit for the result to anchor.
3. **Look up the pre-registration.** `ls Plans/prereg_*.md | grep <slug>`. If no prereg exists, ask the user to either:
   - write one now (ideal if the run was yesterday and they still remember the decision rule), or
   - explicitly mark the section as "not pre-registered" in the chronicle so principle 2 is visible to future readers.
4. **Read `docs/_templates/experiment_section.md`**. Fill fields in order with the user.
5. **Enforce the hard gates:**
   - **Pre-registration execution fidelity (principle 23).** Before writing interpretation, verify explicitly: *(i)* every outcome row in the prereg was tested (none silently added, none silently removed), *(ii)* every part of the plan (Part A baseline, Part B main, degenerate-success checks, etc.) was completed or explicitly deferred with a dated one-line reason in the chronicle, *(iii)* if any parameter, sampler, or seed block was changed mid-run, the new plan was re-pre-registered in a separate commit *before* this chronicle was drafted. Silent partial execution fails the gate. The fidelity checklist must appear as its own block in the chronicle; the user cannot skip it because "it all ran as planned" — if it did, say so explicitly on each of (i)–(iii).
   - **Metric fidelity (principle 25, chronicle-time mirror).** For each metric the prereg named, verify that the number reported in the chronicle is *the metric the prereg asked for*, not a relabeled proxy. The three valid states are the same as at prereg-time: (i) the metric was produced directly as committed; (ii) the metric was produced as a labeled bound/proxy and the chronicle says so *explicitly in the reported-number's caption* (not just a footnote — e.g., "R_exact ≤ 0.036 (upper bound on R_edit_2; the prereg's actual R_edit_2 metric is unmeasured)"); (iii) the prereg's metric was not produced and a proxy was substituted — this requires an explicit "prereg's metric X is DEFERRED / UNMEASURED; the chronicle reports proxy Y instead" sentence. Silent reinterpretation of a bound as satisfying a prereg that asked for the quantity itself fails the gate. When this gate catches a mismatch, it also flags principle 23-(i) — the prereg's outcome row corresponding to the unmeasured metric has not actually been tested, so the status token must reflect that ambiguity (typically `INCONCLUSIVE`, not `PASS`).
   - **Status is one of**: `PASS | FAIL | INCONCLUSIVE | SUPERSEDED | FALSIFIED` (no prose variants like "REJECTED" or "CONFIRMED"). If the result doesn't fit, the outcome table was incomplete — note that and use the closest token.
   - **Observed outcome matches a pre-registered row** verbatim, or the section explicitly says "did not match any pre-registered outcome" (principle 2 follow-up).
   - **n is stated explicitly.** n<20 must carry the "hypothesis-generating only" tag (principle 8).
   - **Commit hash present in status line** (principle 12).
   - **Too-clean OR threshold-adjacent results trigger attractor-category inspection** (principle 21). The bar is broader than just "too clean" — any sweep with **either** a too-clean signature (20/20, zero-drop) **or** a result clustered near a pre-registered threshold (e.g., 1/20, 3/20, 4/20 — anywhere a small attractor-category shift could change the verdict) must include a winner-genotype inspection that classifies each best-of-run into an attractor category. The section must include the resulting category breakdown (X/N seeds in attractor A, Y/N in attractor B, …) or a link to a queued inspection experiment.
   - **Mechanism rename check, both directions** (principle 16 + 16b). When writing the interpretation, ask explicitly: (a) is the claimed mechanism narrower than this name suggests? (b) is it broader than this specific predicate/condition? Renaming is bidirectional. The interpretation should justify the chosen name against both directions, not only against the obvious narrowing.
   - **Prereg-promise ledger.** Read the linked prereg end-to-end and extract every concrete deliverable it required. For each, the chronicle must either report it verbatim or explicitly mark it deferred with a one-line reason. Enumerate at least:
     - **Baseline measurements** named in the prereg's "Baseline measurement" section. If the prereg defines per-pair/per-condition thresholds via `Fmin` or `F_baseline`, the chronicle must print those raw counts and the computed `Fmin` — not only the alternation/headline numbers. Without them the scoring rule cannot be evaluated, and the scales-vs-swamp row cannot be picked.
     - **Statistical tests** named in the prereg (e.g., "paired McNemar per pair"). Must appear in the chronicle with raw disagreement counts, or be marked deferred.
     - **Degenerate-success candidates**, *each one individually*. The prereg enumerates these per-pair / per-condition (e.g., "Pair 2: check `any cell > 9` range-limit trick"; "Pair 3: pre-accept swamp if `Fmin ≥ 19/20`"). A single generic sentence ("near-canonical bodies across seeds") does **not** discharge a pair-specific guard. Each candidate needs its own discharge sentence naming what was checked and what was found. Winner-genotype inspections must print the actual decoded body family or a per-seed category table, not narrate it.
     - **Diagnostics-to-log** named in the prereg (class balance, flip-transition cost, holdout gap, etc.). Missing diagnostics must be marked deferred.

     If any item is silently omitted — present in the prereg, absent from the chronicle, not marked deferred — the gate fails.
   - **Row-match clause fidelity (principle 28a).** Before writing "Matches pre-registered outcome: X", enumerate each clause in row X — prose AND numeric — and verify the observed data satisfies all of them. Prose-only matches fail the gate: they are §2b grid-misses, not row matches. When a row's prose anticipates a shape but its numeric clause is tighter than the observed signature, explicitly note the grid-miss ("matched on letter of prose, failed on numeric clause <0.05") and do not narrate the result as a match. Case: §v2.4-proxy-5a-followup-mid-bp's PLATEAU-MID prose-match / clause-fail drift.
   - **Tested-set qualifier discipline (principle 17b).** Before writing a mechanism-name qualifier for a tested variable (e.g., "at tournament_size ≥ 3", "at budget ≥ N", "at topk ≥ K"), enumerate the tested values for that variable across the supporting experiments. If the qualifier uses `≥`, `>`, `<`, or `≤` against a tested endpoint, rewrite as `∈ {tested values}` unless a new experiment explicitly tested the range claim. Flag any exploratory-classified evidence that appears in the qualifier — exploratory evidence cannot raise the qualifier's scope above "at tested values". Case: `findings.md#proxy-basin-attractor`'s initial "≥ tournament_size=3" half-line extrapolated from discrete tested ts ∈ {3, 5, 8}; rewritten at commit `1165f88`.
   - **Status-line qualifier fidelity (principle 28c).** After drafting the Result + Interpretation sections, re-read them for any "matched on letter," "grid-miss," "guard-letter-vs-intent," or similar qualifier on the headline verdict. If present, the status line must repeat that qualifier inline (in parentheses, on the same line). Bare status tokens with body qualifications fail this gate — the status vocabulary is grep-parsed and a scan-only reader who never drills into the body must still see the qualifier. Case: §v2.4-proxy-5c-tournament-size's initial bare `PASS`, fixed at `1165f88` to carry the grid-miss qualifier inline.
   - **Falsifiability block for tentative mechanism names (principle 16c).** When the chronicle proposes, narrows, or broadens a tentative mechanism name (per the §16 / §16b renaming cycle), the Falsifiability block in the chronicle template (`docs/_templates/experiment_section.md`) is mandatory, not optional. At least **three** falsifiable predictions must be pre-committed, each tied to a specific experiment — pending or completed — that would force a rename if violated. Unnamed experiments fail the gate. Names without falsifiers are just-so stories; they survive any further data by qualifier-attachment and consume the §16 renaming budget without progress. Case: §v2.4-proxy-5a-followup-mid-bp's "non-monotone single-mechanism cloud-destabilisation" was post-hoc rescued with P-1..P-5 after codex flagged the name as too residual.
6. **Run the scope-check mode inline** on: (a) the interpretation text, (b) the "Findings this supports / narrows" bullets, **and (c) any combined-verdict / reframed-headline / cross-experiment section this chronicle adds to or modifies elsewhere in the track.** Summary paragraphs that consolidate across experiments are where overreach phrases slip past a careful local section — "N task families total," "X as the edge" — so scope-check must cover them too, not just the new section's body.
7. **Codex adversarial review (required before final write).** Draft the section to a scratch buffer, then invoke `/codex` in consult mode with a prompt that: (a) references the prereg path, the methodology path, and the draft section, (b) asks specifically for pre-registration fidelity, degenerate-success guard discharge (per-pair/per-condition), scope-tag discipline in any combined-verdict text, and missing statistical tests. Read the codex output and address every P1 finding before writing to disk. Address P2 findings or add an explicit "acknowledged, deferred because X" line per P2 — silent dismissal fails this gate. If the only response to codex is to rewrite the local interpretation, also check whether the combined-verdict / headline paragraphs upstream need the same narrowing.
8. **Populate forward-links** to `findings.md` entries this experiment supports or narrows (leave TODO if the finding hasn't been consolidated yet).

**Output:** the section appended to experiments.md + a summary of which pre-registered outcome row it matched.

---

## Mode: promote-finding

**Goal:** move a replicated, load-bearing claim — positive *or* null — from experiments.md into `docs/<track>/findings.md` using `findings_entry.md`. If the track has no findings.md yet, create it and link from the track's architecture.md.

**Null results promote on equal footing (principle 24).** A major FAIL or INCONCLUSIVE outcome that changes what downstream experiments should assume is itself a finding. Promote it with the same template, status token `FALSIFIED` or `NULL`, and the scope tag documenting *where the claim does not hold*. Do not hide nulls in the chronicle layer — findings.md is the claim layer and both positive and negative claims belong there.

**Steps:**

1. **Read `docs/methodology.md` sections 5, 16, 17, 18, 19, 24** — these bound the consolidation.
2. **Verify preconditions before promoting:**
   - **Replicated or load-bearing:** at least one n≥20 experiment OR multiple independent experiments pointing at the same claim (positive or null). A single n=10 preview is not eligible (principle 8). For null findings, the same bar applies — a single n=20 FAIL is enough if it is load-bearing (downstream experiments were going to assume the inverse).
   - **Mechanism inspection exists:** at least one zero-compute inspection (principle 3) or per-subgroup diagnostic (principle 10) has surfaced a mechanism-level reading, not just an aggregate solve count. For a null finding, the inspection must rule out the mundane failure modes (budget ceiling, sampler degeneracy, decoder-arm confound) so the null is genuinely about the claim, not about the setup.
   - If either precondition fails, refuse to promote and name the missing experiment.
3. **Read `docs/_templates/findings_entry.md`.** Fill with the user.
4. **Enforce the hard gates:**
   - **Status token matches claim polarity.** `ACTIVE` or `NARROWED` for a positive claim; `FALSIFIED` or `NULL` for a null claim. A null entry's one-sentence claim reads "Intervention X does NOT Y under regime Z" — not a softened positive.
   - **Scope tag is in the claim header** (principle 18). One of: `within-family | across-family | universal-at-budget`, combined with an `n=…` tag and a regime tag. For null claims the scope tag documents *where the null holds* — which is the honest mirror of where a positive would hold.
   - **Scope boundaries section is non-empty** (principle 17). What does the claim NOT say? What is the open external-validity question? For nulls: what setup changes might flip the null (e.g., "does not hold under BP_TOPK at 4× compute — open whether 16× compute changes this").
   - **Mechanism name has a renaming history** or an explicit "name expected to narrow after §X" line (principle 16). First-pass names are correlates; budget for at least one cycle.
   - **Supporting experiments are linked with commit hashes** (principle 12).
5. **Run scope-check on the claim sentence.** The one-sentence claim is the thing that will propagate. It must survive the overreach-phrase sweep.
6. **Codex adversarial review (required before final write).** Draft the findings entry to a scratch buffer, then invoke `/codex` in consult mode with a prompt that: (a) references the supporting experiments, the methodology path, and the draft entry, (b) asks specifically for whether the scope tag matches the actual tested subset, whether the one-sentence claim would survive a reviewer challenging the naming (principle 16 both directions), whether the downstream-commitment line is honest about what has *not* been tested, and whether the mechanism reading is consistent with all linked experiments (not just the cleanest one). Address every P1 finding before writing to disk; acknowledge P2 findings in-entry or explicitly defer them. Promotion to findings is the highest-stakes write in this track — the codex gate is non-negotiable here.
7. **Register the downstream-commitment line** — "downstream experiments may assume X; must still test Y" (principle 19). This is the review-loop cost being paid up front.

**Output:** the findings.md entry + a list of downstream commitments the user is implicitly making.

---

## Mode: scope-check

**Goal:** sweep a draft claim for overreach phrases and force scope-qualification (principle 17).

**Steps:**

1. **Read the target** — a paragraph, a section, or a whole file.
2. **Grep for the flagged phrases:**
   ```
   universal | universally | established | proven | confirmed framework
   the X axis | THE mechanism | always | never | guarantees
   cross-regime | cross-task | across tasks
   ```
   Plus any phrase that makes a quantifier claim (`all`, `every`, `no X`) without naming the tested subset.
3. **For each hit, ask the user:**
   - What is the tested scope? (family, n, regime)
   - Is the phrase scope-qualified in the surrounding text?
   - If not, propose a scope-tagged rewrite.
4. **Never silently rewrite.** Show the user each flagged phrase and the proposed rewrite; let them accept, reject, or edit.

**Output:** diff of accepted changes, a list of phrases the user chose to keep unqualified (for visibility), and — if any claim-level overreach was found — a suggestion to update the corresponding findings.md entry's scope tag.

---

## Mode: supersession

**Goal:** explicit retraction when a later experiment narrows or falsifies an earlier claim (principle 13). Never silently edit or delete.

**Steps:**

1. **Identify the target section** in experiments.md and, if consolidated, the target entry in findings.md.
2. **Do NOT edit the original result, table, or interpretation.** Those are the reasoning trail.
3. **Add a supersession block** at the top of the target section, below the status line:

   ```
   > **Superseded by §Y (YYYY-MM-DD).** {one-sentence summary of how Y narrowed
   > or replaced the claim.} The analysis below is preserved for the reasoning
   > trail; read §Y for the current claim.
   ```

4. **Update the status line token** to `SUPERSEDED` or `FALSIFIED` and add `superseded by §Y` to the right-hand metadata.
5. **For the findings.md entry:**
   - If narrowed: update the scope tag, add a row to "Narrowing / falsifying experiments", add a naming-history entry to "Mechanism reading".
   - If falsified: change status token to `FALSIFIED`, move the claim text into the naming-history section, and replace the top-line claim with the narrower (or null) claim the data actually supports.
6. **Run scope-check on the revised claim** before committing.

**Output:** the edited sections + a summary noting that no original content was deleted.

---

## Mode: fwer-audit

**Goal:** enforce principle 22 (family-wise error rate) across the active sweep portfolio. Answers the question "how many confirmatory tests are open, and what is the corrected α today?"

**Steps:**

1. **Scan `Plans/prereg_*.md`** for prereg files whose status line is `QUEUED` or `RUNNING`, plus any chronicled experiments in `docs/<track>/experiments*.md` in the last 30 days whose status is not yet `PASS`/`FAIL`/`SUPERSEDED`/`FALSIFIED` with all downstream commitments discharged.
2. **Group by test family.** A family is the set of tests whose p-values would jointly feed a single findings.md claim (e.g., "constant-slot-indirection family" = §v2.3 main + §v2.6 baseline + §v2.11 decoder-arm). Ask the user to confirm family assignments; do not guess silently.
3. **Classify each test and count per-sweep.** Mark each as confirmatory (family member, gates a claim) or exploratory (effect size only, no claim gate). If the prereg did not make this classification, flag the prereg as out-of-compliance with principle 22 and require a retroactive classification commit. Apply the three counting rules:
   - **Per-sweep counting (principle 22a).** When a prereg drives multiple independent sweeps (e.g., Arm A preserve + BP_TOPK consume in §v2.4-proxy-4c), each sweep's test is a separate family member — not one collective test under the prereg's umbrella. Enumerate tests per sweep, not per prereg. Multi-sweep preregs that omit an explicit per-sweep count state their classification as **ambiguous** and block the audit until amended.
   - **Commit-time family membership.** A confirmatory test that ran counts in the family regardless of rejection outcome. A FAIL-TO-REPLICATE test consumed α budget and remains in the family; its null finding is recorded under §24 but does not reduce the family size. The corrected α tightens whenever a new confirmatory test is registered, not only when one rejects.
   - **Chronicle-vs-audit authority (principle 22b).** When the audit's per-family count disagrees with the source chronicle's own FWER bookkeeping, default to the chronicle *provided* its bookkeeping appeals to standard Bonferroni conventions and is internally consistent. When the audit identifies a specific chronicle-layer error — overcount, misclassification of exploratory-as-confirmatory, non-standard counting convention — surface the contestation for explicit resolution; do not defer automatically. Resolution requires either (i) a chronicle amendment (§13 supersession if load-bearing) or (ii) an explicit audit-layer override documented with the contested count's grounding. Silent audit-deferral and silent chronicle-override both fail this gate.
4. **Compute Bonferroni-corrected α per family:** α_corrected = 0.05 / n_confirmatory_in_family. Report the family, its current member list, the corrected α, and which members have p-values already reported.
5. **Flag at-risk claims** — any finding that currently rests on a p-value that would no longer clear the corrected α. These must either gain a new confirmatory experiment, be re-scoped as effect-size-only, or have the finding narrowed.
6. **Emit a short digest** (≤1 screen) the user can paste into the morning briefing or a methodology audit note. Do not write to disk unless explicitly asked.

**Output:** family breakdown with corrected α per family, at-risk claim list, and a suggested next action per family.

---

## Mode: diagnose

**Goal:** classify an ambiguous experiment outcome (FAIL / `INCONCLUSIVE — grid-miss` / surprising partial) into one of four diagnosis classes *before* any escalation prereg is drafted. Produces a dated diagnosis doc that any subsequent escalation prereg must reference.

**Invokes principle 29** (diagnose-before-escalate). Extends principle 2b's pre-commitment discipline from outcome-grid rows to failure-class tags.

**When to invoke:** user says "what's next after §X FAIL", "should we try rank-2 / escalate", "diagnosis check", "pivot", "§X grid-miss, now what", or "escalation check."

**Do NOT invoke for:** clean PASS (use `promote-finding`), clean FAIL that fits a pre-registered row with escalation already specified in the prereg's decision rule (the decision rule is authoritative), or pre-registered null results (use `promote-finding` → null branch per §24).

**Steps:**

1. **Read `docs/methodology.md` §25, §2b, §29** to refresh the binding principles, and `docs/theory.md` "References to Obtain" plus the Baldwin / EPANN / QD subsections to confirm the literature-term mapping.
2. **Identify the experiment and its pre-registered outcome rows.** Read `Plans/prereg_<§X>.md`. Confirm the observed result does not fit any PASS or explicitly-enumerated FAIL row.
3. **Step 1 — infrastructure gate (measurement-artifact check).** Run through principle 25 sanity checks for this experiment family:
   - Does `F_AND_train` (or the equivalent seeded-cell saturation metric) hit ceiling on seeded cells?
   - Does the frozen-control anchor reproduce the §X-prior baseline within the documented CI?
   - Do the METRIC_DEFINITIONS cited in the prereg match the code verbatim?
   - If any check fails → **diagnosis = `measurement-artifact`**. Output: fix infrastructure; do NOT redesign the experiment. STOP the mode; no escalation prereg yet.
4. **Step 2 — mechanism-capacity check.**
   - Is the mechanism's capacity being exercised? (e.g., latent state spread widens with adaptation budget; tail cells show measurable latent activity; per-individual mechanism state differs across genotypically-diverse individuals.)
   - If NO → **diagnosis = `mechanism-weak`** (literature: capacity-insufficient plasticity, Soltoggio-Stanley-Risi 2018 review, §theory.md References-to-Obtain). Output: escalate capacity per the mechanism ladder (rank-2 memory, deeper mechanism). Cite the ladder position from `docs/chem-tape/runtime-plasticity-direction.md`.
5. **Step 3 — selection-need check.**
   - Does selection *need* the mechanism to satisfy its fitness criterion? (e.g., `F_AND_train` already at ceiling on seeded cells ⇒ selection already satisfied by static shortcut; proxy-predicate attractor dominates ⇒ task-level shortcut rewards static solutions.)
   - If NO → **diagnosis = `selection-deception`** (literature: "deception of learning-to-learn," Risi & Stanley 2010; "objective deception," Lehman & Stanley 2011). Output: change the selection regime, not the mechanism. Escalation ladder:
     1. Strip the static shortcut (drop canonical seed, add regime shift) — cheapest, minimal engineering.
     2. Evolvability ES — BC-free, next-cheapest; measures offspring variance directly.
     3. Novelty search or MAP-Elites with a **pre-registered BC** (see Pugh-Soros-Stanley 2016 for BC design discipline; Mouret-Clune 2015 for MAP-Elites mechanism). BC must live in code with METRIC_DEFINITIONS entry before any sweep runs.
6. **Step 4 — grid-match (if none of 1-3 fired cleanly).**
   - If the pattern doesn't fit any of the above classes → **diagnosis = `grid-miss`** (methodology-local, §2b). The observed pattern is a novel row the prereg did not enumerate. Draft the candidate new row, date it pre-data, and commit it as a provisional scratch doc alongside the diagnosis doc (principle 2b pre-commitment). Do NOT proceed to escalation until the new row is committed and the subsequent data is collected against the expanded grid.
7. **Theory.md currency check.** If the diagnosis invokes a literature concept **not currently cited** in `docs/theory.md` (check both main Related Work sections and "References to Obtain"), add an entry before closing the diagnosis. Anticipatory summary style is fine for not-yet-read PDFs — match the register of existing References-to-Obtain entries, include a confidence tag if the exact citation details are uncertain. This keeps theoretical grounding in lockstep with empirical findings.
8. **Produce the diagnosis doc.** Write `Plans/diagnosis_<§X>_<YYYY-MM-DD>.md` containing:
   - Experiment reference (prereg link, result CSV/JSON link, relevant chronicle entries)
   - Observed pattern (metrics, magnitudes, and the specific signatures that triggered the mode)
   - Diagnosis tag: `<project-term>` / `<literature-term>` (from §29 table; exact terminology)
   - Rejected diagnoses and why (negative reasoning is load-bearing — it records what was considered and ruled out)
   - Escalation path (specific next experiment family, mechanism or selection-regime change, required pre-registrations)
   - Literature references cited; `docs/theory.md` edits made (if any)
9. **Hand off to prereg mode.** The next escalation prereg must be opened via `prereg` mode with the diagnosis doc path provided as input. The escalation prereg's Setup section must contain:
   > *This prereg follows from diagnosis `Plans/diagnosis_<§X>_<YYYY-MM-DD>.md` (class: `<project-term>` / `<literature-term>`). Escalation path is pre-committed; scope is restricted to the path identified there.*
   
   The `prereg` mode should refuse to finish without this clause when the diagnosis doc exists in the preceding commit history.

**Terminology discipline.** Use the project-term / literature-term pair from methodology §29 verbatim. Do not invent ad-hoc synonyms. If a diagnosis legitimately doesn't fit any of the four classes cleanly, that is itself a finding — write it up as `diagnosis = grid-miss (meta)` and request a methodology revision (new class + new literature-term mapping) rather than forcing a classification.

**Literature exploration.** If the mode fires and the diagnosis depends on a literature area thinly covered in `docs/theory.md` (example: if `selection-deception` fires and the project has no MAP-Elites / QD entries yet), propose 1-3 papers to read in the diagnosis doc under a "Literature to obtain" heading. Mark with confidence tags matching theory.md's convention. Do not block the diagnosis on reading them — they are follow-up work, tracked in the diagnosis doc so they don't get lost.

**Output:** the diagnosis doc path, the tag string (for paste into the scratch doc / chronicle), and the escalation-prereg hook for the `prereg` mode.

---

## Reference material loaded by this skill

These files are the skill's backing reference. Read the relevant ones when entering a mode — do not operate from memory, since methodology.md is actively revised.

- `docs/methodology.md` — the 29-principle ledger (plus sub-principles 2b, 16b, 16c, 17a, 17b, 22a, 22b, 28a, 28b, 28c).
- `docs/_templates/README.md` — kit overview and status vocabulary.
- `docs/_templates/prereg.md` — pre-registration template.
- `docs/_templates/experiment_section.md` — chronicle entry template.
- `docs/_templates/findings_entry.md` — findings-ledger template.

## Voice

Be a reviewer, not a secretary. The skill exists because overreach and drift compound silently; its job is to surface the pressure points, not to smoothly fill in forms. If the user is resisting a gate, do not quietly lower it — name the principle and the case in methodology.md that justifies the gate, and let the user override explicitly. Overrides are fine. Silent lowering is not.
