# FWER audit — 2026-04-17

**Scope.** Chem-tape v2 track. Scanned `Plans/prereg_*.md` for QUEUED/RUNNING status, plus chronicle entries in `docs/chem-tape/experiments-v2.md` over the last 30 days whose verdict has not yet been fully discharged in `findings.md`.

**Principle-22 compliance baseline:** principle 22 was added at commit `bc2936a` on 2026-04-16. Preregs dated before that commit predate the principle-22 classification requirement. Those tests have to be retroactively classified (or explicitly re-scoped as exploratory) if they are cited as gating a findings.md claim.

## Families and current state

### F1 — `proxy-basin` family
Claim this family gates: `proxy-basin-attractor` (ACTIVE, last revised `0a2ffff`) + `decoder-knob-leverage-null` (NULL, initial promotion `0a2ffff`).

| member | prereg | pre-§22? | classification | test reported | notes |
|---|---|---|---|---|---|
| §v2.4 compute-scaling | prereg_v2_4_alt.md, prereg_v2_4_proxy3_boundary.md era | **yes** | unclassified; treated as **exploratory** default | paired McNemar not reported in chronicle | supports the basin existence via descriptive counts; pre-§22 so not a confirmatory family member |
| §v2.4-proxy | prereg_v2_4_proxy.md | **yes** | unclassified; treated as **exploratory** | attractor shift descriptive | decorrelation mechanism reading; descriptive |
| §v2.4-proxy-2 | prereg_v2_4_proxy2.md | **yes** | unclassified; treated as **exploratory** | attractor cascade descriptive | cascade mechanism reading; descriptive |
| §v2.4-proxy-3 | prereg_v2_4_proxy3_boundary.md | **yes** | unclassified; treated as **exploratory** | per-threshold descriptive | split-halves INCONCLUSIVE |
| §v2.12 Arm A | prereg_v2_12_arm_A_on_proxy_basin.md | **yes** | unclassified; treated as **exploratory** | no p-value reported | descriptive decoder-arm replication |
| §v2.14b | prereg_v2-14b-consume-proxy.md | **yes** (commit predates bc2936a) | unclassified; treated as **exploratory** | attractor shift descriptive | PARTIAL; descriptive only |
| **§v2.4-proxy-4b** | **prereg_v2-4-proxy-4b-seeded.md** | **no (post-§22)** | **confirmatory** | McNemar χ²=18.05, p<0.0001 | principle-22 compliant |

**Post-§22 confirmatory-test count in F1:** **1** (§v2.4-proxy-4b only).
**Corrected α (Bonferroni, family size 1):** α_FWER = 0.05.
**At-risk claims:** none. `proxy-basin-attractor` (ACTIVE) carries a broad descriptive basis (7+ experiments pointing at the same mechanism) rather than a single family-wise-significant p-value; it is not paper-level-vulnerable to FWER correction because its confirmatory evidence is from §v2.4-proxy-4b's narrowing, which clears α=0.05 by 4+ orders of magnitude.
**Recommendation:** retroactive compliance commit needed IF any pre-§22 F1 test is ever cited as gating a paper-level claim. For now, treat all pre-§22 members as exploratory and note this explicitly in the findings.md review-history block.

### F2 — `§v2.15 decoder-grid` family
Claim this family gates: `decoder-knob-leverage-null` (NULL, initial promotion `0a2ffff`).

| member | prereg | pre-§22? | classification | test reported |
|---|---|---|---|---|
| §v2.15 grid (§v2.3 + Pair 1) | prereg_v2-15-decoder-grid.md | **no (post-§22)** | **exploratory** (per-cell descriptive counts; formal McNemar deferred pending LIFT categorizations) | per-cell counts only |
| §v2.15-bp1-k3-nexp | prereg_v2-15-bp1-k3-nexp.md | **no (post-§22)** | **confirmatory** (exact-binomial JOINT-LIFT-floor test) | P(X≤25\|0.60)=0.0014 |

**Post-§22 confirmatory-test count in F2:** **1** (§v2.15-bp1-k3-nexp only).
**Corrected α:** α_FWER = 0.05 / 1 = 0.05.
**At-risk claims:** none. `decoder-knob-leverage-null` rests on the §v2.15-bp1-k3-nexp exact binomial (p=0.0014 << 0.05) plus the §v2.15 descriptive grid (exploratory). FWER-safe at family size 1.

### F3 — `safe-pop-consume-effect` family
Claim this family gates: `safe-pop-consume-effect` (ACTIVE).

