# Log: 02-fixed-target-sampling

## Seeded 2026-10-04 from prior work

- §27 (commit cd7d463; write-up b66f0d2): pivot night 1, folding vs direct encoding, Phase A (20M paired random genotypes per length) + Phase B (evolution, 50 seeds) → maps differ in bias (rank corr 0.19–0.30); folding solves more often where the maps differ (e.g. count∘rest(products) 47 vs 21/50); the loop has no neutral drift (87–89% of unsolved populations hold one behaviour); evolution no better than random search; steering not testable. [notebook §27](../../../../docs/map-bias/notebook.md), [findings item 17](../../../../docs/map-bias/findings.md)
Decision: run night 2 with tie rules, a `rest`-character weight and matched random search because night 1 tested a race between maps, not steering (Plans/map-bias-pivot-night2.md, 70b4aba).
- §28 (commits f483aaf + a86c49c; write-up 907e0c8, review 055cc28): pivot night 2, tie rules, `rest` weight 0.2/1/5, random search at every budget → evolution is mostly a worse sampler than random search (ratio 0.03–0.75 for fold); beats sampling only on direct count∘rest(employees) (1.3–4.6×); tie rules do not restore diversity; raising the `rest` weight raises count∘rest solve rates in both maps, sublinearly in P(exact). [notebook §28](../../../../docs/map-bias/notebook.md), [findings item 17 "Night 2"](../../../../docs/map-bias/findings.md)
Decision: keep the rarity ladder as optional background (no plan file) and park steering because populations hold one behaviour under every tie rule (findings "Open", 055cc28).
Decision: move the main line to shared-helper reuse (Plans/shared-helper-reuse.md, 826fb68) because nights 1–2 answered which map samples fixed-target solvers more often, not the building-block question.

Status at seeding: parked. The rarity ladder has not been run.
