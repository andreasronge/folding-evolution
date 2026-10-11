"""1938 frozen signed-gate acquisition; development smoke, complete protected inference."""

import argparse
import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import signed_gate_bank as bank_module, order_run as base
from experiments.chem_tape import order_library
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.tree_gp_search import Tree, FUNCTIONS, TERMINALS
from experiments.chem_tape.tree_library import verify_entries

TASK = '2026-10-11-1938'
ARMS = ('R-tree', 'R-all', 'R-order', 'R-gate')
DATA = Path(__file__).with_name('data') / 'signed_gate_1938'
BANK_HASH = '1349277c1e74ea19d8fe5efb7b0ad5c1e1db45887cbbc55fcb28079e9fbc910c'
TRANSPORT_SHA = '31a9cb2bd424e0a3df64240307f55ebb9454a236a69b38dfcc6a6ffe942752ce'
BOOTSTRAP_SEED = 202610111938
DRAWS = 8192
TIMINGS = ('literal_seconds', 'extraction_census_seconds', 'validation_census_seconds')


def load_bank():
    bank_module.executable_check()
    bank = json.loads((DATA / 'manifest.json').read_text())
    if digest(bank) != BANK_HASH or not bank['admitted'] or not bank['screen']['complete']:
        raise ValueError('frozen screened bank hash/admission mismatch')
    bank_module.verify(bank['screen']['cells'])
    if bank['split'] != bank_module.split([c for c in bank['screen']['cells'] if c['retained']]):
        raise ValueError('frozen development/protected split changed')
    pre = json.loads(gzip.decompress((DATA / 'presearch.json.gz').read_bytes()))
    if (pre['bank_hash'] != BANK_HASH or digest(pre['freeze']) != digest(freeze(bank))
            or pre['schedule'] != schedules(bank) or pre['smoke_schedule'] != schedules(bank, True)
            or pre['seed_audit'] != seed_audit(bank)):
        raise ValueError('presearch method/schedule/seed freeze mismatch')
    return bank


def transport():
    from experiments.chem_tape.rectified_run import transport as read_transport
    return read_transport()


def seed(domain, cell, build, repeat, attempt):
    raw = json.dumps([TASK, domain, cell, build, repeat, attempt], separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1 << 63) - 1)


def schedules(bank, smoke=False):
    phases = ('source', 'development') if smoke else ('source', 'development', 'protected')
    return {phase: [dict(cell=c, arm=a, build=b, repeat=r,
                         seeds=[seed(('smoke_' if smoke else '') + phase, c, b, r, k) for k in range(8)])
                    for c in bank['split'][phase]
                    for b in range(1 if smoke else 24)
                    for r in range(2 if phase != 'protected' else 4)
                    for a in (('R-tree',) if phase == 'source' else ARMS)]
            for phase in phases}


def seed_audit(bank):
    historic = set(range(19380000, 19384718)) | set(range(19480000, 19484718)) | set(range(19390000, 19393028))
    historic |= set(range(5000, 5300)) | set(range(70000, 90400)) | set(range(7000, 7800)) | set(range(9000, 9006))
    def collect(value, key=''):
        if isinstance(value, dict):
            for k, v in value.items():
                collect(v, k if 'seed' in k else key)
        elif isinstance(value, list):
            for v in value:
                collect(v, key)
        elif isinstance(value, int) and 'seed' in key:
            historic.add(value)
    artifacts = []
    roots = [Path(__file__).with_name('data'), Path('/Users/andreas/developer/folding-evolution/experiments/output')]
    for root in roots:
        for path in sorted(root.rglob('*')):
            if (path.is_file() and path.suffix in ('.json', '.gz')
                    and any(k in path.name for k in ('schedule', 'seed_audit', 'historical_seeds'))
                    and TASK not in str(path)):
                raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
                collect(json.loads(raw))
                artifacts.append(dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest()))
    saved = transport()
    collect(saved['schedules.json'])
    collect(saved['seed_audit.json'])
    published, all_new = {}, set()
    for smoke in (False, True):
        for phase, metas in schedules(bank, smoke).items():
            uses = {}
            for m in metas:
                for k, value in enumerate(m['seeds']):
                    uses.setdefault(value, []).append((m, k))
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
    timing = [seed('cap_timing', bank_module.SEEN[0], 0, 0, k) for k in range(8)]
    if set(timing) & (historic | all_new) or len(set(timing)) != 8:
        raise ValueError('timing seed collision')
    published['cap_timing'] = timing
    return dict(admitted=True, historical_count=len(historic), historical_hash=digest(sorted(historic)),
                historical_artifacts=artifacts, transport_sha256=TRANSPORT_SHA,
                stage0_ranges=[[19380000,19384717],[19480000,19484717],[19390000,19393027]],
                published_seed_sets=published)


