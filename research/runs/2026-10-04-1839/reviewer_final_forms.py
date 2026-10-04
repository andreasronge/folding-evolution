#!/usr/bin/env python3
"""Reviewer: majority final form in the historical off / selected-mate runs of the same cells."""
import multiprocessing as mp
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, '/Users/andreas/developer/folding-evolution-research/2026-10-04-1839/experiments/chem_tape')
import s31_report as r31  # noqa: E402

OUT = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-03')


def pick(d):
    cfg = yaml.safe_load((d / 'config.yaml').read_text())
    if cfg.get('tape_length') != 64 or not cfg.get('seed_tapes') or cfg.get('seed_counts'):
        return None
    if cfg['crossover_rate'] not in (0.0, 0.3, 0.7) or len(cfg['seed_tapes'].split(',')) not in (10, 32):
        return None
    return str(d)


if __name__ == '__main__':
    dirs = [d for n in ('mapbias_s30_est_dup', 'mapbias_s30_est_partly', 'mapbias_s31_dose')
            for d in (OUT / n).iterdir() if d.is_dir() and (d / 'result.json').exists()]
    with mp.get_context('spawn').Pool(10) as p:
        paths = [x for x in p.map(pick, dirs) if x]
        runs = p.map(r31.classify_run, paths)
    c = Counter()
    for r in runs:
        if r['arm'] != 'D':
            continue
        comp, L, xo, start = r['cell']
        f = r['forms']
        top = max(f, key=f.get) if f else None
        c[(comp, start, xo, r31.outcome(r), top)] += 1
    for k in sorted(c, key=str):
        print(k, c[k])
