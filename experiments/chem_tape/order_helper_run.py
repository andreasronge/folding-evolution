"""1628 helper-arrangement mechanism test on frozen development cells only."""

import argparse
import hashlib
import itertools
import json
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import subprocess
import time

import numpy as np

from experiments.chem_tape import inherited_library_run as archive
from experiments.chem_tape import order_cap_run as saved, order_run as base
from experiments.chem_tape import order_protected_run as previous
from experiments.chem_tape import order_helper_arrangement as construction
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json

TASK = construction.TASK
ARMS = ('R-tree', 'R-all', 'R-hx')
CAP = 8 * 65536
DRAWS = 8192
SOURCE_PREPARATION_HASH = '9a6d3380abb09f02efdd25096bf80111e7f40bdb93ee5a7201396576d3701f13'
DEFAULT_SAVED = '/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1530-prepare'
ARTIFACTS = ('bank', 'libraries', 'method_freeze', 'schedules', 'seed_audit', 'construction_audit', 'coverage')


def schedules(bank, smoke=False):
    return [dict(build=b, cell=c, repeat=r, arm=a, realization=r % 4,
                 seeds=[construction.seed('smoke-search' if smoke else 'search', b, c, r, k)
                        for k in range(8)])
            for r in range(4 if smoke else 8) for b in range(1 if smoke else 24)
            for c in bank['split']['development'] for a in ARMS]


def load_source(path):
    """Hash-check 1530's snapshot, then reconstruct its original 1228 libraries."""
    if (path / 'failure.json').exists():
        raise ValueError('saved 1530 preparation failed')
    p = json.loads((path / 'preparation.json').read_text())
    if (p.get('preparation_hash') != SOURCE_PREPARATION_HASH or not p.get('admitted')
            or digest({k: v for k, v in p.items() if k != 'preparation_hash'}) != SOURCE_PREPARATION_HASH):
        raise ValueError('saved 1530 identity mismatch')
    values = {k: json.loads((path / (k + '.json')).read_text()) for k in p['artifact_hashes']}
    for k, v in values.items():
        if digest(v) != p['artifact_hashes'][k]:
            raise ValueError('saved 1530 artifact mismatch: ' + k)
    bank, libs, artifacts = archive.load_saved(path / 'saved')
    if values['bank'] != bank or values['libraries'] != libs:
        raise ValueError('1530 libraries differ from reconstructed 1228 source')
    # Preserve the original method, checking all search/extraction dependencies
    # against the 1228 source freeze and the approved later extensions.
    previous.freeze(bank, artifacts)
    return bank, libs, artifacts, values