def helper_vectors(inputs):
    return {f'{kind}{a}{b}': outputs([bank_module.helper(kind, a, b).program], inputs, 'v2_x4')[0].astype('<i8').tobytes()
            for kind in ('p', 'n') for a, b in itertools.permutations(range(4), 2)}


def freeze(bank):
    from experiments.chem_tape.independent_input_run import method_hashes
    from experiments.chem_tape.order_protected_run import EXTENSIONS
    current = method_hashes()
    extensions = EXTENSIONS | {'experiments/chem_tape/tree_gp_search.py':
        '23bfe46c7cb1edcbd7d5b6a484e09c8cb754a050705b5ef8731f3e2eca249af0'}  # approved 3a18ef5
    saved = transport()
    old = saved['method_freeze.json']
    modules = ('tree_gp_search.py', 'tree_library.py', 'order_library.py', 'order_run.py',
               'composition_search.py', 'composition_run.py', 'independent_input_bank.py',
               'assembly_bank.py', 'tree_gp_validate.py')
    for path, expected in old['methods'].items():
        if path.startswith(('src/', 'rust/src/')) or path in ['experiments/chem_tape/' + n for n in modules]:
            if current.get(path) != extensions.get(path, expected):
                raise ValueError('reviewed engine/method changed: ' + path)
    gates = [list(bank_module.helper(kind, a, b).prefix) for kind in ('p', 'n')
             for a, b in itertools.permutations(range(4), 2)]
    supplied = [dict(prefix=p, nodes=len(p), compiled_length=len(Tree(tuple(p)).program)) for p in gates]
    verify_entries(supplied, bank['inputs'])
    for lib in saved['libraries.json']:
        verify_entries(lib['semantic_all'], bank['inputs'])
    # Measured overhead is recorded separately; freeze must be deterministic.
    return dict(task=TASK, bank_hash=digest(bank), methods=current, executable=bank_module.executable_check(),
                grammar=base.GRAMMAR, cutoff=65536, attempts=8, population=256, crossover=0.5,
                extractor=order_library.RECIPE | dict(cap=None), builds=24, source_repeats=2,
                development_repeats=2, protected_repeats=4, protected_count=len(bank['split']['protected']),
                arms=list(ARMS), gates=gates, transport_sha256=TRANSPORT_SHA,
                transport_library_hashes=[digest(lib['semantic_all']) for lib in saved['libraries.json']],
                donors='uniform entries; unchanged half-library mutation draws/fallback',
                protected_searches=0, frozen_before_search=True,
                decision=['upper < 0.80: material saving', 'lower >= 0.80: material saving excluded', 'otherwise: unresolved'],
                bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='paired two-way whole builds and cells; repeats retained'))


