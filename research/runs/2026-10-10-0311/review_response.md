Code review response to `code_review.md`

Blocking issue 1 addressed: first-batch median yield below 4/16 no longer participates in either admission calculation. It remains a discovery reading in preparation reasons and source summary; every build’s empty-cell/corpus/library incidence is retained. Empty builds proceed through unchanged G4/fragment fallbacks. No extra degeneracy stop, attempt increase, arm or protected-target search was added.

Minor issues addressed: bank validation restores the caller’s safe-pop mode even on an exception; preparation captures elapsed time once for both admission and its frozen record; plan.md specifies the executable-token screen’s NOP slots and excluded separators. Other minor notes require no change: paired seeds, conservative baseline bootstrap and conditional precision scenarios remain as reviewed.

Verification: 214 relevant tests passed. Full-mode regression dispatches all 192 development jobs for median yields 0 and 3 with empty libraries; runtime bounds remain enforced. Fresh production CLI prepare/score smoke used two builds at cap 8192, reported median yield 0 with admission true, and completed 48 development searches across G4/A8/O. All expected queue artifacts exist; protected performance remains untouched. The smoke report labels all-capped comparisons uninformative. Full-cap sustained-load calibration remains the queued preparation’s responsibility.

The updated task plan and queue remain in this main-checkout task folder. Queue timeouts are unchanged at 25+30=55 minutes. Only implementation/test files are committed on the task branch.

Review fixes committed as `09c850dac6de09c4d6bc3b679d4f3d489abe603d` on `research/2026-10-10-0311`. Worktree status is clean; the commit contains no `research/` paths.
