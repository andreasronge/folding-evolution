codex
The report merges the new G2 cohort into its historical reference, and the new mate modes leave lineage records inconsistent with actual reproduction.

Full review comments:
- [P2] Keep G2 runs separate from the §31 reference — /Users/andreas/developer/folding-evolution/experiments/chem_tape/s32_report.py:134-137
  When the report receives both the G2 sweep and `--g-root`, both sets have arm `G` and the same cell, so this grouping merges seeds 0–49 and 50–99 into one 100-run row labeled `G (§31)`. This hides the additional-seed results and misattributes their counts and timing to the reference. Preserve the source cohort in the grouping key so G2 and the reference produce separate rows.
- [P2] Record the actual crossover mate in lineage data — /Users/andreas/developer/folding-evolution/src/folding_evolution/chem_tape/evolve.py:604-604
  With `track_lineage=True` and a non-default mate mode, reproduction still records the selected index `j` as the second parent even though `_mate` replaces that parent. Self-mating therefore reports an unrelated ancestor, and random mating reports a population ancestor that contributed no material. Update lineage handling in both reproduction paths to represent the actual mate, or reject lineage tracking for unsupported mate modes.