def libraries_from(rows, bank, builds):
    libraries = []
    by = {c['id']: c for c in bank['screen']['cells']}
    vectors = helper_vectors(bank['inputs'])
    for b in range(builds):
        corpus = [r for r in rows if r['build'] == b]
        if any(not r['solved'] and r['evaluations'] != 524288 for r in corpus):
            raise ValueError('source failure not charged full cap')
        lib = order_library.build(corpus, bank['split']['source'], bank['inputs'], cap=None, diagnostic_vectors=vectors)
        start = time.monotonic()
        observed = set()
        row_by = {(r['cell'], r['repeat']): r for r in corpus}
        for census in lib['census']:
            row = row_by[census['cell'], census['repeat']]
            cell = by[row['cell']]
            census.update(own_helper=cell['helpers'][0], own_helper_sizes=census['helpers'][cell['helpers'][0]],
                          root_op=None, evaluations=row['evaluations'],
                          worker_seconds=row['worker_seconds'], first_attempt_solved=row['attempts'][0]['solved'])
            if row['solved']:
                tree = Tree(tuple(row['attempts'][-1]['solver_tree']))
                prefixes = [tree.prefix[p:tree.ends[p]] for p in range(1, len(tree.prefix))]
                observed.update(prefixes)
                op = tree.prefix[0]
                census['root_op'] = (TERMINALS + FUNCTIONS)[op]
        for entry in lib['semantic']:
            if tuple(entry['prefix']) not in observed or not set(entry['source_cells']) <= set(bank['split']['source']):
                raise ValueError('entry does not trace to its own source corpus')
        verify_entries(lib['semantic'], bank['inputs'])
        if len(lib['semantic']) != lib['eligible_semantic_classes']:
            raise ValueError('R-all omitted eligible classes')
        lib['validation_census_seconds'] = time.monotonic() - start
        libraries.append(lib)
    return libraries


def deterministic(libs):
    return [{k: v for k, v in lib.items() if k not in TIMINGS} for lib in libs]


def envelopes(metas, bank, libs, frozen, phase='source', smoke=False):
    allowed = bank['split'][phase]
    if smoke and phase == 'protected':
        raise ValueError('protected smoke is forbidden')
    by = {c['id']: c for c in bank['screen']['cells']}
    old = transport()['libraries.json']
    jobs = []
    for m in metas:
        if (m['arm'] not in (('R-tree',) if phase == 'source' else ARMS)
                or m['cell'] not in allowed or not 0 <= m['build'] < (1 if smoke else 24)):
            raise ValueError('unapproved phase/cell/arm/build')
        donors = (None if m['arm'] == 'R-tree' else frozen['gates'] if m['arm'] == 'R-gate'
                  else [e['prefix'] for e in (libs[m['build']]['semantic'] if m['arm'] == 'R-all'
                                             else old[m['build']]['semantic_all'])])
        jobs.append((m, dict(id=m['cell'], labels=by[m['cell']]['labels']), bank['inputs'], frozen['cutoff'], donors))
    return jobs


def validate_rows(rows, metas, bank):
    from experiments.chem_tape.order_protected_run import validate_rows as validate
    rows = validate(rows, metas, bank)
    for row in rows:
        for attempt in row['attempts']:
            if attempt['evaluations'] % 256 or (not attempt['solved'] and attempt['evaluations'] != 65536):
                raise ValueError('invalid attempt cap')
    return rows


def throughput(rows, elapsed, workers):
    worker = sum(r['worker_seconds'] for r in rows)
    return dict(wall_seconds=elapsed, worker_seconds=worker, workers=workers,
                effective_concurrency=worker / elapsed, jobs_per_second=len(rows) / elapsed,
                evaluations_per_wall_second=sum(r['evaluations'] for r in rows) / elapsed,
                max_worker_seconds=max(r['worker_seconds'] for r in rows),
                projected_2304_jobs_seconds=2304 * elapsed / len(rows),
                projected_8064_jobs_seconds=8064 * elapsed / len(rows))


