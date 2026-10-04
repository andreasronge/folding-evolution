codex
Multi-output evaluation shares context-dependent memoized values between outputs, producing incorrect predictions for cyclic references. The issue was reproduced directly.

Review comment:
- [P2] Isolate memoized run values between output evaluations — /Users/andreas/developer/folding-evolution/src/folding_evolution/chem_tape/tagged.py:246-247
  When output runs reference one another, evaluating all output tags with the same `memo` makes later outputs reuse values computed in a different recursion context, bypassing cycle detection and depth limits. For example, two runs that each execute `RECV(other); PUSH_1; ADD` produce `[2, 3]` with `out_tags=(0, 1)`, although independently evaluating each output produces `[2, 2]`. This makes predictions and knockout classifications depend on output order. Reset the run memo for each output root, or include the recursion context in its key.
