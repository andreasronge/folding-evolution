# Experiment section template — for docs/<track>/experiments.md

<!--
Copy the block below into experiments.md. Preserve the standardized
status line exactly — it is grep-parsed and indexed. See
docs/methodology.md and docs/_templates/README.md for the vocabulary.
-->

---

## §{id}. {short descriptive title}

**Status:** `{PASS | FAIL | INCONCLUSIVE | SUPERSEDED | FALSIFIED}` · n={N} · commit `{short-sha}` · {supersedes §X / superseded by §Y / —}

**Pre-reg:** [Plans/prereg_{slug}.md]({relative-path}) (if applicable)
**Sweep:** `experiments/<track>/sweeps/{name}.yaml`
**Compute:** {minutes · workers}

### Question

{One sentence lifted from the prereg. Do not restate the hypothesis — link to the prereg for that.}

### Hypothesis (pre-registered)

{One-sentence restatement. If this experiment was not pre-registered, say so explicitly — and read methodology §2 before writing the next one.}

### Result

<!--
Lead with a table. The table row-labeled outcomes must match one of
the pre-registered rows verbatim. If the observed pattern matches none
of the pre-registered rows, say so explicitly — that is the signal
that the outcome table was incomplete (methodology §2).
-->

| {arm/condition} | {solved/N} | {median-gens} | {holdout} | {other diagnostic} |
|-----------------|------------|---------------|-----------|--------------------|
| {baseline}      |            |               |           |                    |
| {intervention}  |            |               |           |                    |

**Matches pre-registered outcome:** `{PASS-clean / PASS-partial / INCONCLUSIVE / FAIL / none — see interpretation}`

**Statistical test:** {e.g., paired McNemar on seeds 0-19: p = 0.035; classification: confirmatory/exploratory; corrected α_FWER = 0.05/n_family}

### Pre-registration fidelity checklist (required, principle 23)

<!--
Silent partial execution fails the gate. Say explicitly on each line
whether the pre-registered element was done, deferred, or changed.
If any parameter/sampler/seed was changed mid-run, the new plan must
have been re-pre-registered in a separate commit BEFORE this chronicle
was drafted.
-->

- [ ] Every outcome row from the prereg was tested (none silently added, none silently removed). {note additions/removals here, or "all tested as pre-registered"}
- [ ] Every part of the plan (Part A baseline, Part B main, degenerate-success probes, diagnostics) ran to completion. {note deferrals with date + one-line reason, or "all parts ran"}
- [ ] No parameters, sampler settings, or seed blocks were changed mid-run. {if changed: link to the re-prereg commit `sha`}
- [ ] Every statistical test and diagnostic named in the prereg appears in the Result/Interpretation above, or is explicitly marked deferred below.

### Interpretation

{2-4 paragraphs. What the result says about the hypothesis. When the hypothesis was not quite right, describe WHAT the mechanism actually looks like rather than only what it isn't. Reference methodology principles where they apply.}

### Caveats

<!--
Principle 8 (n=10 is hypothesis-generation only).
Principle 17 (search your own text for "universal", "proven", "framework
confirmed", "the X axis" — scope-qualify any that remain).
-->

- **Seed count:** {n=10 preview / n=20 load-bearing / n=20+ paper-grade}
- **Budget limits:** {where compute cut the signal short}
- **Overreach check:** {explicitly list scope-qualifying caveats}
- **Open mechanism questions:** {what this experiment didn't answer}

### Degenerate-success check (if result is too clean)

<!--
Principle 4. Only fill in when the result is "too clean" (20/20, zero
drop, perfect signature). Delete this subsection otherwise.
-->

- **Mechanism inspection done:** {§X-inspection, or "deferred — inspection queued"}
- **Degeneracy ruled out:** {evidence}

### Falsifiability block (required if a tentative mechanism name is proposed, §16c)

<!--
Principle 16c. Only fill in when this chronicle proposes, narrows, or
broadens a tentative mechanism name (per the §16 / §16b renaming cycle).
Pre-commit at least three falsifiable predictions, each tied to a specific
experiment that would force a rename if violated. Pending experiments are
acceptable; unnamed experiments are not. Delete this subsection if no
mechanism name is being introduced or changed here.
-->

- **Tentative name proposed / narrowed / broadened:** {one-sentence name + which direction on the §16 / §16b cycle}
- **Prediction P-1:** {what the name predicts} — **violated if:** {observation that would force a rename} — **tested by:** {§X experiment, `Plans/prereg_X.md`, or pending sweep ID}
- **Prediction P-2:** {...} — **violated if:** {...} — **tested by:** {...}
- **Prediction P-3:** {...} — **violated if:** {...} — **tested by:** {...}

### Findings this supports / narrows

{Forward-links to docs/<track>/findings.md entries this experiment supports, narrows, or falsifies. Populate after the claim has been consolidated there.}

- Supports: {findings.md#finding-id}
- Narrows: {findings.md#finding-id} — reason: {...}
- Falsifies: {findings.md#finding-id} — reason: {...}

### Next steps

{Drawn from the prereg decision rule. If the observed outcome wasn't in the pre-registered table, the next step is explicitly "revise the outcome table" for future experiments on this axis (methodology §2).}

---

<!--
SUPERSESSION PATTERN (methodology §13):
When a later experiment narrows or falsifies this one, DO NOT edit the
result or interpretation. Instead, add this block at the top of the
section, below the status line:

> **Superseded by §Y ({date}).** {One-sentence summary of how Y narrowed
> or replaced the claim.} The analysis below is preserved for the
> reasoning trail; read Y for the current claim.

Then update the status line to SUPERSEDED or FALSIFIED.
-->