def prepare(args, out, deadline):
    start = time.monotonic()
    bank = load_bank()
    frozen, schedule, audit = freeze(bank), schedules(bank, args.smoke), seed_audit(bank)
    prior_start = time.monotonic()
    prior = [bank_module.helper(k, a, b) for k in ('p','n') for a,b in itertools.permutations(range(4),2)]
    verify_entries([dict(prefix=list(t.prefix), nodes=len(t.prefix), compiled_length=len(t.program)) for t in prior], bank['inputs'])
    supplied_prior_construction_validation_seconds = time.monotonic()-prior_start
    for name, data in [('bank.json', bank), ('method_freeze.json', frozen), ('schedules.json', schedule), ('seed_audit.json', audit)]:
        write_json(out, name, data)
    rows, elapsed = base.run_batch(out, 'acquisition.jsonl', envelopes(schedule['source'], bank, None, frozen, smoke=args.smoke), args.workers, deadline)
    rows = validate_rows(rows, schedule['source'], bank)
    libs = libraries_from(rows, bank, 1 if args.smoke else 24)
    write_json(out, 'libraries.json', libs)
    p = dict(admitted=True, smoke=args.smoke, source_rows_hash=digest(rows), libraries_hash=digest(libs),
             bank_hash=digest(bank), freeze_hash=digest(frozen), schedule_hash=digest(schedule), audit_hash=digest(audit),
             source_batch_seconds=elapsed, throughput=throughput(rows, elapsed, args.workers), seconds=time.monotonic()-start,
             supplied_prior_construction_validation_seconds=supplied_prior_construction_validation_seconds,
             source_jobs=len(rows), source_solves=sum(r['solved'] for r in rows), protected_searches=0, workers=args.workers,
             git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip())
    p['preparation_hash'] = digest(p)
    write_json(out, 'preparation.json', p)
    print('prepared', p, flush=True)


def load_prepared(path, smoke):
    if (path / 'failure.json').exists():
        raise ValueError('preparation has recorded failure')
    def read(name):
        return json.loads((path / (name + '.json')).read_text())
    bank, frozen, libs, schedule, p, audit = [read(n) for n in
        ('bank', 'method_freeze', 'libraries', 'schedules', 'preparation', 'seed_audit')]
    rows = validate_rows([json.loads(line) for line in (path / 'acquisition.jsonl').read_text().splitlines()], schedules(bank, smoke)['source'], bank)
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


def classify(interval):
    low, high = interval
    if high < 0.80:
        return 'material_saving_recipe_extends_return_to_strategy'
    if low >= 0.80:
        return 'pooled_harm_return_to_strategy' if low > 1 else 'material_saving_excluded_return_to_strategy'
    return 'unresolved_return_to_strategy_price_resolution'


def estimate(point, samples):
    if not np.all(np.isfinite(samples)):
        raise ValueError('nonfinite bootstrap')
    return dict(point=float(point), interval95=np.quantile(samples, [0.025, 0.975]).tolist())


def bootstrap_indices(builds, cells):
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    return (rng.integers(builds, size=(DRAWS, builds)),
            rng.integers(cells, size=(DRAWS, cells)))


def bootstrap_mean(array, builds, cells):
    # Retain paired arms and every repeat under the same crossed resampling.
    return array.mean(2)[builds[:, :, None], cells[:, None, :]].mean((1, 2))


