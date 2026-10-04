codex
The sweeps and latent-tag changes appear consistent with the plan, but the report can incorrectly declare majority establishment by excluding seeds that lost exact solutions.

Review comment:
- [P2] Count all seeds when determining majority establishment — /Users/andreas/developer/folding-evolution/experiments/chem_tape/s30_report.py:152-153
  When some seeds end with no fully exact individuals, this divides by only the surviving seeds (`with`), rather than all seeds (`n`). For example, two wins and 28 seeds without exact solutions would be reported as establishment in a majority of seeds. Use all seeds as the majority denominator; excluding lost solutions changes the experiment's establishment conclusion.