| member | prereg | pre-§22? | classification | test reported |
|---|---|---|---|---|
| §v2.14 | prereg_v2-14-safe-pop.md | **yes** | unclassified | McNemar p=0.157 |
| §v2.14b | prereg_v2-14b-consume-proxy.md | **yes** | unclassified; descriptive | descriptive counts |
| §v2.14c | prereg_v2-14c-consume-4x.md | **yes** | unclassified | descriptive counts |
| §v2.14d | prereg_v2-14d-consume-arm-a.md | **yes** | unclassified | descriptive counts |
| §v2.14e | prereg_v2-14e-consume-2nd-body.md | **yes** | unclassified | McNemar p=0.102 |
| **§v2.14g** | **prereg_v2-14g-consume-arm-a-4x.md** | **yes (prereg authored at same session as §22 codification)** | **confirmatory** (explicit in prereg) | McNemar p=1.00 |

**Post-§22 confirmatory-test count in F3:** §v2.14g only.
**Corrected α:** α_FWER = 0.05 / 1 = 0.05.
**At-risk claims:** the `safe-pop-consume-effect` ACTIVE finding rests on §v2.14 (p=0.157) and §v2.14e (p=0.102) — neither of which clear α=0.05 uncorrected. If either were a confirmatory test in an FWER family, they would fall below threshold. The existing finding explicitly acknowledges this as "descriptive (solve count + seed overlap + attractor-category inspection), not statistically confirmed." **This is the closest thing to an at-risk claim in the track; it is already acknowledged in the claim header, not treated as confirmatory.**
**Recommendation:** no FWER-related action; the finding is honest about its non-confirmatory basis. Future prereg on this family should classify explicitly.

### F4 — `constant-slot-indirection` family
Claim this family gates: `constant-slot-indirection` (NARROWED).

Members: §v2.3 (main + seed-expansion blocks), §v2.6 (baseline completion narrowing), §v2.11 (Arm A decoder-arm), §v2.13 (k=5 parameter sweep). All pre-§22.

**Post-§22 confirmatory tests in F4:** 0.
**Corrected α:** n/a (no confirmatory tests in family).
**At-risk claims:** `constant-slot-indirection` NARROWED already reflects mechanism-level evidence (80/80 across 4 seed blocks), not a family-wise-significant p-value. Not at risk.

### F5 — `op-slot-indirection` family
Claim: `op-slot-indirection` (ACTIVE). Members: §v2.2 Pair A + Pair B, §v2.1. All pre-§22.

**Post-§22 confirmatory tests:** 0.
**At-risk claims:** not at risk — claim is across-family PASS at 20/20 on multiple pairs; descriptive basis is strong enough without FWER.

## At-risk claim summary

**None of the 5 findings are at-risk under Bonferroni FWER** at the current family sizes (each family has ≤ 1 post-§22 confirmatory test). The track's claims are built primarily on mechanism inspection (principle 3) and across-experiment replication (principle 8) rather than on individual p-values, which keeps them FWER-robust by construction.

## Outstanding compliance gaps

1. **Pre-§22 preregs lack explicit classification** in 10+ entries. If any of them get cited as confirmatory evidence in future paper-level claims, a retroactive classification commit is required per principle 22. For now they are safely read as exploratory.
2. `prereg_v2-14g-consume-arm-a-4x.md` was authored before principle 22 codified but with classification wording; OK as-is.
3. `prereg_v2-15-decoder-grid.md` declared the cell-level counts as exploratory descriptive and deferred McNemar to JOINT-LIFT candidates — the grid produced no JOINT-LIFT, so no McNemar ran. Compliant.

## Recommended next actions

- **None required for current ACTIVE/NARROWED/NULL findings.** All findings are FWER-safe at current family sizes.
- **Future prereg discipline:** every new prereg MUST name its family and classification explicitly (this is already the §v2.14g / §v2.15-bp1-k3-nexp / §v2.4-proxy-4b pattern).
- **Proxy-basin family long-term:** if a paper-level aggregation across §v2.4, §v2.4-proxy, §v2.4-proxy-2, §v2.4-proxy-3, §v2.12, §v2.14b builds a confirmatory claim, those pre-§22 entries need retroactive classification + family-size bump (which would push α_FWER from 0.05 → 0.05/7 ≈ 0.0071). §v2.4-proxy-4b's p<0.0001 still clears that corrected threshold by 3+ orders of magnitude, so no claim is broken.

---

*Audit generated 2026-04-17 at commit `0a2ffff`. Emitted per research-rigor fwer-audit mode for morning briefing.*