def summarize(rows, libs, bank, smoke=False, phase='protected'):
    metas = schedules(bank, smoke)[phase]
    rows = validate_rows(rows, metas, bank)
    builds = 1 if smoke else 24
    cells = bank['split'][phase]
    repeats = 4 if phase == 'protected' else 2
    by = {(r['build'], r['cell'], r['repeat'], r['arm']): r for r in rows}
    arrays = {metric: {a: np.asarray([[[by[b, c, r, a][metric] for r in range(repeats)]
                                      for c in cells] for b in range(builds)], dtype=float)
                      for a in ARMS} for metric in ('evaluations', 'worker_seconds', 'solved')}
    bi, ci = bootstrap_indices(builds, len(cells))
    boot = {m: {a: bootstrap_mean(v, bi, ci) for a, v in aa.items()} for m, aa in arrays.items()}
    contrasts = {}
    for denominator in ('R-tree', 'R-order', 'R-gate'):
        result = {}
        for metric in ('evaluations', 'worker_seconds'):
            num, den = arrays[metric]['R-all'], arrays[metric][denominator]
            result[metric] = estimate(num.mean()/den.mean(), boot[metric]['R-all']/boot[metric][denominator])
        diff = arrays['solved']['R-all'].mean() - arrays['solved'][denominator].mean()
        result['solve_fraction_difference'] = estimate(diff, boot['solved']['R-all'] - boot['solved'][denominator])
        contrasts['R-all/' + denominator] = result
    arms = {}
    for arm in ARMS:
        rr = [r for r in rows if r['arm'] == arm]
        arms[arm] = dict(jobs=len(rr), solves=sum(r['solved'] for r in rr),
                         first_attempt_solves=sum(r['attempts'][0]['solved'] for r in rr),
                         first_attempt_rate=float(np.mean([r['attempts'][0]['solved'] for r in rr])),
                         capped_mean=float(arrays['evaluations'][arm].mean()),
                         evaluation_quantiles=dict(zip(('p50','p90','p95','p99','max'),
                                                       np.quantile(arrays['evaluations'][arm], [.5,.9,.95,.99,1]).tolist())),
                         mean_worker_seconds=float(arrays['worker_seconds'][arm].mean()),
                         worker_seconds=float(arrays['worker_seconds'][arm].sum()),
                         capped_jobs=sum(r['evaluations'] == 524288 for r in rr))
    coverage, acquisition = [], []
    for b, lib in enumerate(libs):
        included = {h for h, d in lib['helper_diagnostics'].items() if d['semantic']['included']}
        for c in cells:
            needed = next(x['helpers'] for x in bank['screen']['cells'] if x['id'] == c)
            coverage.append(dict(build=b, cell=c, needed_helpers=needed, present=sorted(included & set(needed)),
                                 needed_helpers_present=len(included & set(needed))))
        acquisition.append(dict(build=b, source_jobs=lib['source_jobs'], source_solves=lib['source_solves'],
                                evaluations=lib['acquisition_evaluations'], worker_seconds=lib['acquisition_worker_seconds'],
                                preparation_worker_seconds=lib['extraction_census_seconds'] + lib['validation_census_seconds'],
                                helpers=sorted(included), entries=len(lib['semantic']),
                                helper_diagnostics=lib['helper_diagnostics']))
    economics = {}
    historical = transport()['libraries.json'][:builds]
    for metric in ('evaluations', 'worker_seconds'):
        acq = np.asarray([lib['acquisition_evaluations'] if metric == 'evaluations' else
                          lib['acquisition_worker_seconds'] + lib['extraction_census_seconds'] + lib['validation_census_seconds'] for lib in libs])
        old_acq = np.asarray([lib['acquisition_evaluations'] if metric == 'evaluations' else
                              lib['acquisition_worker_seconds'] + sum(lib.get(k, 0) for k in
                              ('extraction_census_seconds','all_extraction_census_seconds','validation_seconds')) for lib in historical])
        ab, ob = acq[bi].mean(1), old_acq[bi].mean(1)
        economics[metric] = dict(new_acquisition=estimate(acq.mean(), ab),
                                  transported_acquisition=estimate(old_acq.mean(), ob), comparisons={})
        for denominator, charge in [('R-tree', False), ('R-order', False), ('R-order', True)]:
            delta_a = acq.mean() - (old_acq.mean() if charge else 0)
            delta_ab = ab - (ob if charge else 0)
            saving = arrays[metric][denominator].mean() - arrays[metric]['R-all'].mean()
            saving_b = boot[metric][denominator] - boot[metric]['R-all']
            # When old content is newly acquired, report cost-difference curves;
            # a negative intercept is a start-cost advantage, not a repayment.
            comparison = dict(mean_incremental_acquisition=float(delta_a), saving=estimate(saving, saving_b),
                              cost_difference_A_plus_N_S={str(n): estimate(delta_a-n*saving, delta_ab-n*saving_b)
                                                          for n in (0,1,10,100,1000)})
            if not charge:
                rate = saving_b / ab
                lo, hi = np.quantile(rate, [.025,.975])
                comparison.update(repayment_searches=None if saving <= 0 else float(acq.mean()/saving),
                                  repayment_interval95=[None if hi <= 0 else float(1/hi), None if lo <= 0 else float(1/lo)],
                                  repayment_unbounded=bool(lo <= 0))
            economics[metric]['comparisons'][denominator + ('_newly_acquired' if charge else '_owned')] = comparison
    census = [c for lib in libs for c in lib['census']]
    own = sum(bool(c['own_helper_sizes']) for c in census)
    solves = sum(c['solved'] for c in census)
    primary = contrasts['R-all/R-tree']['evaluations']
    secondary = contrasts['R-all/R-order']['evaluations']
    return dict(complete=True, arms=arms, contrasts=contrasts, primary='R-all/R-tree pooled capped arithmetic mean evaluations',
                decision=classify(primary['interval95']) if phase == 'protected' and not smoke else 'descriptive_no_efficacy_verdict',
                transport_interpretation='incremental search advantage resolved' if secondary['interval95'][1] < 1 else
                                         'higher cost than transported content resolved' if secondary['interval95'][0] > 1 else
                                         'no incremental advantage over transported content resolved',
                bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='paired two-way builds and cells; all repeats retained'),
                coverage=coverage, acquisition=acquisition, source_census=census, economics=economics,
                source_solver_census=dict(jobs=len(census), solves=solves, own_helper=own,
                                          own_helper_fraction=own/solves if solves else None,
                                          emittable_own_helper=sum(any(3 <= n <= 9 for n in c['own_helper_sizes']) for c in census),
                                          first_attempt_solves=sum(c['first_attempt_solved'] for c in census)),
                per_cell=[dict(arm=a, cell=c, jobs=builds*repeats,
                               solves=int(arrays['solved'][a][:, i].sum()),
                               capped_mean=float(arrays['evaluations'][a][:, i].mean()),
                               first_attempt_solves=sum(by[b,c,r,a]['attempts'][0]['solved'] for b in range(builds) for r in range(repeats)),
                               p95=float(np.quantile(arrays['evaluations'][a][:, i], .95)))
                          for a in ARMS for i,c in enumerate(cells)],
                scope='Frozen signed-gate rebindings of one construction; cell bootstrap sensitivity is not independent families. External acquisition; no helper causality, symmetric specificity, inherited discovery or uncapped time-to-solution.',
                economics_scope='Source failures charged. Worker acquisition includes extraction/census/validation; shared bank and replay overhead reported separately. Supplied prior has zero evolutionary acquisition and supplied family knowledge. N values illustrate cost curves, not an assumed deployment horizon.')