def seed_audit(bank, artifacts, source, libraries):
    old = previous.seed_audit(bank, artifacts)
    historical = set()
    def collect(obj, key=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                collect(v, k if 'seed' in k else key)
        elif isinstance(obj, list):
            for v in obj:
                collect(v, key)
        elif isinstance(obj, int) and 'seed' in key:
            historical.add(obj)
    collect(old)
    collect(source['seed_audit'])
    collect(source['schedules'])
    # Earlier audit recursively validates raw historical artifacts. Its
    # published 1427/1228/1129 sets are also included via archive/base audits.
    for audit in (archive.audit_seeds(bank, artifacts), saved.seed_audit(bank), base.seed_audit(bank)):
        collect(audit)
    import gzip
    for artifact in base.seed_audit(bank)['historical_artifacts']:
        path = Path(artifact['path'])
        raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        collect(json.loads(raw))
    historical.update(range(7000, 7800))
    historical.update(range(9000, 9006))
    helper_hashes = {hashlib.sha256(v).hexdigest()
                     for v in construction.Semantics(bank['inputs']).helper_vectors.values()}
    groups = {'construction': [construction.seed('construction', lib['build'], r, slot)
                              for lib in libraries for r in range(4)
                              for slot, e in enumerate(lib['entries'])
                              if e['semantic_hash'] in helper_hashes],
              'bootstrap': [construction.seed('bootstrap')]}
    for smoke in (False, True):
        uses = {}
        for m in schedules(bank, smoke):
            for k, s in enumerate(m['seeds']):
                uses.setdefault(s, []).append((m, k))
        for records in uses.values():
            if (len(records) != 3 or {m['arm'] for m, _ in records} != set(ARMS)
                    or len({(m['build'], m['cell'], m['repeat'], k) for m, k in records}) != 1):
                raise ValueError('unintended search seed reuse')
        groups['smoke-search' if smoke else 'search'] = list(uses)
    seen = set(historical)
    for name, values in groups.items():
        if len(set(values)) != len(values) or set(values) & seen:
            raise ValueError('historical/namespace seed collision: ' + name)
        seen.update(values)
    return dict(admitted=True, historical_count=len(historical), historical_hash=digest(sorted(historical)),
                published_seed_sets={k: sorted(v) for k, v in groups.items()},
                pairing='search attempts paired only across arms; independent construction and bootstrap')


def coverage(bank, libs):
    by = {c['id']: c for c in bank['screen']['cells']}
    return [dict(build=b, cell=c, needed_helpers_present=len(
        {h for h, d in lib['all_helper_diagnostics'].items() if d['semantic']['included']}
        & set(by[c]['helpers']))) for b, lib in enumerate(libs) for c in bank['split']['development']]


def freeze(bank, artifacts):
    prior = previous.freeze(bank, artifacts)
    return dict(task=TASK, methods=prior['methods'], bank_hash=digest(bank),
                source_preparation_hash=SOURCE_PREPARATION_HASH,
                cutoff=65536, attempts=8, population=256, crossover=0.5,
                donor_probability=0.5, donor_draw='uniform slots, duplicates retained',
                builds=24, repeats=8, arms=list(ARMS), development_cells=bank['split']['development'],
                construction=dict(realizations=4, max_draws=construction.MAX_DRAWS,
                                  pools='per-entry arity/token-width', accept='no D625 helper-valued subtree',
                                  assignment='repeat mod 4', first_accepted=True),
                bootstrap=dict(seed=construction.seed('bootstrap'), draws=DRAWS, unit='whole paired builds'),
                decision=['lower Q > 1.25: material loss',
                          'upper Q < 1.25 and upper R-hx/R-tree < 0.80: useful retention',
                          'otherwise unresolved'], incomplete='no partial efficacy verdict',
                scope='development-bank mechanism comparison; conditional on replacement law')


def make_values(bank, originals, artifacts, source):
    libs, audit = construction.build(originals, bank['inputs'])
    if len(libs) != 24 or sum(audit['helpers_per_build']) != 177:
        raise ValueError('approved static audit helper/build count differs')
    return dict(bank=bank, libraries=libs, method_freeze=freeze(bank, artifacts),
                schedules=dict(score=schedules(bank), smoke=schedules(bank, True)),
                seed_audit=seed_audit(bank, artifacts, source, libs), construction_audit=audit,
                coverage=coverage(bank, originals))


def envelopes(metas, values, smoke=False):
    bank, libs = values['bank'], values['libraries']
    expected = {key(m): m for m in schedules(bank, smoke)}
    by = {c['id']: c for c in bank['screen']['cells']}
    jobs = []
    for m in metas:
        if expected.get(key(m)) != m:
            raise ValueError('unapproved cell/arm/build/realization/seed')
        lib = libs[m['build']]
        entries = (lib['entries'] if m['arm'] == 'R-all'
                   else lib['constructions'][m['realization']]['entries'])
        donors = None if m['arm'] == 'R-tree' else [e['prefix'] for e in entries]
        c = by[m['cell']]
        jobs.append((m, dict(id=c['id'], labels=c['labels']), bank['inputs'], 65536, donors))
    return jobs


def key(m):
    return m['build'], m['cell'], m['repeat'], m['arm']


def validate_partial(rows, bank, smoke=False):
    by = {key(m): m for m in schedules(bank, smoke)}
    keys = [key(r) for r in rows]
    if len(set(keys)) != len(keys) or not set(keys) <= set(by):
        raise ValueError('duplicate/unknown score rows')
    checked = previous.validate_rows(rows, [by[k] for k in keys], bank)
    pairs = {}
    for r in checked:
        for attempt in r['attempts']:
            if (attempt['cap'] != 65536 or attempt['pop_size'] != 256
                    or attempt['crossover'] != 0.5 or attempt['evaluations'] % 256
                    or (not attempt['solved'] and attempt['evaluations'] != 65536)):
                raise ValueError('attempt search parameters/accounting differ')
        pairs.setdefault(key(r)[:3], []).append(r)
    for group in pairs.values():
        for r, r2 in itertools.combinations(group, 2):
            n = min(len(r['attempts']), len(r2['attempts']))
            if any(r['attempts'][i]['initial_tokens_hash'] != r2['attempts'][i]['initial_tokens_hash']
                   or r['attempts'][i]['training_indices'] != r2['attempts'][i]['training_indices']
                   for i in range(n)):
                raise ValueError('search initialization/training pairing differs')
    return checked


def batch(out, name, values, workers, deadline, smoke=False):
    metas = values['schedules']['smoke' if smoke else 'score']
    jobs = envelopes(metas, values, smoke)
    rows, started = [], time.monotonic()
    with (out / name).open('w') as file:
        def save(row):
            file.write(json.dumps(row, allow_nan=False) + '\n')
            file.flush()
            os.fsync(file.fileno())
            rows.append(row)
            if len(rows) % 60 == 0:
                print(name, len(rows), '/', len(jobs), 'wall', round(time.monotonic()-started, 1), flush=True)
        pool = mp.get_context('spawn').Pool(workers)
        try:
            complete = run_jobs(pool, base.execute, jobs, deadline, save)
            pool.close()
        finally:
            pool.terminate()
            pool.join()
    rows = validate_partial(rows, values['bank'], smoke)
    write_json(out, name.replace('.jsonl', '_completion.json'), dict(
        complete=complete, completed_jobs=len(rows), expected_jobs=len(metas), rows_hash=digest(rows)))
    return rows, time.monotonic() - started


def classify(q_interval, tree_interval):
    if q_interval[0] > 1.25:
        return 'material_loss_return_to_strategy'
    if q_interval[1] < 1.25 and tree_interval[1] < 0.80:
        return 'useful_retention_return_to_strategy'
    return 'unresolved_return_to_strategy_price_resolution'


def summarize(rows, values, smoke=False):
    bank = values['bank']
    rows = validate_partial(rows, bank, smoke)
    if len(rows) != len(schedules(bank, smoke)):
        return dict(admitted=False, complete=False, decision='incomplete_no_efficacy_verdict',
                    completed_jobs=len(rows), expected_jobs=len(schedules(bank, smoke)))
    cells = bank['split']['development']
    builds, repeats = (1, 4) if smoke else (24, 8)
    by = {key(r): r for r in rows}
    arrays = {a: np.array([[[by[b, c, r, a]['evaluations'] for r in range(repeats)]
                            for c in cells] for b in range(builds)], dtype=float) for a in ARMS}
    blocks = {a: v.mean(axis=(1, 2)) for a, v in arrays.items()}
    selected = np.random.default_rng(construction.seed('bootstrap')).integers(builds, size=(DRAWS, builds))
    contrasts = {num + '/' + den: saved.estimate(blocks[num].mean()/blocks[den].mean(),
                 blocks[num][selected].mean(1)/blocks[den][selected].mean(1))
                 for num, den in [('R-hx', 'R-all'), ('R-hx', 'R-tree'), ('R-all', 'R-tree')]}
    strata = {}
    for n in range(3):
        units = {(x['build'], x['cell']) for x in values['coverage'] if x['needed_helpers_present'] == n}
        rr = [r for r in rows if (r['build'], r['cell']) in units]
        means = {a: float(np.mean([r['evaluations'] for r in rr if r['arm'] == a])) if rr else None for a in ARMS}
        strata[str(n)] = dict(paired_units=len(rr)//3, means=means,
                             Q=None if not rr else means['R-hx']/means['R-all'])
    semantics = construction.Semantics(bank['inputs'])
    census = [dict(build=r['build'], cell=r['cell'], repeat=r['repeat'], realization=r['realization'],
                   helpers=semantics.census(r['attempts'][-1]['solver_tree']))
              for r in rows if r['arm'] == 'R-hx' and r['solved']]
    arms = {a: dict(jobs=sum(r['arm'] == a for r in rows),
                   solves=sum(r['solved'] for r in rows if r['arm'] == a),
                   capped_mean=float(arrays[a].mean()),
                   mean_worker_seconds=float(np.mean([r['worker_seconds'] for r in rows if r['arm'] == a]))) for a in ARMS}
    return dict(admitted=True, complete=True, completed_jobs=len(rows), arms=arms, contrasts=contrasts,
                primary='Q = ratio of pooled capped arithmetic mean evaluations R-hx/R-all',
                decision='smoke_only_no_decision' if smoke else classify(
                    contrasts['R-hx/R-all']['interval95'], contrasts['R-hx/R-tree']['interval95']),
                bootstrap=values['method_freeze']['bootstrap'], coverage_strata_descriptive=strata,
                rediscovery=dict(solvers=len(census), solvers_with_helper=sum(bool(r['helpers']) for r in census),
                                 fraction=None if not census else sum(bool(r['helpers']) for r in census)/len(census),
                                 census=census),
                interpretation='Loss: intact entries beat this mostly projection-valued replacement law, conditional on remaining library and search. Retention: preassembled helper-valued donors unnecessary at registered resolution; helpers may be reconstructed. No unique min/max necessity or fresh-bank claim.')


def plot(out, rows, values, filename):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 5, figsize=(21, 4))
    xs = [256, 4096, 16384, 65536, 131072, 262144, CAP]
    for a in ARMS:
        rr = [r for r in rows if r['arm'] == a]
        axes[0].plot(xs, [np.mean([r['solved'] and r['evaluations'] <= x for r in rr]) for x in xs], label=a)
        for panel, field in [(1, 'curve'), (2, 'phenotype_diversity_curve')]:
            paths = []
            for r in rr:
                path, offset = [], 0
                for attempt in r['attempts']:
                    path.extend((offset+p[0], p[1]) for p in attempt[field])
                    offset += attempt['evaluations']
                paths.append(path)
            axes[panel].plot(xs, [np.mean([([v for t, v in line if t <= x] or [line[0][1]])[-1]
                                          for line in paths]) for x in xs], label=a)
        attempts = [t for r in rr for t in r['attempts']]
        total = sum(r['evaluations'] for r in rr)
        axes[3].bar(a, sum(t['tree_nodes_evaluated'] for t in attempts)/total)
        hist = np.sum([t['compiled_length_histogram'] for t in attempts], axis=0)
        axes[4].plot(hist/total, label=a)
    for i, title in enumerate(('D625 solve CDF', 'Training best; restart resets', 'Training output diversity')):
        axes[i].set(xscale='log', xlabel='Evaluations', title=title)
        axes[i].legend(fontsize=7)
    axes[3].set(ylabel='Mean evaluated tree nodes')
    axes[3].tick_params(axis='x', rotation=25)
    axes[4].set(xlabel='Compiled length', ylabel='Evaluated fraction')
    axes[4].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / filename, dpi=140)
    plt.close(fig)


