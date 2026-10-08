---
status: closed
tags: [compositional-transfer, fresh-bank, then-addition, comparison-gate, external-fitting, solver-corpus, context, token-control]
budget: {experiments: 1, used: 0}
---
# Do the frozen comparison-gate corpus fits keep context's advantage over token fitting on a fresh bank of a new shape?

Current summary: **closed after run 1548 (answered at this scope). On the fresh, semantically
selected then-addition bank (16 cells, gates F>m and M>F only), the 32 frozen comparison-gate
tables gave C/T 2.12× [1.86, 2.41] over 16 corpora (16/16 corpora, 14/16 cells individually
resolved; 1.96× with unsolved at 1 × cap, 1.74× on pairs both arms solved). That is a resolved
shrinkage from the same corpora's own-family training gain, 0.68× [0.57, 0.81]; on v1's
within-shape holdouts (development bank, row D) C/T was 2.60× [2.31, 2.92]. The C-over-T
advantage was larger for BE-fitted corpora than for PA-fitted ones, by 1.38× [1.13, 1.68]
(a ratio of C/T ratios, not a direct C_BE-versus-C_PA speed comparison; secondary).** Both fits beat G4
descriptively (C 3.9×, T 1.8×, unpaired). The bank, opened to answer critique 1534's blocking
note, has the same 13-token inventory as v1 (five INPUTs, five reducers, GT, ADD, IF_GT): 240
programs, 86 distinct non-constant behaviours, 37 survive v1's ≤9-token alias screen, 16 agree
with every v1 behaviour on fewer than 80% of inputs. It was built and SHA-pinned before any
search and is now a development bank. Not shown: what carries the gain (K unscored, so emitted
frequencies are not separated from order), why it shrinks (branch placement, gate choice and
near-alias density changed together), uncapped speed, or transfer to other shapes.

Competing explanations:
- A: C carries assembly preferences reusable on a new arrangement of the same primitives;
  C/T on the fresh bank resolves above 1.
- B: C's gain is specific to the shapes it was fitted on (BE/PA order); fresh-bank C/T is bounded
  under 1.10×.
- B': C transfers within shape (v1 holdouts) but not across shape (this bank); read from the
  two rows of run 1548 together.

Scope limits: external fitting, not evolutionary acquisition; C versus the restricted token fit,
not an isolated token-order mechanism (K unscored); one alphabet, domain, cap and shrinkage;
the bank was designed after v1 results were seen, but it was selected semantically only.

Where they stand after run 1548: A supported at this scope; B ruled out on this bank (LB 1.86);
B' ruled out in its strong form, but the resolved cross-shape shrinkage is consistent with a
shape-dependent component.

Related: [root 10](../question.md), [25](../25-comparison-gate-transfer/question.md),
[run 1548 analysis](../../../runs/2026-10-08-1548/analysis.md),
[run 1548 decision](../../../runs/2026-10-08-1548/decision.md),
[24](../24-comparison-gate-bank/question.md), [critique 1534](../../../runs/2026-10-08-1534/critique.md).

Reopen if: a second fresh shape passes the same semantic screen (to test whether the gain
generalizes beyond these two gates), or a mechanism study needs this bank's frozen C/T rows as
its reference (e.g. scoring the frozen K tables on row F's seeds).
