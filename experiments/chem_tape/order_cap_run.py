"""1228 uncapped semantic library experiment; frozen 1129 development roster."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import order_run as base, order_library
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.tree_gp_search import Tree
from experiments.chem_tape.tree_library import verify_entries

TASK = '2026-10-11-1228'
ARMS = ('R-tree', 'R-order', 'R-S', 'R-all')
DATA = Path(__file__).with_name('data') / 'order_cap_1228'
BANK_HASH = '2fc0d88c67ae651cbf3b927ecdedcebdd60220e30307ed4f9aa2bb428803d74a'
PILOT_SHA = '3f978ba320e9e4b1110caa29e2c7c2cf7e5cf5c8f716397e240ec33770cc5a84'
BOOTSTRAP_SEED = 202610111228
DRAWS = 8192
TIMINGS = ('literal_seconds', 'extraction_census_seconds', 'all_extraction_census_seconds', 'validation_seconds')


def load_bank():
    bank = json.loads((DATA / 'bank.json').read_text())
    if digest(bank) != BANK_HASH or not bank['admitted']:
        raise ValueError('frozen 1129 bank hash/admission mismatch')
    # Check semantics and witnesses only; no screening or searches.
    base.bank_module.verify(bank['screen']['cells'])
    if [len(bank['split'][p]) for p in ('source', 'development', 'protected')] != [24, 6, 24]:
        raise ValueError('wrong frozen split')
    return bank


def seed(domain, cell, build, repeat, attempt):
    raw = json.dumps([TASK, domain, cell, build, repeat, attempt], separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1 << 63) - 1)


def schedules(bank, smoke=False):
    return {phase: [dict(cell=c, arm=a, build=b, repeat=r,
                         seeds=[seed(('smoke_' if smoke else '') + phase, c, b, r, k) for k in range(8)])
                    for c in bank['split']['source' if phase == 'source' else 'development']
                    for b in range(1 if smoke else 24)
                    for r in range(2 if phase == 'source' or smoke else 4)
                    for a in (('R-tree',) if phase == 'source' else ARMS)]
            for phase in ('source', 'score')}


def seed_audit(bank):
    old = base.seed_audit(bank)
    historic = set()
    for values in old['published_seed_sets'].values():
        historic.update(values)
    # base audit checks against historical artifacts; new seeds need that same check.
    def collect(value, key=''):
        if isinstance(value, dict):
            for k, v in value.items():
                collect(v, k if 'seed' in k else key)
        elif isinstance(value, list):
            for v in value:
                collect(v, key)
        elif isinstance(value, int) and 'seed' in key:
            historic.add(value)
    import gzip
    historic.update(range(7000, 7800))
    historic.update(range(9000, 9006))
    for artifact in old['historical_artifacts']:
        path = Path(artifact['path'])
        raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != artifact['sha256']:
            raise ValueError('historical artifact changed')
        collect(json.loads(raw))
    published, all_new = {}, set()
    for smoke in (False, True):
        for phase, metas in schedules(bank, smoke).items():
            uses = {}
            for m in metas:
                for k, s in enumerate(m['seeds']):
                    uses.setdefault(s, []).append((m, k))
            expected = {'R-tree'} if phase == 'source' else set(ARMS)
            for records in uses.values():
                if (len(records) != len(expected) or {m['arm'] for m, _ in records} != expected
                        or len({(m['cell'], m['build'], m['repeat'], k) for m, k in records}) != 1):
                    raise ValueError('unintended seed reuse')
            values = set(uses)
            if values & (historic | all_new):
                raise ValueError('historical/phase seed collision')
            all_new.update(values)
            published[('smoke_' if smoke else '') + phase] = sorted(values)
    return dict(admitted=True, historical_count=len(historic), historical_hash=digest(sorted(historic)),
                pilot_audit_hash=digest(old), published_seed_sets=published)


def freeze(bank):
    raw = (DATA / 'pilot_freeze.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != PILOT_SHA:
        raise ValueError('pilot method freeze changed')
    pilot = json.loads(raw)
    current = base.methods()
    # Only the cap option changes an existing file; the new driver/report is separate.
    for path, expected in pilot['methods'].items():
        if path not in ('experiments/chem_tape/order_library.py', 'rust_extension') and current.get(path) != expected:
            raise ValueError('unchanged 1129 method differs: ' + path)
    frozen = base.freeze(bank)
    frozen.update(task=TASK, pilot_freeze_sha256=PILOT_SHA, arms=list(ARMS), builds=24,
                  source_repeats=2, score_repeats=4, extractor_all=order_library.RECIPE | dict(cap=None),
                  bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='paired whole acquisition builds'),
                  decision=dict(precedence=['lower > 0.67: end', 'upper < 0.80: useful', 'otherwise: unresolved']))
    return frozen


def libraries_from(rows, bank, builds):
    libraries = []
    for b in range(builds):
        corpus = [r for r in rows if r['build'] == b]
        capped = order_library.build(corpus, bank['split']['source'], bank['inputs'])
        uncapped = order_library.build(corpus, bank['split']['source'], bank['inputs'], cap=None)
        start = time.monotonic()
        if (uncapped['semantic'][:16] != capped['semantic']
                or len(uncapped['semantic']) != uncapped['eligible_semantic_classes']):
            raise ValueError('R-all is not the complete eligible pool with exact R-S prefix')
        observed = set()
        for row in corpus:
            if row['solved']:
                tree = Tree(tuple(row['attempts'][-1]['solver_tree']))
                observed.update(tree.prefix[p:tree.ends[p]] for p in range(1, len(tree.prefix)))
        for entry in uncapped['semantic']:
            if tuple(entry['prefix']) not in observed or not set(entry['source_cells']) <= set(bank['split']['source']):
                raise ValueError('entry does not trace to its own source corpus')
        verify_entries(uncapped['semantic'], bank['inputs'])
        capped.update(semantic_all=uncapped['semantic'], all_helper_diagnostics=uncapped['helper_diagnostics'],
                      all_extraction_census_seconds=uncapped['extraction_census_seconds'],
                      validation_seconds=time.monotonic() - start)
        libraries.append(capped)
    return libraries


def deterministic(libs):
    return [{k: v for k, v in lib.items() if k not in TIMINGS} for lib in libs]


def envelopes(metas, bank, libs, frozen):
    # base chooses donors from source-only prefixes; all other arms use its old path.
    if any(m['arm'] not in ARMS for m in metas):
        raise ValueError('unapproved arm')
    jobs = []
    for m in metas:
        if m['arm'] == 'R-all':
            proxy = m | dict(arm='R-S')
            all_libs = [dict(semantic=lib['semantic_all']) for lib in libs]
            job = base.envelopes([proxy], bank, all_libs, frozen)[0]
            jobs.append((m, *job[1:]))
        else:
            jobs.extend(base.envelopes([m], bank, libs, frozen))
    # Canonical programs and helper/role annotations never reach a worker.
    return [(m, dict(id=cell['id'], labels=cell['labels']), inputs, cutoff, donors)
            for m, cell, inputs, cutoff, donors in jobs]


def classify(interval):
    low, high = interval
    if low > 0.67:
        return 'end_recipe_worthwhile_one_third_saving_excluded'
    if high < 0.80:
        return 'useful_acquisition_return_to_strategy_price_protected_stage'
    return 'unresolved_return_to_strategy_price_resolution'


def estimate(point, samples):
    if not np.all(np.isfinite(samples)):
        raise ValueError('nonfinite bootstrap')
    return dict(point=float(point), interval95=np.quantile(samples, [0.025, 0.975]).tolist())


def summarize(rows, libs, bank, smoke=False):
    metas = schedules(bank, smoke)['score']
    def key(r):
        return (r['build'], r['cell'], r['repeat'], r['arm'])
    by = {key(r): r for r in rows}
    if len(by) != len(rows) or set(by) != {key(m) for m in metas}:
        raise ValueError('analysis requires complete fixed grid')
    for m in metas:
        if by[key(m)]['seeds'] != m['seeds']:
            raise ValueError('analysis seed pairing mismatch')
    builds = 1 if smoke else 24
    cells = bank['split']['development']
    repeats = 2 if smoke else 4
    arrays = {metric: {a: np.asarray([[[by[b, c, r, a][metric] for r in range(repeats)]
                                      for c in cells] for b in range(builds)], dtype=float)
                      for a in ARMS} for metric in ('evaluations', 'worker_seconds', 'solved')}
    for a in ARMS:
        for r in (r for r in rows if r['arm'] == a):
            if not r['solved'] and r['evaluations'] != 524288:
                raise ValueError('failure is not charged the full cap')
    selected = np.random.default_rng(BOOTSTRAP_SEED).integers(builds, size=(DRAWS, builds))
    blocks = {m: {a: v.mean(axis=(1, 2)) for a, v in aa.items()} for m, aa in arrays.items()}
    contrasts = {}
    for denom in ('R-tree', 'R-S', 'R-order'):
        result = {}
        for metric in ('evaluations', 'worker_seconds'):
            num, den = blocks[metric]['R-all'], blocks[metric][denom]
            result[metric] = estimate(num.mean()/den.mean(), num[selected].mean(1)/den[selected].mean(1))
        logs = {a: np.log(arrays['evaluations'][a]).mean(axis=(1, 2)) for a in ('R-all', denom)}
        result['geometric_evaluations'] = estimate(np.exp((logs['R-all']-logs[denom]).mean()),
                                                  np.exp((logs['R-all']-logs[denom])[selected].mean(1)))
        diff = blocks['solved']['R-all'] - blocks['solved'][denom]
        result['solve_fraction_difference'] = estimate(diff.mean(), diff[selected].mean(1))
        contrasts['R-all/' + denom] = result
    arms = {}
    tree_log = np.log(arrays['evaluations']['R-tree']).mean()
    gap = tree_log - np.log(arrays['evaluations']['R-order']).mean()
    for a in ARMS:
        rr = [r for r in rows if r['arm'] == a]
        operators = [p['operator'] for r in rr for p in r['attempts']]
        arms[a] = dict(jobs=len(rr), solves=sum(r['solved'] for r in rr),
                       capped_mean=float(arrays['evaluations'][a].mean()),
                       geometric_mean=float(np.exp(np.log(arrays['evaluations'][a]).mean())),
                       mean_worker_seconds=float(arrays['worker_seconds'][a].mean()),
                       worker_seconds=sum(r['worker_seconds'] for r in rr),
                       log_gap_recovered=None if gap <= 0 else float((tree_log - np.log(arrays['evaluations'][a]).mean())/gap),
                       operators={k: sum(p.get(k, 0) for p in operators) for k in sorted({k for p in operators for k in p})})
    coverage = []
    strata = {str(n): [] for n in range(3)}
    for b, lib in enumerate(libs):
        included = {h for h, d in lib['all_helper_diagnostics'].items() if d['semantic']['included']}
        for c in cells:
            needed = next(x['helpers'] for x in bank['screen']['cells'] if x['id'] == c)
            n = len(included & set(needed))
            coverage.append(dict(build=b, cell=c, needed_helpers_present=n))
            strata[str(n)].extend(by[b, c, r, a] for r in range(repeats) for a in ARMS)
    coverage_costs = {n: dict(paired_units=len(rr)//len(ARMS), arms={a: dict(
        jobs=sum(r['arm'] == a for r in rr),
        capped_mean=None if not rr else float(np.mean([r['evaluations'] for r in rr if r['arm'] == a])),
        worker_seconds=sum(r['worker_seconds'] for r in rr if r['arm'] == a)) for a in ARMS}) for n, rr in strata.items()}
    economics = {}
    for metric in ('evaluations', 'worker_seconds'):
        acq = np.array([lib['acquisition_evaluations'] if metric == 'evaluations' else
                        lib['acquisition_worker_seconds'] + sum(lib[k] for k in TIMINGS if k != 'literal_seconds') for lib in libs])
        saving = blocks[metric]['R-tree'] - blocks[metric]['R-all']
        boot_rate = saving[selected].mean(1)/acq[selected].mean(1)
        lo, hi = np.quantile(boot_rate, [0.025, 0.975])
        economics[metric] = dict(mean_acquisition=float(acq.mean()), mean_saving=float(saving.mean()),
                                 repayment_searches=None if saving.mean() <= 0 else float(acq.mean()/saving.mean()),
                                 repayment_interval95=[None if hi <= 0 else float(1/hi), None if lo <= 0 else float(1/lo)],
                                 repayment_unbounded=bool(lo <= 0))
    primary = contrasts['R-all/R-tree']['evaluations']
    return dict(arms=arms, contrasts=contrasts, primary='R-all/R-tree capped arithmetic mean evaluations',
                decision='smoke_only_no_decision' if smoke else classify(primary['interval95']),
                smaller_saving_supported=primary['interval95'][1] < 1,
                bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='whole paired builds; equal cell/repeat weights; ratio of pooled means'),
                acquisition=[dict(build=b, source_jobs=lib['source_jobs'], source_solves=lib['source_solves'],
                                  evaluations=lib['acquisition_evaluations'], worker_seconds=lib['acquisition_worker_seconds'],
                                  library_sizes={k: len(lib[k]) for k in ('semantic', 'semantic_all')},
                                  timing={k: lib[k] for k in TIMINGS}) for b, lib in enumerate(libs)],
                coverage=coverage, coverage_costs_descriptive=coverage_costs, economics_against_R_tree=economics,
                scope='External fitting, frozen recurrence recipe, six development cells of x4-order-v1; no fresh-bank transfer, helper causality or inherited-adaptation claim',
                economics_scope='All failed sources charged; worker cost includes both extractions, census and preparation validation; replay validation reported separately; no repayment claim against cheaper R-order')


def prepare(args, out, deadline):
    start = time.monotonic()
    bank = load_bank()
    frozen, schedule, audit = freeze(bank), schedules(bank, args.smoke), seed_audit(bank)
    for name, data in [('bank.json', bank), ('method_freeze.json', frozen), ('schedules.json', schedule), ('seed_audit.json', audit)]:
        write_json(out, name, data)
    rows, elapsed = base.run_batch(out, 'acquisition.jsonl', envelopes(schedule['source'], bank, None, frozen), args.workers, deadline)
    rows = base.validate_rows(rows, schedule['source'], bank)
    libs = libraries_from(rows, bank, 1 if args.smoke else 24)
    write_json(out, 'libraries.json', libs)
    p = dict(admitted=True, smoke=args.smoke, source_rows_hash=digest(rows), libraries_hash=digest(libs),
             bank_hash=digest(bank), freeze_hash=digest(frozen), schedule_hash=digest(schedule), audit_hash=digest(audit),
             source_batch_seconds=elapsed, seconds=time.monotonic()-start, source_jobs=len(rows),
             source_solves=sum(r['solved'] for r in rows), protected_searches=0, workers=args.workers,
             git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip())
    if time.monotonic() > deadline:
        raise TimeoutError('preparation deadline exceeded during verification')
    p['preparation_hash'] = digest(p)
    write_json(out, 'preparation.json', p)
    print('prepared', p, flush=True)


def load_prepared(path, smoke):
    if (path / 'failure.json').exists():
        raise ValueError('preparation has recorded failure')
    def read(name):
        return json.loads((path / name).read_text())
    bank, frozen, libs, schedule, p, audit = [read(n + '.json') for n in
        ('bank', 'method_freeze', 'libraries', 'schedules', 'preparation', 'seed_audit')]
    rows = base.validate_rows([json.loads(line) for line in (path / 'acquisition.jsonl').read_text().splitlines()], schedules(bank, smoke)['source'], bank)
    if (not p['admitted'] or p['smoke'] != smoke or digest(bank) != BANK_HASH
            or digest(frozen) != digest(freeze(load_bank())) or schedule != schedules(bank, smoke) or audit != seed_audit(bank)
            or p['preparation_hash'] != digest({k: v for k, v in p.items() if k != 'preparation_hash'})
            or any(p[k + '_hash'] != digest(v) for k, v in
                   [('source_rows', rows), ('libraries', libs), ('bank', bank), ('freeze', frozen), ('schedule', schedule), ('audit', audit)])):
        raise ValueError('preparation provenance/method mismatch')
    start = time.monotonic()
    rebuilt = libraries_from(rows, bank, 1 if smoke else 24)
    if deterministic(libs) != deterministic(rebuilt):
        raise ValueError('source-only reconstruction mismatch')
    return bank, frozen, libs, schedule, p, time.monotonic()-start


def score(args, out, deadline):
    bank, frozen, libs, schedule, p, replay_seconds = load_prepared(Path(args.prepared), args.smoke)
    for name, data in [('bank.json', bank), ('method_freeze.json', frozen), ('libraries.json', libs), ('schedules.json', schedule)]:
        write_json(out, name, data)
    rows, elapsed = base.run_batch(out, 'score.jsonl', envelopes(schedule['score'], bank, libs, frozen), args.workers, deadline)
    rows = base.validate_rows(rows, schedule['score'], bank)
    report = summarize(rows, libs, bank, args.smoke)
    report.update(admitted=True, smoke=args.smoke, protected_searches=0, workers=args.workers,
                  score_batch_seconds=elapsed, replay_validation_seconds=replay_seconds,
                  preparation_hash=p['preparation_hash'], score_rows_hash=digest(rows))
    plots(out, rows, libs)
    if time.monotonic() > deadline:
        raise TimeoutError('score deadline exceeded during report')
    write_json(out, 'report.json', report)
    print('scored', len(rows), 'wall', elapsed, 'arms', report['arms'], flush=True)


def plots(out, rows, libs):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(17, 4))
    xs = [256, 4096, 16384, 65536, 131072, 262144, 524288]
    for a in ARMS:
        rr = [r for r in rows if r['arm'] == a]
        axes[0].plot(xs, [np.mean([r['solved'] and r['evaluations'] <= x for r in rr]) for x in xs], label=a)
        for panel, field in [(1, 'curve'), (2, 'phenotype_diversity_curve')]:
            timelines = []
            for r in rr:
                line, offset = [], 0
                for attempt in r['attempts']:
                    line.extend((offset + p[0], p[1]) for p in attempt[field])
                    offset += attempt['evaluations']
                timelines.append(line)
            axes[panel].plot(xs, [np.mean([([v for t, v in line if t <= x] or [line[0][1]])[-1] for line in timelines]) for x in xs], label=a)
    for i, title in enumerate(('D625 solves', 'Training best score; restart resets', 'Training output diversity')):
        axes[i].set(xscale='log', xlabel='Evaluations', title=title)
        axes[i].legend(fontsize=7)
    axes[3].plot([len(lib['semantic']) for lib in libs], label='R-S')
    axes[3].plot([len(lib['semantic_all']) for lib in libs], label='R-all')
    axes[3].set(xlabel='Build', ylabel='Library classes')
    axes[3].legend()
    fig.tight_layout()
    fig.savefig(out / 'dynamics.png', dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'score'))
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--prepared')
    parser.add_argument('--seconds', type=int)
    args = parser.parse_args()
    limit = 1170 if args.phase == 'prepare' else 5370
    seconds = limit if args.seconds is None else args.seconds
    if args.workers < 1 or not 0 < seconds <= limit or (args.phase == 'score' and not args.prepared):
        parser.error('positive workers, approved phase deadline and --prepared for score required')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if any((out / name).exists() for name in ('failure.json', 'preparation.json', 'report.json', 'acquisition.jsonl', 'score.jsonl')):
        parser.error('RUN_DIR contains previous experiment artifacts')
    deadline = time.monotonic() + seconds
    try:
        (prepare if args.phase == 'prepare' else score)(args, out, deadline)
        if time.monotonic() > deadline:
            raise TimeoutError('fixed phase deadline exceeded')
    except Exception as error:
        write_json(out, 'failure.json', dict(admitted=False, phase=args.phase, smoke=args.smoke, error=str(error)))
        raise


if __name__ == '__main__':
    main()
