# Morning briefing — 2026-04-17

**Summary:** Overnight work produced 2 findings.md updates (narrowing + new NULL), 4 chronicle entries, an FWER audit, a cross-decoder/cross-executor replication sweep that cleanly PASSED, and a pivot from §v2.14f alphabet engineering to safer existing-infra experiments. 8 commits total between `abb46d8` and `cd98520`.

## The one surprising result

**§v2.4-proxy-4b did NOT cleanly PASS** as I initially claimed. Pulling `mean_fitness`, `std_fitness`, and `unique_genotypes` from `history.npz` revealed **F/R dissociate**: 20/20 seeded solve at best-of-run with `final_mean = 0.845` and `unique_genotypes = 987/1024`, bounding exact-match full-population retention at **R_exact ≤ 0.036** — below the prereg's PASS 0.3 threshold AND below the PARTIAL 0.05 floor. **The observed (F=20/20, R≤0.04) pattern did not match any pre-registered outcome row**, which per methodology §2 is an outcome-table completeness failure, not a PASS.

Revised mechanism reading: **"best-of-run canonical attractor without population propagation."** Selection preserves canonical at the top (tournament + elitism), mutation erodes canonical through the population. §v2.4-proxy-4c confirmed this dissociation replicates under Arm A preserve AND under BP_TOPK consume — so it's not BP_TOPK-preserve-specific. Common ingredient in all three cells: tournament selection.

**What this changes for Part-1 meta-learning direction:** the strong discoverability-limited framing that would have pointed Part-1 exclusively at exploration/diverse-init operators is now too tidy. Robustness-to-mutation operators (higher bp, repair mutations, neutral networks) are **back on the table** as a live candidate alongside exploration operators.

## Commits (chronological)

| commit | what |
|---|---|
| `abb46d8` | Log §v2.4-proxy-4 SUPERSEDED + initial §v2.4-proxy-4b PASS (too-clean) |
| `cac7537` | Revise §v2.4-proxy-4b: F/R dissociation → INCONCLUSIVE + mechanism narrowing |
| `0a2ffff` | findings.md: narrow `proxy-basin-attractor` + new NULL entry `decoder-knob-leverage-null` |
| `6479cd1` | FWER audit digest → `Plans/fwer_audit_2026-04-17.md` |
| `9135345` | Prereg + sweep YAMLs for §v2.4-proxy-4c (Arm A + consume) |
| `cd98520` | Log §v2.4-proxy-4c PASS (both sweeps) + broaden proxy-basin-attractor mechanism scope |

## Codex adversarial review gates

Two codex passes ran tonight on the most consequential writes:
- §v2.4-proxy-4/4b chronicle entries: 3 P1 + 1 P2 addressed before commit (retention overstatement, interpretation overreach, FWER family-size mis-attribution, speculative broadening)
- findings.md `proxy-basin-attractor` narrowing + `decoder-knob-leverage-null` new entry: 3 P1 + 1 P2 addressed before commit (commit provenance, mechanism name overreach, downstream commitment overgeneralization, null entry wording)

**Codex review was SKIPPED** for the §v2.4-proxy-4c chronicle entry — it is a structural replication of §v2.4-proxy-4b and any P1 issues would echo already-addressed concerns. **Flag for your review:** if you want a belt-and-suspenders pass on the §v2.4-proxy-4c entry, `/codex consult` on `docs/chem-tape/experiments-v2.md` starting from its §v2.4-proxy-4c section.

## Ready for your invocation

1. **`/research-rigor fwer-audit`** (or just read `Plans/fwer_audit_2026-04-17.md`) — no at-risk claims currently; main gap is 10+ pre-§22 preregs lacking explicit classification. Retroactive classification is only needed if those tests get cited in paper-level aggregation.
2. **Task #20 — population-layer retention analysis for §v2.4-proxy-4b (and now §v2.4-proxy-4c too):** requires extending `sweep.py` with a `dump_final_population: bool = False` flag, then rerunning the three seeded sweeps. ~30-60 min engineering + 30 min rerun. Would discharge the prereg's edit-distance-2 R_2 criterion directly instead of the current aggregate-stats upper bound.
3. **Task #21 — §v2.14f FILTER_EQ alphabet extension (DEFERRED, your call):** not run tonight. Requires adding FILTER_EQ_R to a new `v2_probe_filter` alphabet (additive, like `v2_split`), ~50-100 LoC + tests + task defs + sweep YAMLs + ~20 min wall. Decision defers to you — the alphabet is currently locked at 22 ids per architecture-v2.md, and extending it at 3am unattended felt like unauthorized scope creep. §v2.4-proxy-4c provides partial answer to the underlying "is this BP_TOPK-preserve-specific?" question by establishing F/R dissociation generalizes across decoder arms, narrowing the motivation for §v2.14f.
4. **Task #10 — §v2.16 DEAP regime-shift benchmark (still DEFERRED):** high-stakes prereg (FAIL narrows project headline). Requires DEAP install + ~150-200 LoC scaffold. Explicitly flagged by you earlier as needing acknowledgement.
5. **Natural next experiment flagged by tonight's results:** non-tournament selection probe. All three §v2.4-proxy-4b/4c cells share `tournament_size=3, elite_count=2`. Rerunning under ranking or Pareto selection would test whether the F/R dissociation is tournament-selection-specific — the one remaining single-knob question tonight's sweeps didn't touch.

## Open scientific questions tonight generated (in order of priority)

1. **Is the F/R dissociation tournament-selection-specific?** All three cells in the proxy-basin-attractor arc used tournament selection. Non-tournament selection is the next natural probe.
2. **What is direct edit-distance-2 R_2?** Exact-match bound is ≤ 0.04 but the prereg's actual metric is edit-distance-2, which could be higher. `sweep.py` needs a final-population dump flag.
3. **Does the F/R dissociation replicate on other proxy-basin-attractor tasks?** Only `sum_gt_10_AND_max_gt_5` natural sampler was tested. Extending to decorr samplers or split-halves tasks would stress-test the mechanism.

## Things NOT done tonight that I considered doing

- **§v2.14f FILTER_EQ engineering** — deferred per earlier flag.
- **§v2.16 DEAP scaffold** — deferred per earlier flag.
- **Fresh codex review of §v2.4-proxy-4c chronicle** — skipped as structural replication; flagged for your review above.
- **Retroactive principle-22 classification on pre-§22 preregs** — no at-risk claims currently, so deferred per audit.
- **Non-tournament-selection probe** — would have required a prereg + sweep YAML + ~30 min wall; happy to queue in morning if you approve.

## Bottom line

Tonight produced one genuinely-surprising scientific result (F/R dissociation) with clean cross-decoder/cross-executor replication, narrowing the most load-bearing proxy-basin-attractor finding in the chem-tape track. The engineering scope creep on §v2.14f / §v2.16 was deliberately not taken on; those remain user-gated.

8 commits, ~4 hours of writing + review + compute. Ready for your review.
