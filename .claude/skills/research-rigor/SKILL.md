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
  "promote to findings", "scope check", "review my claim language", "narrow
  this", "supersede §X", or "retract §X".
---

# research-rigor

Project-local skill that enforces `docs/methodology.md` at the three checkpoints where overreach silently accumulates:

1. **Before running** — pre-registration (principles 1, 2, 4, 6)
2. **After running** — chronicle entry (principles 3, 10, 12, 13, 18)
3. **When consolidating** — findings-ledger promotion (principles 5, 16, 17, 18, 19)

Plus two maintenance modes:
- **Scope check** — scan draft text for overreach (principle 17)
- **Supersession rewrite** — explicit retraction, not silent deletion (principle 13)

## How to invoke

The skill triggers on intent, not a literal command. Match the user's phrasing to a mode below and follow that mode's steps.

| user intent | mode |
|-------------|------|
| "pre-register X", "new experiment on X", "design experiment for Y" | **prereg** |
| "record result of §X", "log the sweep", "write up X", "add §X to experiments.md" | **log-result** |
| "promote §X to findings", "consolidate this claim", "add to findings.md" | **promote-finding** |
| "scope check", "review this claim", "is this overreaching", "check my language" | **scope-check** |
| "supersede §X", "retract §X", "narrow §X based on §Y" | **supersession** |

If the user's intent is ambiguous between modes, ask which one — do not guess.

---

## Mode: prereg

**Goal:** produce `Plans/prereg_<slug>.md` that could not pass review without enforcing principles 1, 2, 4, 6, and 20.

**Steps:**

1. **Read `docs/methodology.md` sections 1, 2, 4, 6, and 20** to refresh the binding principles.
2. **Read `docs/_templates/prereg.md`** and copy it to `Plans/prereg_<short-slug>.md`. Slug should be kebab-case, ≤30 chars.
3. **Fill with the user** — section by section, in order. Do not skip ahead.
4. **Enforce the hard gates** (refuse to finish until satisfied):
   - **Outcome table has ≥3 rows** including at least one "partial" outcome (principle 2). If the user proposes only pass/fail, ask: "what would a *partial* result look like on this experiment, and what would it mean?" If they insist it's pass/fail, flag that the outcome table is incomplete and record that explicitly.
   - **Thresholds are baseline-relative** (principle 6). If an absolute number appears without a `F_baseline`-style referent, challenge it.
   - **Internal-control contrast is identified** (principle 1). If the user plans external-validity work without a tighter internal contrast, ask why the internal contrast isn't run first.
   - **Degenerate-success candidates are enumerated** (principle 4). What would a 20/20 / zero-drop / too-clean signature mean mechanistically? This must be written before running, not after.
   - **Sampler-design audit (principle 20).** If the prereg changes the **training input distribution** — sampler range, balanced-class fractions, stratification scheme, or the label function operating on the new sample — the prereg must include three measured numbers on a representative seed *before* the sweep runs:
     - (i) class balance under the new sampler (positives ÷ total)
     - (ii) accuracy of the primary suspected proxy predictor on training (e.g., "max > 5 → 0.75 train acc")
     - (iii) at least one verification that the label function is non-degenerate under the new sampler (positives exist; predicting constant-0 doesn't trivially win)

     If any of (i)–(iii) is missing, the prereg fails this gate. Sampler design is a dependent-variable carrier, not a neutral backdrop.
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
   - **Status is one of**: `PASS | FAIL | INCONCLUSIVE | SUPERSEDED | FALSIFIED` (no prose variants like "REJECTED" or "CONFIRMED"). If the result doesn't fit, the outcome table was incomplete — note that and use the closest token.
   - **Observed outcome matches a pre-registered row** verbatim, or the section explicitly says "did not match any pre-registered outcome" (principle 2 follow-up).
   - **n is stated explicitly.** n<20 must carry the "hypothesis-generating only" tag (principle 8).
   - **Commit hash present in status line** (principle 12).
   - **Too-clean OR threshold-adjacent results trigger attractor-category inspection** (principle 21). The bar is broader than just "too clean" — any sweep with **either** a too-clean signature (20/20, zero-drop) **or** a result clustered near a pre-registered threshold (e.g., 1/20, 3/20, 4/20 — anywhere a small attractor-category shift could change the verdict) must include a winner-genotype inspection that classifies each best-of-run into an attractor category. The section must include the resulting category breakdown (X/N seeds in attractor A, Y/N in attractor B, …) or a link to a queued inspection experiment.
   - **Mechanism rename check, both directions** (principle 16 + 16b). When writing the interpretation, ask explicitly: (a) is the claimed mechanism narrower than this name suggests? (b) is it broader than this specific predicate/condition? Renaming is bidirectional. The interpretation should justify the chosen name against both directions, not only against the obvious narrowing.
6. **Run the scope-check mode inline** on the interpretation text before writing it out.
7. **Populate forward-links** to `findings.md` entries this experiment supports or narrows (leave TODO if the finding hasn't been consolidated yet).

**Output:** the section appended to experiments.md + a summary of which pre-registered outcome row it matched.

---

## Mode: promote-finding

**Goal:** move a replicated, load-bearing claim from experiments.md into `docs/<track>/findings.md` using `findings_entry.md`. If the track has no findings.md yet, create it and link from the track's architecture.md.

**Steps:**

1. **Read `docs/methodology.md` sections 5, 16, 17, 18, 19** — these bound the consolidation.
2. **Verify preconditions before promoting:**
   - **Replicated or load-bearing:** at least one n≥20 experiment OR multiple independent experiments pointing at the same claim. A single n=10 preview is not eligible (principle 8).
   - **Mechanism inspection exists:** at least one zero-compute inspection (principle 3) or per-subgroup diagnostic (principle 10) has surfaced a mechanism-level reading, not just an aggregate solve count.
   - If either precondition fails, refuse to promote and name the missing experiment.
3. **Read `docs/_templates/findings_entry.md`.** Fill with the user.
4. **Enforce the hard gates:**
   - **Scope tag is in the claim header** (principle 18). One of: `within-family | across-family | universal-at-budget`, combined with an `n=…` tag and a regime tag.
   - **Scope boundaries section is non-empty** (principle 17). What does the claim NOT say? What is the open external-validity question?
   - **Mechanism name has a renaming history** or an explicit "name expected to narrow after §X" line (principle 16). First-pass names are correlates; budget for at least one cycle.
   - **Supporting experiments are linked with commit hashes** (principle 12).
5. **Run scope-check on the claim sentence.** The one-sentence claim is the thing that will propagate. It must survive the overreach-phrase sweep.
6. **Register the downstream-commitment line** — "downstream experiments may assume X; must still test Y" (principle 19). This is the review-loop cost being paid up front.

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

## Reference material loaded by this skill

These files are the skill's backing reference. Read the relevant ones when entering a mode — do not operate from memory, since methodology.md is actively revised.

- `docs/methodology.md` — the 19-principle ledger.
- `docs/_templates/README.md` — kit overview and status vocabulary.
- `docs/_templates/prereg.md` — pre-registration template.
- `docs/_templates/experiment_section.md` — chronicle entry template.
- `docs/_templates/findings_entry.md` — findings-ledger template.

## Voice

Be a reviewer, not a secretary. The skill exists because overreach and drift compound silently; its job is to surface the pressure points, not to smoothly fill in forms. If the user is resisting a gate, do not quietly lower it — name the principle and the case in methodology.md that justifies the gate, and let the user override explicitly. Overrides are fine. Silent lowering is not.
