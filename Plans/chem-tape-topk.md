# Chem-Tape Top-K Decode-Breadth Sweep

**Purpose.** Diagnostic experiment that maps the BP→A decode-breadth axis on sum-gt-10 as a single integer sweep. Decides whether the residual BP<A gap (§3b: 1/10 vs 3/10) is purely about "how much of the tape gets executed" or whether something else (soft decode, §9) is needed.

See `docs/chem-tape/experiments.md` §8 for pre-registration.

---

## Mechanism under test

The current chem-tape decode (Arms B and BP) executes only the *single longest* bonded run. Top-K generalizes:

- Identify all bonded runs (maximal contiguous non-separator spans under the permeable rule).
- Select the K longest runs. Tie-break on equal length by leftmost position.
- Concatenate the selected runs in **tape order** (not length-rank order) and execute the concatenation as an RPN program.

K=1 is exactly Arm BP. K=∞ (= "all non-empty runs") differs from Arm A only in that hard separators (ids 14, 15) still gate out cells. This makes K an interpolation from BP toward A along a single semantically clean axis.

## Hypothesis

One of four pre-registered outcomes (§8):

1. **Monotone saturating at A:** gap is pure decode-breadth → promote K as a hyperparameter; §9 preempted.
2. **Monotone plateau strictly below A:** breadth is part of the cost → §9 promoted with sharper question.
3. **Non-monotone (intermediate K wins):** selective decode is the sweet spot → re-opens "scaffold preservation" mechanism on cleaner data.
4. **Flat:** binding constraint is elsewhere → §9 urgent.

The prior is weakly (1) or (2). (3) is the most scientifically interesting; (4) is the most disruptive.

## Sweep specification

**File:** `experiments/chem_tape/sweeps/sum_gt_10_topk.yaml`

```yaml
sweep_name: sum_gt_10_topk
base:
  task: sum_gt_10
  tape_length: 32
  n_examples: 64
  holdout_size: 256
  pop_size: 1024
  generations: 1500
  tournament_size: 3
  elite_count: 2
  mutation_rate: 0.03
  crossover_rate: 0.7
  backend: mlx
  log_every: 50
  arm: BP_TOPK        # new arm; permeable bond rule + Top-K decode
grid:
  topk: [1, 2, 3, 4, 8, 999]   # 999 acts as ∞; all bonded runs
  seed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

60 runs. Expected ~30 min at 4 workers, matching §3b's Rust-executor compute profile.

**Seed reuse:** seeds 0-9 are the same seeds used in §2b, §3b, §4a panmictic. Direct per-seed comparison against existing A (3/10), B (0/10), BP (1/10) data is possible.

## Implementation plan

### Layer 5 engine change (minimal)

Both NumPy and MLX engines currently expose:

- `_longest_run_under_mask(eligible)` — returns the leftmost-longest run mask.
- `compute_longest_runnable_mask(tapes)` — wraps the above with permeable eligibility.

Add:

- `_topk_runs_under_mask(eligible, k)` — returns a mask selecting the K longest runs in the eligibility mask; tie-break leftmost; cells retained in tape order.
- `compute_topk_runnable_mask(tapes, k)` — wraps with permeable eligibility.

NumPy implementation sketch:
1. Run-length-encode each row's eligibility mask.
2. Compute run lengths and starts.
3. Argsort by (−length, start) to get top-K indices.
4. Build the output mask by OR-ing the top-K run positions.

MLX path mirrors NumPy; bitwise parity test already exists (`test_chem_tape_engine_parity.py`) — extend with K ∈ {1, 2, 3, ∞} parity cases.

### Config surface

`ChemTapeConfig` already has `arm: str`. Options:

- **(a)** Introduce `arm = "BP_TOPK"` and `topk: int` field. Cleaner for the sweep, doesn't break existing arm semantics.
- **(b)** Overload existing `arm = "BP"` with an optional `topk` field defaulting to 1 (≡ current BP).

Preferred: (a). Keeps BP as a frozen reference semantics; makes the sweep config explicit; avoids silent changes to cached results under existing config hashes.

### Metrics

Extend `metrics.py` per-generation record with:
- `mean_num_bonded_runs` — population mean of "number of non-empty bonded runs per tape."
- `mean_total_bonded_cells` — how much tape is bonded in aggregate.
- Existing `mean_longest_run` stays (comparable across K).

These are arm-independent tape statistics; useful for reading the results.

### Reproducibility

Pre-existing test pattern applies: extend `test_chem_tape_reproducibility.py` with a Top-K case. Before running the sweep, assert:
- Top-K with K=1 produces bitwise-identical masks to existing BP on 5 random seeds × (B=64, L=32).
- Top-K with K=999 produces bitwise-identical masks to "all non-separator cells in tape order" on the same fixtures.
- NumPy and MLX engines produce bitwise-identical Top-K masks on the same fixtures.

Sweep output directories are keyed by `ChemTapeConfig.hash()`; adding `topk` to the config hash is automatic if it's a dataclass field.

## Decision rule

On completion, record in `experiments.md` §8 the solve-count table across K:

| K | solved / 10 | median gens-to-solve | max best-ever | median longest-run (final) |
|---|-------------|----------------------|---------------|----------------------------|

Reference baselines on the same seeds (from §2b and §3b):
- A: 3/10 (seeds 2, 8, 9)
- B: 0/10
- BP: 1/10 (seed 2)

**Verdict on §8:**
- (1) saturating-at-A: K=8 or K=999 solves ≈ 3/10 with monotone rise from K=1.
- (2) plateau-below-A: K=999 solves strictly less than 3/10, with monotone rise that flattens.
- (3) non-monotone: some K ∈ {2, 3, 4} outperforms both K=1 and K=999.
- (4) flat: all K ∈ {1, 2, 3, 4, 8, 999} give 0-2/10 with no visible trend.

Seed-level inspection (§4h-style) of any K=999 failures on seeds {1, 15, 19} — the A-solved but BP-unsolved seeds — tells us whether separators are gating solutions the full-tape arm needs, which would suggest a further decode relaxation test.

## Out of scope for this probe

- **Other tasks.** Top-K on count-R / has-upper is cheap but not diagnostic — the sum-gt-10 gap is the question. If §8 produces a clear outcome, one-off reruns on count-R and has-upper are a follow-up, not part of the decision.
- **Island version of Top-K.** The §4 island baseline is confounded enough already (§4f still pending). Keep §8 on panmictic pop=1024 for clean comparison to §3b.
- **Soft-decode overlap.** §8 does not touch mutation rates. Any mutation-rate redesign is §9, contingent on §8's outcome.

## Exit criteria

- All 60 runs completed, results committed with commit hash recorded per `CLAUDE.md` guidance.
- `experiments.md` §8 updated with the solve-count table and one of the four pre-registered verdicts.
- §9 either promoted (with a refined hypothesis) or demoted (with §8 as the documented reason).
