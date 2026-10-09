# Does containing a block edit make the fitted bias useful?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 1606](../runs/2026-10-09-1606/strategy.md). The steward supplies
the proposal, sample size and decision rule. This is not an experiment registration.

**Question.** Does preserving the decoded suffix account for a useful part of the
C-chain block operator's advantage over ordinary C search? W/C is 1.23× on
then-addition and 1.28–1.38× on the other scored scopes. W uses no extracted fragment
content. Its benefit could come from containing changes, from proposing coordinated
chain content, or from their combination. This determines which operator to retain
when testing a future acquired decoder, without building another repertoire first.

The alternative changes variation while keeping the fitted table fixed. It is related
to the representation-locality question in [Rothlauf and Oetzel, *On the Locality of
Grammatical Evolution* (2005 working paper; EuroGP 2006)](https://madoc.bib.uni-mannheim.de/1255/1/ww_11_2005.pdf).
Their grammatical-evolution result motivates the question; it does not establish that
suffix protection helps this sequential decoder. Token locality is also not semantic
locality: one local stack edit can change every output.

**Reuse and narrow build.** Inspect the reviewed `research/main` implementation,
`fragment_operator.py`, `composition_search.py` and `fragment_reuse_run.py` (1036 code
`348f9e2`; later pre-solve runner `e9a04f8`). Reuse the sixteen 1246 C tables, 1036's
whole-library length laws and complete then-addition roster, D1331 length-three inputs,
32-token tapes, primitive executor, ordinary selection/crossover/mutation and exact
verifier. The current main checkout lacks these experiment runners; do not recreate
them. No source collection, fitter, library extraction or new bank is needed.

Source inspection shows that W runs **after ordinary offspring variation**. It draws
one C-chain block for a selected child (probability 0.2), conditionally encodes its
tokens, then re-encodes the following allele to retain its old decoded token. With
previous-token context, that one boundary repair preserves the entire remaining
decoded suffix; alleles beyond it are untouched. This is an implementation observation,
not a new efficacy result.

Compare incumbent W with a chain-block counterpart R that permits suffix propagation.
Keep the same selection of children, span/start law, chain draws, block encoding and
ordinary offspring path. At a fixed input child and shared draws, both must write
exactly the same decoded block and retain the prefix. R lets the next old allele decode
under the block's new final token and permits the consequent suffix changes. W instead
retains that boundary's old token. Do not substitute uniformly random block content.

Control the boundary's neutral allele refresh too: a concrete R implementation first
reads the token that its unchanged boundary allele would produce in the new context,
then draws uniformly within that token's conditional interval, just as W draws within
the preserved token's interval. This keeps R's immediate decoded output equal to the
unrepaired output while matching the conditional re-encoding operation. Both leave
alleles after that boundary unchanged. Specify and validate this law before scoring;
a raw deletion of the repair also changes whether a boundary allele is refreshed.
No-op blocks and blocks ending at the last position need explicit checks. Keep legacy
W replayable and isolate operator randomness from search/case streams.

A repaired point-mutation arm beside W and C would change block width and the added
edit schedule as well as locality. It can test a replacement procedure, but does not
isolate W's suffix intervention. Prefer the matched block comparison above for this
slot. Do not expand it into a factorial sweep.

**First experiment and answer.** Score R against W, keeping C as the practical reference.
Use all sixteen corpora and the complete then-addition roster, with paired initial
programs and case draws. Historical W/C rows are reusable only after hash, initial-state
and representative full-search replay checks; otherwise price fresh references before
admission. Preserve both source-family labels and corpus-level uncertainty. Then-addition
is development data. W's span law was itself derived from F's library; this comparison
does not establish a wholly corpus-independent block policy.

The primary decision is whether suffix preservation gives a worthwhile search-cost
increment **within this block operator**, with a fixed size, one 95% interval and an
explicit unresolved branch. The steward sets the worthwhile increment using the next
operator choice. Keep R/C visible: W beating a badly degraded R does not show how much
of W/C is due to repair. Show solve counts, capped-cost sensitivity, arithmetic mean
evaluations/time, and realized changes inside and beyond the block. Diagnostic audits
on identical input tapes establish intervention fidelity, not evolutionary efficacy.

If removing preservation loses useful performance, retain boundary repair in subsequent
acquisition tests. If R retains W's performance within a decision-relevant bound and
still helps over C, suffix protection is unnecessary at that resolution; coordinated
chain proposals remain the next candidate, without being identified as the sole cause.
If R is better, the presumption that containment helps is wrong here. A broad interval
needs a resolution price; failure to reject a difference is not sufficiency. Even a
clean repair effect does not explain C/T, identify semantic modules, or establish
evolutionary acquisition. C is still an external solver-corpus fit in every arm.

**Full cost and exit.** Allocate one experiment, **4–6 hours total**, including up to
two hours preparation, roughly 1–2 hours queue work, reviews, analysis and contingency.
Keep summed queue timeouts at **3 hours** and preparation at **120 minutes**. These are
allowances pending measurement. As a price anchor, 1350 ran 8,192 new then-addition
searches in 84 minutes; one 4,096-search arm would be about 42 minutes at that rate.
R may be slower, and adequate precision, replay and reporting must be priced at intended
concurrency. Failed historical pairing requires a revised complete price, not silently
unpaired inference. A probe-only stage retains the separate 60-minute timeout limit
and must price confirmation as well.

This is a complete one-cycle mechanism question: no second experiment is needed to
make its first result useful. Return to strategy after the result or a measured
validity/build/cost obstruction. No automatic point-edit study, new library, extra
bank or acquisition experiment follows. Shared C acquisition costs cancel in the
incremental W/R comparison; a future complete learning pipeline must still charge them.
