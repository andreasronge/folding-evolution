---
next: strategy
decision: continue
node: questions/01-map-bias/08-evolve-bias
new_question: questions/01-map-bias/09-generic-bias-speedup
---
# Decision — 2026-10-05-1705

**Hand to the strategist; 08 stays open with its last slot unspent; open sub-question 09.**

The run is complete and clean (650 runs, 20 min, all 642 solvers re-verified exact) and
returned the pre-registered **Partial** outcome:

- matched vs uniform: **faster** in both families (4.33×, 3.58×; lower bounds 2.6×, 1.9×).
  B ("supply, not success") is out for these tasks.
- matched vs mismatched: **unresolved** in both (1.66×, 1.80× after 100 pairs).
- matched vs hand-set: **no difference** in both (0.93×, 1.08×).

The plan's frozen route for Partial is "strategy, with the last slot unspent". I follow it.

**Why not spend 08's last slot now.** The only contrast left open in 08 is matched vs
mismatched. Its point estimates sit at 1.7–1.8×, under the 2× the proposal fixed as
worthwhile. More seeds would at best show "real but small"; it would not change what we do.

**Why open 09.** The unregistered surprise is that the mismatched vector, with no sampling
lift on these holdouts (1.02×, 1.33×), is itself 3.3× / 1.9× faster than uniform. Most of
the matched gain is generic, and sampling lift does not predict evolution speed
(pass-through 0.35–3.2). That contradicts the simple reading of item 12 and asks a new
question: what in a frequency vector does evolution use? Three explanations (shared INPUT/GT
scaffold, junk-op suppression, shortcut stepping stone) can be separated by one cheap run
(~30 min; arms sketched in 09) plus a free decode of 1705's shortcut genomes. The tree rule
is to give a new question its own folder, so 09 is open with budget 2. It is a sub-question
of the root, so it draws on the root's 2 remaining experiments.

**Why not propose 09 directly.** The plan pre-registered strategy as the next step, and the
root has only 2 experiments left. Whether to spend one on 09, on 08's specificity, or to
move the program (heritable bias, decoder rules, 02) is the strategist's call.

**Options for the strategist, my ranking.**
1. 09's arm test (uniform, mismatched, INPUT+GT only, suppression only on sum>2 / max>2).
   It explains the run's main surprise and decides what a heritable bias would need to carry.
2. Close 08 and stop part 2 here, with "yes over uniform, mostly generic, a hand-set scaffold
   suffices" as its answer.
3. 08's last slot on specificity — not recommended (see above).

**Parked questions.** None reopens.
[02](../../questions/01-map-bias/02-fixed-target-sampling/question.md) still needs the
owner's wish, but it is relevant: on TAG threshold tasks with lexicase, evolution beat
computed random search 9–40× in every arm, unlike the fixed-target picture in §28. That
does not meet 02's condition; it is worth the strategist's attention.
[07](../../questions/01-map-bias/07-shared-arrival/question.md) has no B-helper copy or
replay; [04](../../questions/01-map-bias/04-random-start-discovery/question.md) depends on 07.

**Tree changes.** 08: log entry, summary, explanation states (B out; A half met; C carries
the evolution gain; A' holds at cell level), stop rule and reopen condition updated. 09
opened (question + log). Root 01 summary and Related updated. Digest: new bullet on the
evolution result; the product-model bullet notes its out-of-sample failure; the §28 bullet
notes 1705's 9–40× over random search; open-question list updated.
