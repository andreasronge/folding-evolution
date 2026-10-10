---
next: strategy
---
# Decision 2026-10-10-2254: close 43, return to strategy

**Outcome.** The third attempt at frozen native A8 versus family-blind closure-based subtree GP ran to
completion (commit `c32ff04`; all gates passed; 896 rows per family; every solver re-verified on D625;
[analysis](analysis.md)).

- **DG (primary):** Q = cost(tree) ÷ cost(A8) = **0.961 [0.683, 1.352]** at 2 × cap. The whole interval
  lies inside the [0.67, 1.5] margin, with its lower end 0.013 above it. An A8 advantage of 1.5× is excluded;
  a tree advantage up to about 1.46× is not. The 1 × cap sensitivity, 0.785 [0.583, 1.055], is unresolved.
  This is not equality. A8 solved 314/384 and tree GP 202/384. When tree GP solved it was about 8× faster
  (median 6 784 against 57 088 evaluations). Its failed searches crowded the 32-token cap.
- **Arithmetic economics:** A8 saves 85 714 [47 278, 123 791] evaluations per DG search, so it repays its
  acquisition after about 146 [99, 269] searches per build. In worker time tree GP is 1.6× slower per
  evaluation.
- **TS (descriptive):** Q 0.175 [0.142, 0.217]. Tree GP solved 382/384 and was cheaper on every cell; A8
  never repays there.

**Decision: close 43; next: strategy.**

- The question is answered within its scope. Frozen A8 has no worthwhile geometric search-cost advantage
  over this untuned tree GP on DG, and tree GP is cheaper on TS. The comparison landed on the plan's
  pre-registered row "PASS partial, bounded geometric difference / positive savings, interval excludes
  zero". That row's action is to redirect learning toward an increment over tree search, not to price a
  fresh-bank A8 test.
- The plan and strategy 2214 both route the result to strategy and forbid tuning or top-ups. Root 10's
  budget is spent (35 of 35), so no root 10 proposal could run without a strategist allocation anyway.
- I am writing no proposal. The next step is a program-level choice: whether root 10 continues, and with
  what comparator. That decision is the strategist's.

**For the strategist (suggestions, not commitments).**

1. *Cheapest next look, no new search:* a restart analysis of the saved 2254 tree rows. Tree GP solved
   179/384 DG searches within 65 536 evaluations, and 58 within 4 096. Restarting at a fixed budget (Luby et
   al. 1993, a known technique) might beat A8's mean cost on DG. This is post hoc on development data, so it
   could motivate a pre-registered arm but could not be a result on its own.
2. *The increment the plan points to:* use what A8 learned *inside* tree GP, for example A8's fragment
   library as subtree seeds or as a mutation source. The closest known techniques are module/library
   acquisition in GP (Koza's ADFs; Angeline & Pollack's GLiB) and library learning (DreamCoder); literature not searched this cycle. This would
   need new code and its own question.
3. *Or move on:* root 10 has run 35 experiments. Its strongest current claims (fitted context and fragments
   beating hand-set and token baselines) were all measured against tape-search baselines. Against
   conventional tree GP the A8 line gave no worthwhile geometric advantage on DG. A program review may
   decide that the core question is better served elsewhere.

**Parked questions re-checked.** None of the parked questions (02, 04, 07, 08 and 09 under root 01; root 23) has a reopen
condition that a tree-GP baseline result meets. Question 40's reopen clause anticipated "A8″ against a
stronger uninformed baseline". Question 43 has now answered that on the spare DG cells, so 40 does not need
reopening.

**Digest check.** Critique note 6 found no overclaim to fix. The digest now records 43 as a belief: a
complete pre-registered experiment, with the TS contrast labelled descriptive and the DG result stated as
"no worthwhile advantage", not equality.
