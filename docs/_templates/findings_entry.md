# Findings entry template — for docs/<track>/findings.md

<!--
A findings entry is a DURABLE claim with explicit scope tags. Promote
here only from experiments with n ≥ 20 OR load-bearing claims that
downstream experiments will build on. See methodology §18 (scope tags)
and §19 (review loop is load-bearing).

Copy the block below. Every field is required unless marked optional.
-->

---

## {claim-slug}. {One-sentence claim — scope-tagged}

**Scope tag:** `{within-family | across-family | universal-at-budget}` · `{n=20 | n=20+}` · `{at <regime> | <task-family>}`

**Status:** `{ACTIVE | NARROWED | FALSIFIED}` · last revised commit `{short-sha}` · {YYYY-MM-DD}

### Claim

<!--
Lead with the single sentence. No hedging adjectives that cannot be
unpacked into specific experiments. "Chem-tape reaches X on Y under Z"
not "chem-tape works well on Y".
-->

{The claim. One sentence. Re-read after writing: does every adjective have a defined referent? Is the quantifier ("all", "most", "sometimes") backed by specific experiments below?}

### Scope boundaries (what this claim does NOT say)

<!--
Principle 16: the mechanism is usually narrower than the first-pass
name. Principle 17: search for "universal", "established", "the X
axis" and scope-qualify each. The scope boundaries are where future
experiments will re-contest the claim, so name them here.
-->

- Does not claim: {...}
- Does not generalize to: {...}
- Tested only on: {task family, alphabet range, budget}
- Open external-validity question: {...}

### Mechanism reading (current)

<!--
First-pass mechanism names are correlates. Budget for at least one
renaming cycle per claim (principle 16). If the name has already been
narrowed, record the narrowing chain here.
-->

**Current name:** `{mechanism-name}`

**Naming history (if narrowed):**
- Initial: `{name}` (experiment §X)
- Narrowed to: `{name}` (experiment §Y — reason)
- Current: `{name}` (experiment §Z — reason)

### Supporting experiments

| experiment | commit | n | what it establishes |
|------------|--------|---|---------------------|
| [§X]({path}#X) | `sha` | 20 | {primary positive result} |
| [§Y]({path}#Y) | `sha` | 20 | {replication / confirmation} |
| [§Z]({path}#Z) | `sha` | 20 | {mechanism inspection} |

### Narrowing / falsifying experiments (if any)

<!--
Principle 13: retract explicitly. When a later experiment narrows this
claim, add the experiment here and update the claim's scope boundaries
above. Do not silently edit the original claim.
-->

| experiment | commit | effect |
|------------|--------|--------|
| {§W} | `sha` | {"narrowed scope from X to Y" / "falsified within sub-family Z"} |

### Implications for downstream work

{What planned experiments should assume, and what they should NOT assume. The review-loop cost of this claim (principle 19) is that it becomes a commitment for downstream work — name that commitment here.}

- Downstream experiments may assume: {...}
- Downstream experiments must still test: {...}

### Review history

<!--
Principle 19: the review loop is load-bearing. Each major revision
should show a reviewer cycle — your own cross-model adversarial review,
a codex challenge, or a named collaborator's pushback.
-->

- {YYYY-MM-DD} — initial claim drafted from §X (commit `sha`).
- {YYYY-MM-DD} — reviewed by {mechanism}; narrowed scope to {current}.