def score(args, out, deadline):
    bank, frozen, libs, schedule, p, replay = load_prepared(Path(args.prepared), args.smoke)
    phase = args.phase
    for name, data in [('bank.json', bank), ('method_freeze.json', frozen), ('libraries.json', libs), ('schedules.json', schedule)]:
        write_json(out, name, data)
    degenerate = all(not lib['semantic'] for lib in libs)
    metas = [m for m in schedule[phase] if not degenerate or m['arm'] != 'R-all']
    rows, elapsed = base.run_batch(out, 'score.jsonl', envelopes(metas, bank, libs, frozen, phase, args.smoke), args.workers, deadline)
    if degenerate:
        import copy
        clones = [copy.deepcopy(r) | dict(arm='R-all', degenerate_R_tree_replay=True) for r in rows if r['arm'] == 'R-tree']
        # Empty-donor fallback takes the ordinary variation RNG path. Exact paired
        # R-tree costs avoid duplicating identical scoring in this declared case.
        with (out / 'score.jsonl').open('a') as file:
            for row in clones:
                file.write(json.dumps(row, allow_nan=False) + '\n')
        rows.extend(clones)
    report = summarize(rows, libs, bank, args.smoke, phase)
    start = time.monotonic()
    plots(out, rows, libs)
    report.update(admitted=True, smoke=args.smoke, phase=phase, all_libraries_empty=degenerate,
                  supplied_prior_construction_validation_seconds=p.get('supplied_prior_construction_validation_seconds'),
                  protected_searches=len(rows) if phase == 'protected' else 0,
                  throughput=throughput(rows, elapsed, args.workers), replay_validation_seconds=replay,
                  plotting_seconds=time.monotonic()-start,
                  preparation_hash=p['preparation_hash'], score_rows_hash=digest(validate_rows(rows, schedule[phase], bank)))
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
    axes[3].plot([len(lib['semantic']) for lib in libs], label='R-all')
    axes[3].set(xlabel='Build', ylabel='Library classes')
    axes[3].legend()
    fig.tight_layout()
    fig.savefig(out / 'dynamics.png', dpi=140)
    plt.close(fig)


