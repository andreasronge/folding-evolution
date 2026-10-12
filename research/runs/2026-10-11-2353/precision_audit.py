"""Reconstruct conditional sizing evidence from existing 2150 rows, no searches."""
import hashlib
import json
from pathlib import Path
import numpy as np

SOURCE = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-2150-confirm/score.jsonl')
rows = [json.loads(line) for line in SOURCE.read_text().splitlines()]
rows = [r for r in rows if r['arm'] == 'R-all']
cells = sorted({r['cell'] for r in rows})
by = {(r['build'], r['cell'], r['repeat']): r['evaluations'] for r in rows}
x = np.asarray([[[by[b,c,r] for r in range(4)] for c in cells] for b in range(24)], dtype=float)
rng = np.random.default_rng(202610112353)
bi, ci = rng.integers(24, size=(8192,24)), rng.integers(18, size=(8192,18))
def audit(a,b):
    ratio = a.mean(2)[bi[:,:,None],ci[:,None,:]].mean((1,2)) / b.mean(2)[bi[:,:,None],ci[:,None,:]].mean((1,2))
    lo,hi = np.quantile(np.log(ratio), [.025,.975])
    return dict(point=float(a.mean()/b.mean()), interval95=np.exp([lo,hi]).tolist(), log_half_width=float((hi-lo)/2))
report = dict(source=str(SOURCE), source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              seed=202610112353, draws=8192, shape=list(x.shape),
              shifted_builds={str(k): audit(x, np.roll(x,k,axis=0)) for k in (1,12)},
              split_repeats=audit(x[:,:,:2],x[:,:,2:]),
              scope='Reconstructed pseudo-contrasts, not the unavailable original planning snippet; no R-bind data. Shifted builds are distinct historical acquisitions but crossed dependence remains. Repeats cannot eliminate R-bind-specific persistent build heterogeneity.',
              forecast='Proposal log half-width .08-.09 on 24 cells with 6 repeats is conditional; these 18-cell/4-repeat checks do not guarantee it.')
Path(__file__).with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
