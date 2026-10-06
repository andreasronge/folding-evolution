"""Approved 1425 saved-map conditional replication; all outputs under RUN_DIR."""

import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path
import signal
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import search
from experiments.chem_tape.map_learning import log_cost
from experiments.chem_tape.saved_shape_maps import emitted, load_saved
from experiments.chem_tape.saved_shape_report import report

BASE = 1419000000
CAP = 524288


def plots(out, result, rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for rep, marker in [('a', 'o'), ('b', 's')]:
        pairs = [(p, r) for p, r in result['per_pair'].items()
                 if p.endswith(rep) and r['R/M+'] is not None]
        for p, r in pairs:
            axes[0].scatter(r['IF_GT_difference_R_minus_Mplus'], r['R/M+']['ratios']['shift'],
                            marker=marker, color='C0' if rep == 'b' else 'C1')
            axes[0].annotate(p, (r['IF_GT_difference_R_minus_Mplus'], r['R/M+']['ratios']['shift']))
    axes[0].set(xlabel='R−M+ exact IF_GT frequency', ylabel='R/M+ BE/LIN shift')
    # Existing harness curves include max case matches and correctness diversity.
    for ax, column, ylabel in [(axes[1], 1, 'Mean best training matches (of 64)'),
                               (axes[2], 2, 'Mean distinct correctness patterns')]:
        for family in ['G', 'M+', 'R', 'R_abl', 'R_fm']:
            buckets = {}
            for r in rows:
                if r['family'] != family:
                    continue
                for point in r['curve']:
                    buckets.setdefault(point[0], []).append(point[column])
            if buckets:
                xs = sorted(buckets)
                ax.plot(xs, [np.mean(buckets[x]) for x in xs], label=family)
        ax.set(xlabel='Evaluations (surviving searches)', ylabel=ylabel, xscale='log')
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / 'diagnostics.png', dpi=140)
    plt.close(fig)


def summary(out, result):
    lines = ['# Saved-map shape shift', '', json.dumps(result['outcome']), '',
             result['downstream'], '', result['scope'], '',
             'Intervals require six starts; pooled averages a/b within start.', '',
             '| Layer | Contrast | BE ratio [95% CI] | LIN ratio [95% CI] | Shift [95% CI] |',
             '|---|---|---|---|---|']
    for name, layer in result['layers'].items():
        for label, metrics in layer['contrasts'].items():
            cells = []
            for metric in ('BE', 'LIN', 'shift'):
                r = metrics[metric]
                cells.append(f"{r['ratio']:.3f} [{r['interval_95'][0]:.3f}, {r['interval_95'][1]:.3f}]"
                             if r['state'] == 'complete' else 'unresolved (missing starts/control)')
            lines.append('| ' + ' | '.join([name, label] + cells) + ' |')
        lines.extend(['', f"{name} dependency: {json.dumps(layer['dependency'])}", ''])
    lines.extend(['Per-cell costs/solves, per-pair contrasts, IF_GT covariates and M/G references: result.json.',
                  'Search curves are descriptive among searches still running at each evaluation count.'])
    (out / 'summary.md').write_text('\n'.join(lines) + '\n')


