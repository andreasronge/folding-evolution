---
next: strategy
---
# Decision — 2026-10-11-1736 recurrent inherited library choice

**Park [55](../../questions/55-inherited-library-choice/question.md); no proposal; return to strategy.**
Root 55's budget is spent (2/2), as is every other root's (`research.py status`: 01, 10, 23, 55 at 0 left).
Strategy 1736 and the proposal both routed every outcome back to strategy, and no follow-up was funded.

**What the experiment showed** (commit `3a18ef5`; six order development cells, 24 saved R-all libraries,
P 256, lexicase, crossover 0.5; content and donor law supplied; [analysis](analysis.md)).
- With the inherited bit redrawn from Bernoulli(1/16) at rate 1/32, the R-all carrier bit stayed polymorphic and
  rose from 1/16 to a mean of **0.29 [0.23, 0.35]** in linked populations, against 0.06 neutral-bit and 0.05
  shuffled (L − N 0.23 [0.16, 0.30]; L higher in 24/24 libraries).
- The rise is bimodal: 46/144 populations above 0.5, 55/144 at or below the start. Selection is very weak while
  the bit is rare (+0.0017 per generation at f ≤ 0.25) and about ten times stronger once common.
- Primary: each population's own frozen law cost **0.805 [0.704, 0.913]** of the starting law q₀. The pre-set
  useful bar (upper < 0.90) narrowly missed; the "20% excluded" bar (lower > 0.80) also missed → **unresolved**
  by the frozen rule. The interval excludes 1. Both controls resolved (L/N 0.75 [0.64, 0.86], L/S 0.70 [0.61,
  0.80]); headroom present (q₀/R-all 2.12).
- The evolved law carries nothing beyond its dose: each endpoint's cost sits within 6% of the 1427 dose curve
  at its own q; the saving comes from the 43% of populations where the bit rose. Hand-set R-all is 1.71× [1.45,
  2.01] cheaper per search and needs no exposure; exposure repays against q₀ after about 16 searches.
- My forecast (0.95, mean f 0.13) was wrong. It assumed one constant selection coefficient; the data show strong
  positive frequency dependence.

**Why park, not continue or close.** The README says an unresolved result that a larger run could settle is a
reason to propose that run, unless it would not change a decision. Here it would not. The resolving run (a second
batch of six populations per library, ~70 min queue, ~4 h complete) would only move the result between "useful"
and "unresolved" at the 10% bar, and the analysis's resampling suggests even that only just reaches 0.90. Either
way the program's conclusions are the same:
- selection can acquire a cost-lowering frequency of a supplied law once selector loss is reversible;
- the acquired law is a dose, 1.7× worse than the obvious hand setting;
- nothing about content learning or transfer follows.
Not closed, because the pre-set rule did not resolve and only one mutation rate, population size, crossover rate
and library was tested. The reopen condition names the priced top-up and the more informative variant.

**Digest.** Root 55 now holds two beliefs (full experiment): linked selection raised the bit above both controls,
and the frozen law was cheaper than its start, by an amount the 10% bar does not resolve and only through its dose.
The 1427 probe's observations stay in the log.

**Critique digest check (notes 6–8), fixed.**
- 57's question.md no longer says (b)+(c) are "worth at most the small residual"; it now says the permuted library
  keeps a small net saving with component contributions and interactions unidentified.
- "Gradient disappears/vanished/gone" now reads "the strong intact-library gradient was not apparent in the point
  estimates" in the digest, root 10's question.md and 57's question.md.
- The digest's Overall paragraph now says "acquired on DG and order sources, DG libraries also on fresh gate-sum
  compositions".
- Correction entries were appended to 57's and root 10's logs; the earlier entries stay as written.
- The digest was compressed slightly to make room (former text logged in roots 01 and 10).

**Parked questions re-checked.** None is reopened.
- **23**'s condition needs a selectable signal in *token-frequency* learning; this signal is for a supplied
  structured law with 2.1× headroom.
- **50** and **54** are unaffected.
- **01/06** (mixing blocks rare forms) is consistent with the weak low-frequency selection seen here under
  crossover 0.5. That is a hypothesis, logged in 55, not a reopen.

**For the strategist** (about 18.5 h left; 19/40 experiments used). The inheritance line has now shown what a
dose-only selector over supplied content can show. Ranked candidates:
1. **Fresh content-family bank for the frozen R-all recipe** (root 10's largest gap; recommended at 1628):
   a stage-0 source census (≥ 25% of solvers build the family's helpers) before scoring, 7–9 h total. Tests
   whether acquisition generalizes beyond order helpers.
2. **Content choice by inheritance** (55 reopen branch): the same harness with the bit choosing intact R-all
   versus helper-scrambled R-hx at equal mix. Same dose, different content (known 2.35× contrast), so selection
   would have to discriminate content, not just turn up a dose. About 6–8 h. Expect the same weak rare-carrier
   selection; I would buy it only if the strategist wants one more inheritance result before stopping.
3. **55 precision top-up** (~4 h): not recommended, for the reason above.
4. **Stop**: reasonable if neither 1 nor 2 justifies its full cost.
