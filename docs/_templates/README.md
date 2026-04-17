# Research Documentation Templates

Small templates for the folding-evolution research lifecycle. Each template enforces the lessons in [`../methodology.md`](../methodology.md) by making the required fields part of the structure.

## The four-document flow

```
Plans/prereg_<name>.md       docs/<track>/experiments.md    docs/<track>/arcs/<arc>.md    docs/<track>/findings.md
──────────────────────       ────────────────────────────   ────────────────────────      ──────────────────────
pre-registration              chronicle entry (per run)      reasoning trail (live)         durable claim (scope-tagged)
[prereg.md]                   [experiment_section.md]        [arc.md]                       [findings_entry.md]

    pre-register  ──run──▶   record result  ──refresh arc──▶   promote claim when ready
    (before compute)          (after compute)                    (after replication)
```

The arc doc is the scaling layer between chronicle (one experiment, frozen) and findings.md (one consolidated claim). It carries the reasoning trail across a chain of related experiments so readers can reconstruct the state of an inquiry without re-reading every chronicle. Arc docs are **intentionally live** — rewritten in place as the arc narrows — unlike chronicles and findings.md entries, which are append-only with supersession markers. Keep each arc doc ≤ 1-2 screens; when it grows past that, either consolidate to findings.md or split the arc.

Each template is short and opinionated. Fields that are not optional are the load-bearing lessons from methodology.md — remove them and the lesson silently decays.

## Templates

| file | when to use | enforces |
|------|-------------|----------|
| `prereg.md` | before any new sweep | methodology principles 1, 2, 2b, 4, 6, 20, 22, 25, 26, 27 |
| `experiment_section.md` | when a sweep finishes | principles 3, 10, 12, 13, 18, 21, 23, 25 |
| `arc.md` | when a mechanism question spans ≥ 2 related experiments; refresh on every chronicle that touches the arc | principles 5 (narrowing trail), 13 (supersession visibility), 19 (live-next commitments) |
| `findings_entry.md` | when promoting a claim (positive or null) to a findings ledger | principles 5, 16, 17, 18, 24 |

## Status vocabulary (standardized)

Use exactly one of these tokens in every status line. Do not invent new ones.

| token | meaning |
|-------|---------|
| `QUEUED` | pre-registered, not yet run |
| `RUNNING` | compute in flight |
| `PASS` | pre-registered acceptance criterion met |
| `FAIL` | pre-registered rejection criterion met |
| `INCONCLUSIVE` | neither criterion met (usually budget-limited or ambiguous) |
| `SUPERSEDED` | result still stands but a later experiment has narrowed or replaced the claim |
| `FALSIFIED` | a later experiment has shown the claim is wrong |

**Findings entries** use a narrower vocabulary: `ACTIVE`, `NARROWED`, `NULL`, or `FALSIFIED`. `NULL` is for first-class negative claims ("X does not Y under Z") — principle 24 requires them to be promoted on equal footing with positives.

`SUPERSEDED` and `FALSIFIED` always carry a forward link to the superseding experiment (methodology §13).

## Commit-hash discipline (non-negotiable)

Every status line cites the commit hash that produced the result. No exceptions, even for transient "I'll rerun" data. See methodology §12.

```bash
# quick snippet for capturing the hash at run time
git rev-parse --short HEAD > experiments/<track>/output/<sweep>/COMMIT
```

## When to create each document

- **Pre-register before running** — even for 10-minute sweeps. Pre-registration cost is sub-1% of compute cost; the information gain from a committed outcome table is decisive. Principle 2.
- **Chronicle every run** — experiments.md is the lab notebook. Every sweep gets its own section whether it passes, fails, or is inconclusive. Principle 13 (retract explicitly, do not delete).
- **Promote claims selectively** — only durable claims (replicated or load-bearing) enter findings.md. A finding is a commitment that downstream experiments will build on it; pay for that commitment by writing it down with full scope tags. Principle 18, 19.

## Keeping the kit alive

When an experiment contributes a new lesson worth adding:

1. Add the case + takeaway to `methodology.md`.
2. If the lesson is structural (affects what a template must collect), update the template here.
3. If the lesson is procedural (affects when to invoke), update the skill at `.claude/skills/research-rigor/SKILL.md`.

Methodology is the ledger. Templates are its enforcement. Skills are its triggers.
