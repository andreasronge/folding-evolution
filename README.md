# Folding Evolution

GP/ALife research project: protein-inspired genotype-phenotype mapping for genetic programming.

## License and Citation

This repository is shared for visibility into ongoing personal research and
learning work. It is not released as open source software.

Code, documentation, and associated materials are `All rights reserved`. If
you want to reference this project, please use the citation metadata in
[`CITATION.cff`](CITATION.cff). If you want permission to reuse material from
the repository, please contact the author or open an issue first.

**Active tracks:** chem-tape v2 probe wrapping up (§v2.5-plasticity-2d primary cell). CA developmental revival starting — shifting from "can the CA compute?" to "is the CA actually developing?" See [Plans/ca-developmental-revival.md](Plans/ca-developmental-revival.md).

## Core Question

Does a developmental encoding enable qualitatively different evolutionary dynamics than direct encoding — specifically, the ability to discover and propagate rare compositional structures that direct GP cannot reach?

## Prior Results (Folding Track — Complete)

The original 2D-grid folding track established the foundational answer:

- Folding loses on static metrics (neutrality, crossover preservation) vs. direct encoding
- Folding wins on evolutionary dynamics: discovers solutions direct GP cannot reach, recovers under fitness-regime shifts
- The 3-bond complexity ceiling was broken via Pareto scaffold preservation (§1.11/§1.13): S5 reached in 78–92% of seeds
- **Key mechanism:** Altenberg's constructional selection — the static/dynamic discrepancy is explained by pleiotropy enabling structural reorganization under selection pressure, not by neutrality per se

Full results: [docs/folding/findings.md](docs/folding/findings.md).

## Active Track: Chem-tape v2

Chem-tape is a 1D redesign: a token tape with per-cell bond bits, decoded as a postfix (RPN) stack program. The v1 experiments established a **body-invariant-route** mechanism — when two tasks share a token-identical body and differ only in a single slot binding, evolution discovers the body once and absorbs task variation through slot indirection.

**v2 north star:** Does this mechanism scale with expressivity, or is it a v1-scale artifact?

v2 adds an extended alphabet (~30 tokens: MAP-family ops, IF_GT, quotation tokens, field-access), matching folding-Lisp's problem domain. The v2 probe runs five pre-registered experiments (§v2.1–§v2.5); total compute ~1.5 hrs on M1.

Durable findings so far: [docs/chem-tape/findings.md](docs/chem-tape/findings.md) — `op-slot-indirection` (ACTIVE), `constant-slot-indirection`, `proxy-basin-attractor`.

Active lab notebook: [docs/chem-tape/experiments-v2.md](docs/chem-tape/experiments-v2.md).

## Research Tracks

| Track | Status | Architecture | Experiments |
|---|---|---|---|
| **Chem-tape** | Active (v2 wrapping) | [architecture-v2.md](docs/chem-tape/architecture-v2.md) | [experiments-v2.md](docs/chem-tape/experiments-v2.md) |
| Folding | Complete | [architecture.md](docs/folding/architecture.md) | [findings.md](docs/folding/findings.md) |
| **CA** | **Reviving (developmental probe)** | [architecture.md](docs/ca/architecture.md) | [experiments.md](docs/ca/experiments.md) |

## Next Direction

**CA developmental revival** — the CA track already has two ceiling-breakers on 8-bit parity (banded_3 at 0.969 max, phased_2 at 0.961 max; §11.a, §11.b). Zero existing sweeps test whether those dynamics actually *develop* — canalize, self-repair, redeploy under perturbed I/O. The plan: visuals first (atlas of evolved trajectories across all 256 inputs), damage assay second (Hamming-scar curves on mid-development perturbation), I/O-shift probe third. Rule surgery, fate maps, failure galleries, and attractor portraits follow. Dashboard grows organically around whichever visual you keep rewatching. Full plan: [Plans/ca-developmental-revival.md](Plans/ca-developmental-revival.md).

**Runtime plasticity (deferred).** Rank-1 operator-threshold plasticity tested at §v2.5-plasticity-1a returned a NULL on Arm A's narrow plateau (`plasticity-narrow-plateau` finding). Higher-rank plasticity and the meta-learning framing remain on the roadmap but are deprioritized while the CA probe runs. Design note preserved: [docs/chem-tape/runtime-plasticity-direction.md](docs/chem-tape/runtime-plasticity-direction.md).

## Performance Notes

- **Rust backend:** `_folding_rust` provides `rust_develop_batch` (Rayon parallel) and `rust_chem_execute_batch` for full VM scoring. The Python `develop()` auto-detects and uses Rust.
- **Batch evaluation:** use `develop_batch(genotypes)` for population loops — 2–3× faster than per-individual calls. The `dynamics.py` engine already does this; prefer reusing it over custom eval loops.

## Running Overnight Experiments

```bash
# validate queue, then launch
uv run python scripts/run_queue.py --validate
caffeinate -s uv run python scripts/run_queue.py

# morning: summarize
uv run python scripts/summarize_runs.py
```

Pre-bed smoke test with short-budget variants:
```bash
uv run python scripts/run_queue.py \
  --queue smoke.yaml \
  --status /tmp/smoke.status.json \
  --lock /tmp/smoke.lock \
  --output-root /tmp/smoke_out
```

Experiments must write outputs under `$RUN_DIR` (exported to child env) for `expect_outputs` checks to pass. Full design: [Plans/overnight-queue-runner.md](Plans/overnight-queue-runner.md).

## Research Workflow (`/research-rigor`)

The `research-rigor` skill enforces [docs/methodology.md](docs/methodology.md) at the three checkpoints where overreach silently accumulates.

```
(1) prereg  →  [run sweep]  →  (2) log-result  →  [replicate/inspect]  →  (3) promote-finding
                                      │
                                      ↓
                               scope-check (inline)
                               supersession (when a later experiment narrows)
```

| mode | when | produces |
|---|---|---|
| **prereg** | before running | `Plans/prereg_<slug>.md` with outcome table, decision rule, degenerate-success guards |
| **log-result** | after running | section in `docs/<track>/experiments.md` matching a pre-registered outcome row |
| **promote-finding** | after replication + mechanism inspection | scope-tagged entry in `docs/<track>/findings.md` |
| **scope-check** | any draft text | overreach phrases → scope-qualified rewrites |
| **supersession** | when a later experiment narrows an earlier one | retraction block; original reasoning preserved |

Templates: [docs/_templates/](docs/_templates/).

## Key References

- Altenberg, L. (1995/2023). "Genome Growth and the Evolution of the Genotype-Phenotype Map." — Constructional selection; why developmental encodings create different fitness landscapes
- Hinton, G.E. & Nowlan, S.J. (1987). "How Learning Can Guide Evolution." — Baldwin effect; needle-in-haystack proof that within-lifetime adaptation creates selection gradients on flat landscapes
- Kauffman, S.A. (1989). "Adaptation on rugged fitness landscapes." — NK model; epistasis and evolvability
- Hillis, W.D. (1990). "Co-evolving parasites improve simulated evolution as an optimization procedure."
- Bonner, J.T. (1974). *On Development.* — Low-pleiotropy principle