def capped_timing(args, out, deadline):
    bank, frozen, libs, schedule, p, replay = load_prepared(Path(args.prepared), True)
    cell = bank_module.SEEN[0]
    metas = [dict(cell=cell, build=0, repeat=0, arm=a,
                  seeds=[seed('cap_timing', cell, 0, 0, k) for k in range(8)]) for a in ARMS]
    jobs = envelopes(metas, bank, libs, frozen, 'development', True)
    # A synthetic unreachable label on a development fixture measures capped
    # throughput only. It never enters acquisition, scoring or inference.
    for job in jobs:
        job[1]['labels'] = list(job[1]['labels'])
        job[1]['labels'][0] = 10**12
    rows, elapsed = base.run_batch(out, 'timing.jsonl', jobs, args.workers, deadline)
    if any(r['solved'] or r['evaluations'] != 524288 or len(r['attempts']) != 8 for r in rows):
        raise ValueError('capped timing fixture did not consume all eight attempts')
    write_json(out, 'timing.json', dict(smoke=True, efficacy_observation=False, fixture_cell=cell,
               overridden_label=dict(index=0, value=10**12), rows=rows, throughput=throughput(rows, elapsed, args.workers),
               replay_validation_seconds=replay, preparation_hash=p['preparation_hash']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'development', 'protected', 'timing'))
    parser.add_argument('--workers', type=int, default=11)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--prepared')
    parser.add_argument('--seconds', type=int)
    args = parser.parse_args()
    limit = {'prepare': 1770, 'development': 1170, 'protected': 3570, 'timing': 300}[args.phase]
    seconds = args.seconds or limit
    if args.workers < 1 or seconds <= 0 or seconds > limit or (args.phase != 'prepare' and not args.prepared):
        parser.error('positive workers, approved phase limits, and --prepared for score required')
    if os.environ.get('RAYON_NUM_THREADS') != '1':
        parser.error('RAYON_NUM_THREADS=1 required for comparable worker costs')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if any((out / n).exists() for n in ('failure.json', 'preparation.json', 'report.json', 'acquisition.jsonl', 'score.jsonl')):
        parser.error('RUN_DIR contains previous experiment artifacts')
    if args.phase == 'timing' and not args.smoke:
        parser.error('timing is smoke-only')
    if args.smoke and args.phase == 'protected':
        parser.error('protected smoke is forbidden')
    deadline = time.monotonic() + seconds
    try:
        (prepare if args.phase == 'prepare' else capped_timing if args.phase == 'timing' else score)(args, out, deadline)
        if time.monotonic() > deadline:
            raise TimeoutError('fixed phase deadline exceeded during verification/report')
    except Exception as error:
        write_json(out, 'failure.json', dict(admitted=False, phase=args.phase, smoke=args.smoke, error=str(error)))
        raise


if __name__ == '__main__':
    main()