def prepare(args, out, deadline):
    started = time.monotonic()
    shutil.copytree(args.saved, out / 'source', ignore=shutil.ignore_patterns('metadata.json', '*log', '*.png'))
    bank, originals, artifacts, source = load_source(out / 'source')
    values = make_values(bank, originals, artifacts, source)
    for name, value in values.items():
        write_json(out, name + '.json', value)
    static_seconds = time.monotonic() - started
    rows, elapsed = batch(out, 'smoke.jsonl', values, args.workers, deadline-30, True)
    report = summarize(rows, values, True)
    if not report['complete']:
        raise TimeoutError('development smoke incomplete')
    # Descriptive runtime projection only, not an efficacy gate or sample-size adaptation.
    worker = sum(r['worker_seconds'] for r in rows)
    effective = min(args.workers, worker/elapsed)
    projected = 1152 * sum(v['mean_worker_seconds'] for v in report['arms'].values()) / effective
    report.update(batch_seconds=elapsed, static_seconds=static_seconds, effective_workers=effective,
                  projected_full_score_seconds=projected)
    write_json(out, 'smoke_report.json', report)
    plot(out, rows, values, 'smoke_dynamics.png')
    if projected > 3300:
        raise ValueError(f'smoke projects {projected:.1f}s scoring, beyond approved 3600s timeout with validation reserve')
    p = dict(admitted=True, task=TASK, artifact_hashes={k: digest(v) for k, v in values.items()},
             source_preparation_hash=SOURCE_PREPARATION_HASH, smoke_rows_hash=digest(rows),
             protected_searches=0, workers=args.workers, seconds=time.monotonic()-started,
             git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip())
    if time.monotonic() > deadline:
        raise TimeoutError('preparation deadline exceeded')
    p['preparation_hash'] = digest(p)
    write_json(out, 'preparation.json', p)
    print('prepared', 'seconds', p['seconds'], 'projected score seconds', projected, flush=True)


