# FWER audit — 2026-04-18 (supersedes 2026-04-17)

**Scope.** Chem-tape v2 track. Scanned `Plans/prereg_*.md` (QUEUED / RUNNING / BLOCKED), plus chronicled experiments in `docs/chem-tape/experiments-v2.md` over the last 30 days whose verdict has not yet been fully discharged in `findings.md`.

**Principle-22 compliance baseline.** Principle 22 was codified at commit `bc2936a` on 2026-04-16. Preregs authored before that commit default to **exploratory** unless they explicitly state a confirmatory classification with a named family.

**Supersedes.** `Plans/fwer_audit_2026-04-17.md` under-counted the F1 proxy-basin family by 2 tests: it omitted both §v2.4-proxy-4c Arm A preserve and §v2.4-proxy-4c BP_TOPK consume, each of which is a separate confirmatory McNemar test per the §v2.4-proxy-4c chronicle (line 2605 of `experiments-v2.md`). Today's reconciled F1 size = 3, not 1.

**Authoritative-source rule.** When an audit-file count disagrees with a chronicle's own FWER bookkeeping, the chronicle wins — chronicles are commit-anchored to the data, audit files are meta-summaries that can go stale. The 2026-04-18 audit is a reconciliation with the chronicle layer, not a reinterpretation.

---

## Families and current state

### F1 — `proxy-basin` family

**Claims gated:** `proxy-basin-attractor` (ACTIVE, last revised `4aa8b40`) + `decoder-knob-leverage-null` (NULL, initial promotion `0a2ffff`).

**Post-§22 confirmatory tests:**

| # | test | prereg | commit | paired McNemar statistic | classification source |
|---|---|---|---|---|---|
| 1 | §v2.4-proxy-4b | `prereg_v2-4-proxy-4b-seeded.md` | `f10b066` | χ²=18.05, p<0.0001 (BP_TOPK preserve) | prereg + chronicle |
| 2 | §v2.4-proxy-4c Arm A preserve | `prereg_v2-4-proxy-4c-replication.md` | `9135345` | χ²=18.05, p<0.0001 | prereg + chronicle |
| 3 | §v2.4-proxy-4c BP_TOPK consume | `prereg_v2-4-proxy-4c-replication.md` | `9135345` | χ²=18.05, p<0.0001 | prereg + chronicle |

**Post-§22 confirmatory-test count:** **3**.
**Corrected α (Bonferroni, family size 3):** α_FWER = 0.05/3 ≈ **0.017**.
**All members clear α_FWER by > 4 orders of magnitude.**

**Pre-§22 supporting evidence (NOT family members):**
- §v2.4 compute-scaling (§v2.4 alt / proxy-3 era): descriptive solve counts.
- §v2.4-proxy decorrelation: attractor-shift descriptive, no p-value.
- §v2.4-proxy-2, §v2.4-proxy-3, §v2.12 Arm A, §v2.14b: descriptive / effect-size-only.
These tests build the mechanism narrative but do not enter the FWER family at principle-22-strict accounting. If they are ever cited as gating a paper-level claim, they need retroactive classification — not guessed here.

**Post-§22 exploratory members (do not grow the family):**
§v2.4-proxy-4d decode-consistent (commit `cca2323`), §v2.4-proxy-5a bp sweep, §v2.4-proxy-5a-followup-bp-inspection, §v2.4-proxy-5a-followup-mid-bp, §v2.4-proxy-5b mutation_rate / -amended, §v2.4-proxy-5b-crosstask, §v2.4-proxy-5c-nontournament, §v2.4-proxy-5c-tournament-size, §v2.4-proxy-5ab-cross-probe-diff. All explicitly classified exploratory in their preregs.

**Pending confirmatory expansion (queued):**
`prereg_v2-4-proxy-5d-followup-cloud-reexpansion.md` — tests prediction P-1 (non-monotone dip-recovery replicates on seeds 20..39). Classified confirmatory; family grows to **4** on promotion, corrected α → **0.05/4 = 0.0125**. Existing 3 members clear 0.0125 by > 3 orders of magnitude — no claim integrity impact.

**At-risk claims in F1:** none. `proxy-basin-attractor` ACTIVE rests on χ²=18.05, p<0.0001 tests across three independent configurations plus a broad descriptive basis; `decoder-knob-leverage-null` is FWER-safe at family size 3 (cleared by the §v2.4-proxy-5b-amended BOTH-KINETIC data at exploratory level; its confirmatory gate is the §v2.15 family, not F1).

---

### F2 — `§v2.15 decoder-grid` family

**Claims gated:** `decoder-knob-leverage-null` (NULL, initial promotion `0a2ffff`).

