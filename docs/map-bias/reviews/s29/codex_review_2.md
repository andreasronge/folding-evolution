codex
Multi-output tracking produces inconsistent statistics when used with the existing task-alternation feature. Test execution was blocked by sandbox restrictions and MLX initialization.

Review comment:
- [P2] Update census targets when the active task changes — /Users/andreas/developer/folding-evolution/src/folding_evolution/chem_tape/evolve.py:1056-1058
  When `track_shared` is combined with task alternation (for example, `mbs_three` followed by `mbs_xor`), the census retains the initial task's output tags and labels while `cases` contains results for the current task. Consequently, the same record reports exactness against the old three-output goal and `train_perfect` against the new single-output goal; `track_runs` also continues counting the initial output tags. Rebuild the tracking context on task flips, or explicitly reject task alternation with these multi-output trackers.