def load_prepared(path):
    started = time.monotonic()
    if (path / 'failure.json').exists():
        raise ValueError('preparation failed')
    bank, originals, artifacts, source = load_source(path / 'source')
    expected = make_values(bank, originals, artifacts, source)
    p = json.loads((path / 'preparation.json').read_text())
    if (not p['admitted'] or p['task'] != TASK or p['source_preparation_hash'] != SOURCE_PREPARATION_HASH
            or p['preparation_hash'] != digest({k: v for k, v in p.items() if k != 'preparation_hash'})):
        raise ValueError('preparation identity mismatch')
    for name, value in expected.items():
        actual = json.loads((path / (name + '.json')).read_text())
        if actual != value or p['artifact_hashes'][name] != digest(actual):
            raise ValueError('frozen artifact changed: ' + name)
    rows = [json.loads(line) for line in (path / 'smoke.jsonl').read_text().splitlines()]
    checked = validate_partial(rows, bank, True)
    if len(rows) != len(schedules(bank, True)) or p['smoke_rows_hash'] != digest(checked):
        raise ValueError('smoke rows changed/incomplete')
    return expected, p, time.monotonic()-started


def score(args, out, deadline):
    values, p, replay_seconds = load_prepared(Path(args.prepared))
    for name, value in values.items():
        write_json(out, name + '.json', value)
    rows, elapsed = batch(out, 'score.jsonl', values, args.workers, deadline-60, args.smoke)
    report = summarize(rows, values, args.smoke)
    report.update(smoke=args.smoke, workers=args.workers, protected_searches=0,
                  batch_seconds=elapsed, replay_seconds=replay_seconds,
                  preparation_hash=p['preparation_hash'], score_rows_hash=digest(rows))
    write_json(out, 'report.json', report)
    if report['complete']:
        plot(out, rows, values, 'dynamics.png')
    print('scored', len(rows), 'wall', elapsed, 'decision', report['decision'], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'score'))
    parser.add_argument('--saved', default=DEFAULT_SAVED)
    parser.add_argument('--prepared')
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--seconds', type=int)
    parser.add_argument('--smoke', action='store_true', help='score only the independent development smoke grid')
    args = parser.parse_args()
    limit = 570 if args.phase == 'prepare' else 3570
    seconds = limit if args.seconds is None else args.seconds
    if (args.workers < 1 or not 60 < seconds <= limit or
            (args.phase == 'score' and not args.prepared) or (args.phase == 'prepare' and args.smoke)):
        parser.error('positive workers, approved deadline, --prepared for score; --smoke is score-only')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if any((out / n).exists() for n in ('failure.json', 'preparation.json', 'report.json', 'score.jsonl', 'source', 'method_freeze.json')):
        parser.error('RUN_DIR contains previous artifacts')
    deadline = time.monotonic() + seconds
    try:
        (prepare if args.phase == 'prepare' else score)(args, out, deadline)
    except Exception as error:
        write_json(out, 'failure.json', dict(admitted=False, phase=args.phase, error=str(error)))
        raise


if __name__ == '__main__':
    main()
