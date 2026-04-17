# Arc: {arc-name}

<!--
Save as: docs/<track>/arcs/<arc-slug>.md

An arc doc is the layer between chronicle (one experiment) and
findings.md (one consolidated claim). It carries the *reasoning
trail across a chain of related experiments* so a reader coming
back in three months can reconstruct the state of inquiry without
re-reading every chronicle entry.

Scope: one arc = one central mechanism question being iteratively
narrowed. Stop creating a new arc when the question is either
promoted to findings.md (consolidated) or abandoned.

Update cadence: refresh on every new chronicle entry that touches
the arc. Arc docs are intentionally LIVE — unlike chronicle entries
(frozen at commit) or findings.md (revised with supersession
markers), arc docs are rewritten in place. The reasoning trail lives
in the "Chronology" section via commit-hash pointers back to
chronicles and findings.md entries, not via preserved prose.

Each arc doc is ≤ 1-2 screens. If it grows past that, the arc is
either (a) ready to consolidate into findings.md, or (b) actually
two separate arcs that should be split.

Delete this comment block when filling in.
-->

**Central question (one sentence):** {what this arc is iteratively answering}

**Current state (one sentence):** {what we believe today, scope-qualified, with link to latest chronicle}

**Live next question:** {the single most load-bearing open sub-question right now}

**Related findings.md entry:** [findings.md#{id}](../findings.md#{id}) (ACTIVE / NARROWED / FALSIFIED / not yet consolidated)

## Chronology

<!--
One row per chronicle entry that moved the arc. Chronologically
ordered. Narrowing entries and broadening entries both belong here.
Keep rows terse — the chronicle is the source of truth for detail.
-->

| date | §id | commit | what it added / changed |
|---|---|---|---|
| {YYYY-MM-DD} | [§X](../experiments-v2.md#{anchor}) | `{sha}` | {one-line summary} |

## Open questions (priority-ordered)

<!--
Questions this arc has surfaced but not yet answered. Each one
should name the experiment that would resolve it (prereg slug or
"not-yet-scoped") and whether it is zero-compute or requires fresh
compute. The top row is the "live next question" duplicated for
visibility.
-->

| # | question | resolver (prereg / follow-up) | compute |
|---|---|---|---|
| 1 | {most-load-bearing open question} | {slug or "not-yet-scoped"} | {zero-compute / fresh} |

## Closed questions (most recent first)

<!--
Questions the arc has resolved. Each row lists the question, the
chronicle that resolved it, and what the resolution was. Retire to
this table rather than deleting — the "why this arc stopped caring
about X" is itself information.
-->

| question | resolved by | resolution |
|---|---|---|
| {closed question} | [§X](../experiments-v2.md#{anchor}) | {one-line resolution} |

## Known failure modes / abandoned branches

<!--
Things tried and not pursued further. The "don't revisit X because
Y" ledger. Prevents re-running the same failed experiment because
its reason-for-failure wasn't recorded at claim level.
-->

- **{abandoned approach / failed attempt}** — reason it was dropped + chronicle link if any.

## Superseded readings (preserved per methodology §13)

<!--
As the arc narrows, earlier mechanism readings get superseded.
Record them here so the naming history is one place, not scattered
across chronicles. Include a commit hash for each supersession.
-->

- **{old mechanism name}** — superseded by {new name} at commit `{sha}` ({date}). Why: {one line}.

---

## Promotion criteria (when to consolidate to findings.md)

<!--
Pre-registered conditions under which this arc becomes a findings.md
entry. Lifted from methodology §5 (narrowing, not false→true flips)
and §24 (null results promote on equal footing).
-->

- **Positive promotion:** {e.g., "n≥20 replicated across ≥3 independent cells + zero-compute mechanism inspection"}
- **Null promotion:** {e.g., "load-bearing FAIL/INCONCLUSIVE that changes what downstream experiments should assume"}
- **Abandonment:** {e.g., "no new experiments in 30 days AND live-next-question is not scope-blocked"}
