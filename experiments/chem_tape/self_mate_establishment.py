#!/usr/bin/env python3
"""Approved 2026-10-04-1839 contest: sweep construction, census and readouts.

Uses §31's exact final non-elite verdict unchanged. Reports sampled trajectories
separately: those include elites and condition shared share on full exactness.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import random
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

import numpy as np
import yaml

import s31_report as r31
import shared_helper as sh
from sweep import expand_grid
from folding_evolution.chem_tape import tagged

HERE = Path(__file__).resolve().parent
SWEEP = HERE / 'sweeps/mapbias/self_mate_establishment.yaml'
OFF_WINS = {('duplicated', '1/32'): 19, ('duplicated', '1/10'): 29,
            ('partly', '1/32'): 8, ('partly', '1/10'): 19}
SELECTED_WINS = {('duplicated', '1/32', 0.3): 10, ('duplicated', '1/10', 0.3): 24}


def make_spec() -> dict:
    """Copy historical records byte-for-byte; only replace rate and mate."""
    old = yaml.safe_load((HERE / 'sweeps/mapbias/s31_dose.yaml').read_text())
    cells = [p for p in old['paired'] if p['tape_length'] == 64 and p['crossover_rate'] == 0.3]
    assert len(cells) == 4
    return {'sweep_name': 'self_mate_establishment',
            'base': {**old['base'], 'crossover_mate': 'self'},
            'paired': [{**p, 'crossover_rate': rate} for p in cells for rate in (0.3, 0.7)],
            'grid': {'seed': list(range(30))}}


def parents(spec: dict) -> dict:
    known = {sh.form_genome(name, 64).tobytes().hex(): name for name in sh.FORMS}
    found = {}
    for cfg in expand_grid(spec):
        for tape in cfg.seed_tapes.split(','):
            if tape not in known:
                raise ValueError('Unexpected hand-built seed tape')
            found[known[tape]] = np.frombuffer(bytes.fromhex(tape), dtype=np.uint8).copy()
    if set(found) != set(sh.FORMS):
        raise ValueError('Census requires all three seed forms')
    return found


def census(spec: dict, n: int, seed: int) -> dict:
    rows = []
    for name, parent in sorted(parents(spec).items()):
        rng, exact, machine, cache = random.Random(seed), sh.Exactness(), sh.machine(), {}
        if sh.classify(parent, machine)['form'] != name:
            raise ValueError(f'Parent does not classify as {name}')
        counts, clones, semantic_clones = Counter(), 0, 0
        parent_key = sh.semantic_key(parent)
        for _ in range(n):
            child = tagged.crossover(parent, parent, rng, 'v2')
            clones += int(np.array_equal(child, parent))
            key = sh.semantic_key(child)
            semantic_clones += int(key == parent_key)
            if not exact(child).all():
                category = 'broken'
            else:
                if key not in cache:
                    cache[key] = sh.classify(child, machine)['form'] or 'exact_other'
                category = cache[key]
            counts[category] += 1
        rows.append({'parent': name, 'parent_hex': parent.tobytes().hex(), 'L': 64,
                     'seed': seed, 'events': n, 'children': n,
                     'counts': {k: counts[k] for k in (*r31.FORMS, 'broken', 'exact_other')},
                     'byte_clones': clones, 'semantic_clones': semantic_clones})
    return {'operator': 'tagged.crossover(parent, parent, random.Random(seed), variant="v2")',
            'mutation_rate': 0, 'rows': rows}


def validate_run(root: Path, cfg) -> str:
    d = root / cfg.hash()
    for name in ('config.yaml', 'result.json', 'history.npz', 'final_population.npz'):
        if not (d / name).exists():
            raise ValueError(f'Missing {d / name}')
    saved = yaml.safe_load((d / 'config.yaml').read_text())
    if saved != asdict(cfg):
        raise ValueError(f'Config mismatch: {d}')
    res = json.loads((d / 'result.json').read_text())
    if res['config_hash'] != cfg.hash() or res['generations_run'] != cfg.generations:
        raise ValueError(f'Incomplete/mismatched result: {d}')
    stats = res['shared_stats']
    expected = list(range(0, cfg.generations + 1, cfg.log_every))
    if expected[-1] != cfg.generations:
        expected.append(cfg.generations)
    if [s['gen'] for s in stats] != expected:
        raise ValueError(f'Missing/duplicate census generations: {d}')
    for s in stats:
        n, nf = s['n'], s['n_fully_exact']
        if n != min(256, cfg.pop_size) or not 0 <= nf <= n:
            raise ValueError(f'Bad census denominator: {d}')
        shares = [s[k] for k in r31.FORMS]
        if nf == 0:
            if any(v is not None for v in shares):
                raise ValueError(f'Undefined share encoded as a number: {d}')
        elif any(v is None or not 0 <= v <= 1 for v in shares) or not np.isclose(sum(shares), 1):
            raise ValueError(f'Invalid form shares: {d}')
        if not np.isclose(s['fully_exact'], nf / n):
            raise ValueError(f'Exactness denominator mismatch: {d}')
    with np.load(d / 'final_population.npz') as f:
        if f['genotypes'].shape != (cfg.pop_size, 2 * cfg.tape_length):
            raise ValueError(f'Final population shape mismatch: {d}')
    with np.load(d / 'history.npz') as h:
        if h['generation'][-1] != cfg.generations:
            raise ValueError(f'Short history: {d}')
    return str(d)


def mean_defined(values) -> float | None:
    defined = [v for v in values if v is not None]
    return float(np.mean(defined)) if defined else None


def report(spec: dict, root: Path, out: Path, workers: int) -> None:
    configs = expand_grid(spec)
    hashes = [c.hash() for c in configs]
    if len(hashes) != len(set(hashes)):
        raise ValueError('Duplicate sweep configs')
    paths = [validate_run(root, c) for c in configs]
    actual = {p.name for p in root.iterdir() if p.is_dir() and (p / 'result.json').exists()}
    if actual != set(hashes):
        raise ValueError('Unexpected or missing run directories')
    if workers > 1:
        with mp.get_context('spawn').Pool(workers) as pool:
            runs = pool.map(r31.classify_run, paths)
    else:
        runs = list(map(r31.classify_run, paths))
    grouped = defaultdict(list)
    slim = []
    for r in runs:
        comp, L, rate, start = r['cell']
        key = (comp, start, rate)
        grouped[key].append(r)
        slim.append({'hash': Path(r['dir']).name, 'competitor': comp, 'L': L,
                     'start': start, 'rate': rate, 'seed': r['cfg']['seed'],
                     'outcome': r31.outcome(r), 'n_exact_nonelite': r['n_exact'],
                     'forms_nonelite': r['forms'], 'elite_forms': r['elites'],
                     'final_shared_share_nonelite': r['forms'].get('shared', 0) / r['n_exact']
                     if r['n_exact'] else None,
                     'early': [s for s in r['stats'] if s['gen'] in (5, 10, 20)],
                     'late': [s for s in r['stats'] if s['gen'] >= r['cfg']['generations'] - 50],
                     'trajectory': r['stats'], 'elapsed_sec': r['elapsed']})
    cells = []
    md = ['# Self-mate establishment readouts', '',
          f'Validated {len(runs)} / {len(configs)} expected runs.', '',
          'Final verdict: ≥20 fully exact non-elites; won if >90% of those are shared.',
          'Census shares condition on exactness and include sampled elites (n≤256).',
          'Null shares remain undefined. Historical counts are descriptive, not paired tests.', '',
          '| competitor | start | rate | N | won | gone | between | no solution | off wins/30 | selected wins/30 |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for key, rs in sorted(grouped.items()):
        comp, start, rate = key
        outcomes = Counter(r31.outcome(r) for r in rs)
        generations = [s['gen'] for s in rs[0]['stats']]
        trajectory = []
        for i, gen in enumerate(generations):
            shares = [r['stats'][i]['shared'] for r in rs]
            # Unconditional sampled shared frequency retains zero-exact samples as zero.
            freq = [0.0 if r['stats'][i]['n_fully_exact'] == 0 else
                    r['stats'][i]['shared'] * r['stats'][i]['n_fully_exact'] / r['stats'][i]['n'] for r in rs]
            trajectory.append({'gen': gen, 'mean_shared_among_exact': mean_defined(shares),
                               'n_defined': sum(v is not None for v in shares),
                               'mean_shared_population_frequency': float(np.mean(freq))})
        row = {'competitor': comp, 'start': start, 'rate': rate, 'n': len(rs),
               'outcomes': {k: outcomes[k] for k in ('won', 'gone', 'between', 'no_solution')},
               'historical_off_wins': OFF_WINS[(comp, start)],
               'historical_selected_wins': SELECTED_WINS.get(key, 0),
               'trajectory': trajectory}
        cells.append(row)
        md.append(f"| {comp} | {start} | {rate} | {len(rs)} | " +
                  ' | '.join(str(row['outcomes'][k]) for k in ('won', 'gone', 'between', 'no_solution')) +
                  f" | {row['historical_off_wins']} | {row['historical_selected_wins']} |")
    md += ['', 'Early readouts (means among runs with a defined exact-conditioned share):', '',
           '| competitor | start | rate | generation | defined N | shared among exact | shared population frequency |',
           '|---|---|---|---|---|---|---|']
    for c in cells:
        for s in c['trajectory']:
            if s['gen'] in (5, 10, 20):
                md.append(f"| {c['competitor']} | {c['start']} | {c['rate']} | {s['gen']} | "
                          f"{s['n_defined']} | {s['mean_shared_among_exact']} | {s['mean_shared_population_frequency']:.6f} |")
    md += ['', 'Per-seed early/late values, denominators, elite forms and all trajectories are in readouts.json.',
           'Inspect between outcomes and late trajectories before distinguishing slow establishment from failure.', '']
    out.mkdir(parents=True, exist_ok=True)
    (out / 'readouts.json').write_text(json.dumps({'cells': cells, 'runs': slim}, indent=2, allow_nan=False) + '\n')
    (out / 'readouts.md').write_text('\n'.join(md))
    plot(cells, out / 'trajectories.png')


def plot(cells, path: Path) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True, sharey=True)
    for row, comp in enumerate(('duplicated', 'partly')):
        for col, start in enumerate(('1/32', '1/10')):
            ax = axes[row, col]
            for c in cells:
                if (c['competitor'], c['start']) != (comp, start):
                    continue
                ax.plot([s['gen'] for s in c['trajectory']],
                        [s['mean_shared_population_frequency'] for s in c['trajectory']],
                        label=f"self, crossover {c['rate']}")
            ax.set(title=f'vs {comp}, start {start}', ylim=(0, 1))
            ax.grid(alpha=0.25)
            ax.legend(fontsize=8)
    for ax in axes[-1]:
        ax.set_xlabel('Generation')
    for ax in axes[:, 0]:
        ax.set_ylabel('Shared population frequency\n(sample mean, elites included)')
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    make = sub.add_parser('make-sweep')
    make.add_argument('--out', type=Path, default=SWEEP)
    make.add_argument('--smoke', action='store_true')
    ce = sub.add_parser('census')
    ce.add_argument('--sweep', type=Path, default=SWEEP)
    ce.add_argument('--out', type=Path, required=True)
    ce.add_argument('--events', type=int, default=10_000)
    ce.add_argument('--seed', type=int, default=0)
    re = sub.add_parser('report')
    re.add_argument('--sweep', type=Path, default=SWEEP)
    re.add_argument('--root', type=Path, required=True)
    re.add_argument('--out', type=Path, required=True)
    re.add_argument('--workers', type=int, default=10)
    args = ap.parse_args()
    if args.command == 'make-sweep':
        spec = make_spec()
        if args.smoke:
            spec['base'].update(pop_size=64, generations=20)
            spec['grid']['seed'] = [0]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text('# Approved task 2026-10-04-1839; copied from s31_dose.yaml.\n' +
                            yaml.safe_dump(spec, sort_keys=False, width=1_000_000))
        print(f'Wrote {len(expand_grid(spec))} configs to {args.out}')
    elif args.command == 'census':
        if args.events < 1:
            ap.error('--events must be positive')
        res = census(yaml.safe_load(args.sweep.read_text()), args.events, args.seed)
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / 'census.json').write_text(json.dumps(res, indent=2) + '\n')
        md = ['# One self-crossover census', '',
              'One child per event, no mutation; exact forms checked on all 10,000 inputs.',
              'Byte clones and semantic clones overlap form counts; semantic identity is a structural key.', '',
              '| parent | children | exact shared | exact partly | exact duplicated | broken | exact other | byte clones | semantic clones |',
              '|---|---|---|---|---|---|---|---|---|']
        for r in res['rows']:
            md.append(f"| {r['parent']} | {r['children']} | " +
                      ' | '.join(str(r['counts'][k]) for k in (*r31.FORMS, 'broken', 'exact_other')) +
                      f" | {r['byte_clones']} | {r['semantic_clones']} |")
        (args.out / 'census.md').write_text('\n'.join(md) + '\n')
    else:
        report(yaml.safe_load(args.sweep.read_text()), args.root, args.out, args.workers)


if __name__ == '__main__':
    main()
