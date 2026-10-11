"""Saved-row, explicitly synthetic clustered precision sensitivity; no GP search.

The 1427 initial (.125) / ordinary (0) pair supplies an empirical paired search
noise and library heterogeneity anchor. This is not a measured q0 or endpoint
law: both mean and endpoint variance are assumptions. No new efficacy pilot.
"""
import json
from pathlib import Path
import numpy as np
from experiments.chem_tape import recurrent_library_run as run

path = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1427-readout/score.jsonl')
raw = path.read_bytes()
rows = [json.loads(s) for s in raw.splitlines()]
cells = sorted({r['cell'] for r in rows})
by = {(r['build'], r['cell'], r['repeat'], r['arm']): r['evaluations'] for r in rows}
rng = np.random.default_rng(run.seed('precision'))
# Expand to 6 paired endpoint blocks per library with 12 jobs each. Empirical
# repeats are sampled together across numerator/reference within each cell.
arrays = {a: np.empty((24, 6)) for a in ('initial', 'R-tree')}
for b in range(24):
    for p in range(6):
        choices = {c: rng.integers(2, size=2) for c in cells}
        for a in arrays:
            arrays[a][b, p] = np.mean([by[b, c, int(r), a] for c in cells for r in choices[c]])
reference = arrays['R-tree']
anchor = arrays['initial']
outputs = []
for interaction_scale, cv in ((g, c) for g in (0.25, 0.5, 1.0) for c in (0, 0.25, 0.5, 1.0)):
    sigma = np.sqrt(np.log1p(cv**2))
    factor = np.exp(rng.normal(-sigma**2/2, sigma, (24, 6)))
    normalized_anchor = anchor*reference.mean()/anchor.mean()
    paired_anchor = (1-interaction_scale)*reference + interaction_scale*normalized_anchor
    candidate = paired_anchor*factor
    candidate *= 0.95*reference.mean()/candidate.mean()
    values = dict(candidate=candidate, reference=reference)
    row = dict(assumed_paired_response_noise_scale=interaction_scale, assumed_endpoint_multiplier_cv=cv, centered_ratio=0.95)
    for nested in (False, True):
        boot = run.paired_draws(values, np.random.default_rng(run.seed('bootstrap')), nested=nested)
        interval = np.quantile(boot['candidate']/boot['reference'], [0.025, 0.975]).tolist()
        row['nested' if nested else 'library_only'] = dict(interval95=interval,
            excludes_0_80=bool(interval[0] > 0.80), half_width=(interval[1]-interval[0])/2)
    outputs.append(row)
import hashlib
result = dict(saved_rows_sha256=hashlib.sha256(raw).hexdigest(), saved_jobs=len(rows),
    seed=run.seed('precision'), bootstrap_seed=run.seed('bootstrap'), draws=run.DRAWS,
    empirical_anchor='paired 1427 initial/ordinary rows (not measured new q0 or endpoint)',
    assumptions='24 empirical library clusters; paired cellwise repeat resampling to six populations; fixed 0.95 mean ratio; paired response deviations scaled by 0.25/0.5/1 of the saved fixed-dose anchor; independent lognormal endpoint multipliers with listed CVs; no extra library correlation beyond saved anchor',
    limitations='Only two saved repeats per cell; new endpoint heterogeneity and library correlation are unknown; Response noise at the much closer new low-dose laws is unmeasured; scaling is an assumption. This sensitivity is not a guarantee or an added efficacy gate.', scenarios=outputs)
print(json.dumps(result, indent=2))