def run(args):
    os.environ['RAYON_NUM_THREADS'] = '1'
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'config.json').exists():
        raise ValueError('RUN_DIR already used; choose a fresh directory')
    started = time.monotonic()
    deadline = started + args.deadline_seconds - 60
    inputs = inputs_for('D1331')
    # A hash failure aborts before any searches; gate.json remains reviewable.
    try:
        maps, cells, fits, prior, provenance = load_saved(inputs)
    except ValueError as error:
        write_json(out, 'gate.json', dict(passed=False, reason=str(error)))
        raise
    seeds = list(range(BASE + (10000000 if args.smoke else 0),
                       BASE + (10000000 if args.smoke else 0) + (4 if args.smoke else 200)))
    order = [['G']]
    for rep in ('b', 'a'):
        for k in range(1, 7):
            order.append([f'{a}{k}{rep}' for a in ('M+', 'R', 'R_abl', 'R_fm')
                          if f'{a}{k}{rep}' in maps])
    order.extend([[f'M{k}'] for k in range(1, 7)])
    write_json(out, 'maps.json', maps)
    write_json(out, 'fits.json', fits)
    write_json(out, 'cells.json', cells)
    write_json(out, 'config.json', dict(task='2026-10-06-1425', arguments=vars(args),
        sources=provenance, seeds=seeds, seed_convention='same seed range across frozen cells and all maps, as 0811; smoke offset +10000000',
        domain='D1331', executor='v2_rmin', population=256, length=32, allele_range=23000,
        crossover=0.7, allele_mutation=0.03, selection='lexicase', cases=64, cap=CAP,
        unsolved_cost=float(np.log2(2*CAP)), order=order, prior_G_cell_costs=prior,
        intervals='95% t, df=5; six start clusters; pooled a/b mean within start',
        fitting='3000 proportional steps, rate 0.5, +/-ln16, continuous support floor then production normalize; TV<0.005'))
    rows, gate_passed, state, pool = [], False, 'running', None

    def save(row):
        name = row['arm']
        if row['table_hash'] != maps[name]['table_hash']:
            raise ValueError('evaluation map hash mismatch')
        # Retain acceptance check in evaluator, independent of fit construction.
        if name.startswith('R_fm'):
            pair = name[4:]
            tv = float(np.abs(emitted(maps[name]['table']) - emitted(maps['R'+pair]['table'])).sum()/2)
            if tv >= 0.005:
                raise ValueError(f'evaluator frequency match failed: {name}')
        family = next((a for a in ('R_fm', 'R_abl', 'M+', 'R') if name.startswith(a)), name)
        row.update(family=family, log2_cost=log_cost(row, CAP))
        rows.append(row)
        with (out / 'search.jsonl').open('a') as f:
            f.write(json.dumps(row, allow_nan=False) + '\n')

    def stop(signum, frame):
        raise TimeoutError(f'signal {signum}; partial observations retained')

    old_handlers = {s: signal.signal(s, stop) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        pool = mp.get_context('spawn').Pool(args.workers)
        for batch in order:
            jobs = [(c, name, maps[name]['table'], seed, CAP, 256, inputs)
                    for name in batch for c in cells for seed in seeds]
            if not run_jobs(pool, search, jobs, deadline, save):
                raise TimeoutError('internal search deadline; partial observations retained')
            if batch == ['G']:
                new = float(np.mean([r['log2_cost'] for r in rows]))
                old = float(np.mean(list(prior.values())))
                gate_passed = abs(new - old) <= 0.6
                write_json(out, 'gate.json', dict(passed=gate_passed, prior_mean=old,
                    current_mean=new, difference=new-old, threshold=0.6, smoke=args.smoke))
                if not gate_passed:
                    state = 'gate_failed'
                    break
            write_json(out, 'status.json', dict(state=state, finished_batch=batch,
                searches=len(rows), elapsed_seconds=time.monotonic()-started))
        else:
            state = 'complete'
    except TimeoutError as error:
        state = 'incomplete'
        write_json(out, 'stop.json', dict(reason=str(error)))
    finally:
        if pool is not None:
            pool.terminate()
            pool.join()
        for s, old in old_handlers.items():
            signal.signal(s, old)
        result = report(rows, maps, cells, seeds, prior, gate_passed, args.smoke)
        result.update(state=state, gate_passed=gate_passed, smoke=args.smoke,
            elapsed_seconds=time.monotonic()-started, searches=len(rows),
            worker_seconds=sum(r['seconds'] for r in rows))
        write_json(out, 'result.json', result)
        summary(out, result)
        plots(out, result, rows)
        write_json(out, 'status.json', dict(state=state, searches=len(rows),
            complete_b_starts=result['complete_b_starts'], elapsed_seconds=time.monotonic()-started))
    return 0 if state == 'complete' else 2


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--deadline-seconds', type=int, default=8700)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 60:
        parser.error('positive workers and deadline >60 required')
    raise SystemExit(run(args))


if __name__ == '__main__':
    main()
