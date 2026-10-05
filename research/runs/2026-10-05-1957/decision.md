---
next: strategy
---
# Decision: 2026-10-05-1957 shortcut-veto reproduction (09)

**Park 09 again. No proposal; the program goes to the strategist.**

The run did what its frozen rules said. The 50-seed pilot was clean (200/200 solved and
re-verified, identity checks 100/100, veto never leaked), but power for "P_R upper < 1.25 when
P_R = 1" was 0.48 / 0.53 at n = 600 / 800, under the 0.80 gate, so the main stage did not run
([analysis](analysis.md)). There is no registered contrast and no outcome label. The plan calls
this a feasibility result, not evidence against the stepping stone (G3), and I log it that way.

Why park rather than close or continue:
- The [strategy](../2026-10-05-1945/strategy.md) and the proposal committed to one valid
  experiment on this threshold line and a stop whatever the result. Running stage 2 now would be
  a second look after seeing the pilot.
- 09 has used both experiments; root 01 has none left (`research.py status`: left=0 everywhere).
  Any further run under 01 needs the owner to raise the budget.
- 09 is not answered, so it is not closed. Reopen condition (c) is used up; I replaced it with a
  narrow, owner-funded rerun (n ≈ 1600 or a model-based power gate). The reviewer showed the
  gate's power estimate swings 0.05–1.00 under resampling of the pilot, and n ≈ 1600 fits one
  queue, so the stop says "this gate was not met", not "no affordable design decides".

What changed in belief (pilot strength, in the digest): the exact max>2 shortcut is the usual
last step to the sum>2 solve (immediate parent in 55/60 exposed runs) in both uniform and R, and
vetoing it delays but never prevents the solve (100/100), because near-max programs take over.
Whether it explains R's advantage over uniform is unmeasured.

Parked questions re-checked: none reopens. 08 needs 09 to *show* what a heritable bias must
carry; it did not. 07/04 have no B-helper handle; 02 still needs the owner's request. All have
no budget left under root 01 in any case.

Why `next: strategy`: no open question under 01 deserves another experiment, and none can run
without a new budget. The strategist should decide whether root 01 ends here, whether the
owner should fund the 1957 rerun at n ≈ 1600 (my view: worth it only if the program wants
"bias toward useful intermediates" as a design target for a heritable map; the pilot already
says the exact intermediate is replaceable), or whether a new root (e.g. a transfer target
beyond constant substitution, as 1945's strategy suggested) should take over.
