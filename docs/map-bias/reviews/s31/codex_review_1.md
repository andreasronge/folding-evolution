codex
The dose-response plot combines incompatible definitions of establishment, potentially distorting the experiment's main comparison. Tests could not run because sandbox restrictions caused the installed MLX backend to abort during collection.

Review comment:
- [P2] Apply the same win criterion to all crossover-dose points — /Users/andreas/developer/folding-evolution/experiments/chem_tape/s31_report.py:153-157
  When `--s30` supplies the crossover 0 and 0.7 endpoints, their `win` counts come from `s30_report.summarise()`, which uses the 256-individual census, includes elites, and requires only one fully exact individual. The new intermediate points instead use the complete non-elite population and require at least 20 exact individuals. A run retaining only an exact shared elite can therefore count as a win at an endpoint but as no solution at an intermediate rate, creating an artificial crossover-dose effect. Reclassify the §30 final populations with the same `outcome()` criterion before combining these points.