**Post-§22 confirmatory tests:**
| # | test | prereg | statistic |
|---|---|---|---|
| 1 | §v2.15-bp1-k3-nexp | `prereg_v2-15-bp1-k3-nexp.md` | exact binomial P(X≤25\|0.60) = 0.0014 |

**Family size:** 1. **α_FWER = 0.05/1 = 0.05.** Cleared by p = 0.0014.

**No change since 2026-04-17.** At-risk claims: none.

---

### F3 — `safe-pop-consume-effect` family

**Claims gated:** `safe-pop-consume-effect` (ACTIVE — descriptive, explicitly non-confirmatory).

**Post-§22 confirmatory tests:**
| # | test | prereg | statistic |
|---|---|---|---|
| 1 | §v2.14g consume Arm A 4× | `prereg_v2-14g-consume-arm-a-4x.md` | McNemar p=1.00 |

**Family size:** 1. **α_FWER = 0.05.**

**No change since 2026-04-17.** The underlying claim is descriptive (solve-count + attractor-inspection), not p-gated; §v2.14g's null p-value is reported for completeness, not claim-gating. At-risk claims: none (acknowledged non-confirmatory basis).

---

### F4 — `constant-slot-indirection` family

**Claims gated:** `constant-slot-indirection` (NARROWED).

**Post-§22 confirmatory tests:** 0.
**Supporting evidence (pre-§22):** §v2.3 main + seed expansions, §v2.6 baseline, §v2.11 Arm A, §v2.13 k=5.

**No change since 2026-04-17.** Claim NARROWED rests on 80/80 mechanism-level replication (principle 8) + attractor inspection (principle 3); not vulnerable to FWER at current size 0.

---

### F5 — `op-slot-indirection` family

**Claims gated:** `op-slot-indirection` (ACTIVE).

**Post-§22 confirmatory tests:** 0.
**Supporting evidence (pre-§22):** §v2.1, §v2.2 Pair A + Pair B.

**No change since 2026-04-17.** Claim rests on 20/20 solve rate on multiple pairs plus across-family replication. FWER-safe at size 0.

---

### F6 — `plasticity-narrow-plateau` (**NEW — founded this session**)

**Claims gated:** `plasticity-narrow-plateau` (candidate, not yet promoted).

**Pending confirmatory test:**
`prereg_v2-5-plasticity-1a.md` — Arm A Baldwin_slope CI test. Currently QUEUED (BLOCKED on engineering + METRIC_DEFINITIONS additions); will enter the family at size 1 on sweep completion.

**Projected family size on first-test promotion:** 1. **α_FWER = 0.05.**

**At-risk claims:** none (family founded at size 1).

---

## At-risk claim summary

**None.** All six families are claim-robust under Bonferroni at current sizes. Specifically:

- F1 `proxy-basin-attractor`: three independent χ²=18.05 tests, p<0.0001 each, vs α=0.017 (or 0.0125 post-5d). Safe by > 3 orders of magnitude.
- F2, F3, F4, F5: all size ≤ 1 or rely on non-p-gated descriptive bases.
- F6: family founded at size 1.

---

## Outstanding compliance items

1. **Pre-§22 supporting tests in F1** have no explicit classification. The 2026-04-18 findings.md FWER block labels them "descriptive-exploratory supporting evidence, NOT confirmatory family members." If a future paper-level draft cites any of them as gating a claim, a retroactive classification + family-size bump is required.
2. **Yesterday's audit (2026-04-17) is superseded.** Anyone pulling from `Plans/fwer_audit_2026-04-17.md` must consult this file instead. The 2026-04-17 audit is preserved per methodology §13 (no silent deletion); a pointer at its top to this file would be courtesy.
3. **Per-sweep-counting convention.** When a prereg drives two independent sweeps (different arms, different decoders, different tasks) that each yield a separate McNemar p-value, each p-value counts as one family member (2 tests). This is applied for §v2.4-proxy-4c; future multi-sweep preregs should state the per-sweep test count explicitly to avoid under-counting.

---

## Recommended next actions

- **None required** for current ACTIVE / NARROWED / NULL findings.
- **Post-5d-v1 promotion:** if §v2.4-proxy-5d v1 (the §v2.4-proxy-5d-followup-cloud-reexpansion v1 sweep) replicates the non-monotone shape, promote to findings.md as a narrowing of `proxy-basin-attractor` and update this audit to F1 size = 4.
- **Post-plasticity-1a completion:** first entry in F6. Update this audit on promotion.
- **Next audit trigger:** after either of the above promotions, OR at the next scheduled morning briefing if preregs have grown by > 3 queued items since this audit.

---

*Audit generated 2026-04-18 at commit `3bf1ba7`. Emitted per research-rigor `fwer-audit` mode. Supersedes `fwer_audit_2026-04-17.md`.*
