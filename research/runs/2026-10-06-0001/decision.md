---
next: strategy
---
# Decision: run 2026-10-06-0001 (12-generic-grammar-headroom)

**Close 12. No proposal; return to strategy.**

Outcome **row 1** on complete data (commit `a65ded0`, 35 min, clean). Of 162 frozen ten-token
canonicals in six same-primitive shapes, 11/16/16 survive the exhaustive ≤ 9-token alias screen
on the three domains. Gate and branch-then keep 0 cells everywhere, branch-else ≤ 2,
post-addition 4–8, and the two linear shapes 3 each by construction. No shape pair meets the
frozen ≥ 4-cell rule on any domain. The verdict holds for every alias cutoff in 0.70–0.85. The
witnesses name the obstacle: ADD distributes out of an IF_GT branch through CONST_0, DUP reuses
the condition, and the sign correlation of S and S+X gives near-aliases. Stage B was complete:
16 cells × 4 arms × 50 seeds, no top-up owed. Ten-token branch cells sit 2–10× above the
4 096 line under the frozen G (medians 8 192–41 728), and F and G-marg are above the line on
all 16 cells. G/U is 8.4–11.3× and G/G-marg 1.5–6.0× (paired capped-time ratios). Stages C and
D did not run, so no family-grammar contrast and no adaptation cost were measured.

Decision: close 12 because the question it was given is answered for the screened design
space. Headroom above G exists at ten tokens, but the six enumerated same-primitive shapes give
no two-family pair. The failure is semantic and identified, not a threshold or domain artefact.
Return to strategy because row 1 says so, and because strategy 0001 asked for a program review
"after another bank failure". This is the second bank failure. The proposal also predicted
row 1, so another steward-designed bank on the same alphabet would be a third unmeasured
redesign without a program-level choice behind it.

Scope of the negative: it covers only the six shapes with conditions and operands from
{S, M, m} on `v2_rmin`, three domains and the frozen rules. It does not show that every
length-≤ 10 family aliases, or that an alphabet change is required. No learned decoder or
transfer was tested; root 10's question remains open, with 3 of 5 slots left.

**Inputs for the strategist** (my reading, not a proposal):
1. **One-family transfer on post-addition.** On D1331/D2401, PA has 8 retained cells and a valid
   split: 6 training cells, and 2 holdouts (`(S?M:S)+M`, `(S?M:S)+m`) at G medians of 13.6k and
   18.7k. G-start inner searches reach ≥ 25/50 at a 65k budget on every cell. This would test
   learned-versus-fixed (A vs B) and overfitting (C) without the family-specificity contrast.
   A decoder trained on the six linear cells could be a structurally mismatched control, but it
   has no IF_GT, so it is not token-matched. Stage A/B data are reusable, but the outer-loop
   cost is unmeasured.
2. **Break the identities.** Add a fourth, weakly correlated reducer, or a comparison that is
   not sign-aligned with S. This needs Rust and executor changes and a new screen. The screen
   costs ~90 s and 4.9 GB per domain.
3. **Park root 10** if neither is judged worth a slot. The reopen condition would be a
   family design outside the 162 screened canonicals with ≥ 4 retained cells per family.

Avoid: relaxing the 80 % alias rule or the ≥ 4-cell rule after seeing the data. A pair first
appears only at 0.90. Also avoid reusing BE:S?M:(S+m) as a holdout without more training cases,
because two G seeds sat on training-perfect wrong programs there.

**Tree changes.** 12 is closed, and its log.md was created with the result and decision. The
root 10 summary and log are updated. The critic's digest-check notes 6–7 are fixed: 12's
"at best, learn similar rows" is removed, and the "whatever the cap / at any cap" wording is
qualified as the operational 4 096 rule in the digest, root 10 and 11's question.md. A
correction entry was appended to 11's log. The digest has a new section, "Assembly-family
screen". No parked question reopens: 02, 04, 07, 08, 09 and 11 were re-checked. F's sampling
lift on these cells is unresolved (0–2 hits per 10⁸), not absent, so 09's condition (a) is
not met.
