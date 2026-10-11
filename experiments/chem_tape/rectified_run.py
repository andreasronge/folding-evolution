"""1315 fixed development rectifier probe; no protected searches or method tuning."""

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

from experiments.chem_tape import rectified_bank as bank_module, order_run as base
from experiments.chem_tape import order_cap_run as cap_run, order_library
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.tree_gp_search import Tree, FUNCTIONS, TERMINALS
from experiments.chem_tape.tree_library import verify_entries

TASK = '2026-10-11-1315'
ARMS = ('R-tree', 'R-rect', 'R-all', 'R-order-all')
DATA = Path(__file__).with_name('data') / 'rectified_1315'
BANK_HASH = 'eb7965937359a0b80ca169b69fe7e8ba1425f3151b56076369dcb905a91b5465'
TRANSPORT_SHA = '31a9cb2bd424e0a3df64240307f55ebb9454a236a69b38dfcc6a6ffe942752ce'
BOOTSTRAP_SEED = 202610111315
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
    return bank


def transport():
    raw = gzip.decompress((DATA / 'transport.json.gz').read_bytes())
    if hashlib.sha256(raw).hexdigest() != TRANSPORT_SHA:
        raise ValueError('transported 1228 artifact changed')
    saved = json.loads(raw)
    p = saved['preparation.json']
    if (not p['admitted'] or p['smoke'] or p['source_jobs'] != 1152
            or p['preparation_hash'] != digest({k: v for k, v in p.items() if k != 'preparation_hash'})):
        raise ValueError('transported preparation invalid')
    for key, name in [('libraries', 'libraries.json'), ('freeze', 'method_freeze.json'),
                      ('schedule', 'schedules.json'), ('audit', 'seed_audit.json')]:
        if p[key + '_hash'] != digest(saved[name]):
            raise ValueError('transported preparation hash mismatch: ' + name)
    return saved


def seed(domain, cell, build, repeat, attempt):
    raw = json.dumps([TASK, domain, cell, build, repeat, attempt], separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1 << 63) - 1)


def schedules(bank, smoke=False):
    return {phase: [dict(cell=c, arm=a, build=b, repeat=r,
                         seeds=[seed(('smoke_' if smoke else '') + phase, c, b, r, k) for k in range(8)])
                    for c in (bank['split']['source'] if phase == 'source' else
                              list(bank_module.SEEN) if smoke else bank['split']['development'])
                    for b in range(1 if smoke else 8)
                    for r in range(1 if smoke and phase == 'score' else 2)
                    for a in (('R-tree',) if phase == 'source' else ARMS)]
            for phase in ('source', 'score')}


def seed_audit(bank):
    old_bank = cap_run.load_bank()
    pilot, old = base.seed_audit(old_bank), cap_run.seed_audit(old_bank)
    historic = set(range(5000, 5300)) | set(range(70000, 90000)) | set(range(90000, 90400))
    historic |= set(range(7000, 7800)) | set(range(9000, 9006))
    def collect(value, key=''):
        if isinstance(value, dict):
            for k, v in value.items():
                collect(v, k if 'seed' in k else key)
        elif isinstance(value, list):
            for v in value:
                collect(v, key)
        elif isinstance(value, int) and 'seed' in key:
            historic.add(value)
    for artifact in pilot['historical_artifacts']:
        path = Path(artifact['path'])
        raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != artifact['sha256']:
            raise ValueError('historical seed artifact changed')
        collect(json.loads(raw))
    for audit in (pilot, old, transport()['seed_audit.json']):
        for values in audit['published_seed_sets'].values():
            historic.update(values)
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
                historical_artifacts=pilot['historical_artifacts'], historical_audit_hashes=[digest(pilot), digest(old)],
                stage0_ranges=[[5000, 5299], [70000, 89999], [90000, 90399]],
                transport_sha256=TRANSPORT_SHA, published_seed_sets=published)


def helper_vectors(inputs):
    return {f'{kind}{a}{b}': outputs([bank_module.helper(kind, a, b).program], inputs, 'v2_x4')[0].astype('<i8').tobytes()
            for kind in ('pos', 'neg') for a, b in itertools.combinations(range(4), 2)}


def freeze(bank):
    saved = transport()
    current = base.methods()
    for path, expected in saved['method_freeze.json']['methods'].items():
        if path not in ('experiments/chem_tape/order_library.py', 'rust_extension') and current.get(path) != expected:
            raise ValueError('reviewed engine/method changed: ' + path)
    rect = [list(bank_module.helper(kind, a, b).prefix) for kind in ('pos', 'neg')
            for a, b in itertools.combinations(range(4), 2)]
    old = [lib['semantic_all'] for lib in saved['libraries.json'][:8]]
    for entries in old + [[dict(prefix=p, nodes=len(p), compiled_length=len(Tree(tuple(p)).program)) for p in rect]]:
        verify_entries(entries, bank['inputs'])
    return dict(task=TASK, bank_hash=digest(bank), methods=current, executable=bank_module.executable_check(),
                grammar=base.GRAMMAR, cutoff=65536, attempts=8, population=256, crossover=0.5,
                extractor=order_library.RECIPE | dict(cap=None), builds=8, source_repeats=2, score_repeats=2,
                arms=list(ARMS), rect=rect, transport_sha256=TRANSPORT_SHA,
                transport_library_hashes=[digest(lib) for lib in old],
                donors='uniform entries; unchanged half-library mutation draws/fallback',
                stage0_preceded_freeze=True, protected_searches=0,
                recommendation='advisory descriptive investment criteria; capped arithmetic mean ratios',
                thresholds=dict(coverage_pairs=24, total_pairs=48, rect_solve_fraction=0.9,
                                rect_tree_ratio=0.5, all_tree_ratio=0.67, own_helper_fraction=0.25),
                bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='paired whole builds'))


def libraries_from(rows, bank, builds):
    libraries = []
    by = {c['id']: c for c in bank['screen']['cells']}
    vectors = helper_vectors(bank['inputs'])
    triple = {tuple(indices): np.asarray(bank['inputs'], dtype=np.int64)[:, indices].sum(1).astype('<i8').tobytes()
              for indices in itertools.combinations(range(4), 3)}
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
                          three_input_sum_sizes=[], root_op=None, evaluations=row['evaluations'],
                          worker_seconds=row['worker_seconds'], first_attempt_solved=row['attempts'][0]['solved'])
            if row['solved']:
                tree = Tree(tuple(row['attempts'][-1]['solver_tree']))
                prefixes = [tree.prefix[p:tree.ends[p]] for p in range(1, len(tree.prefix))]
                observed.update(prefixes)
                form_vectors = outputs([Tree(p).program for p in prefixes], bank['inputs'], 'v2_x4')
                own_triple = tuple(sorted({int(x) for x in cell['id'] if x.isdigit()}))
                census['three_input_sum_sizes'] = sorted({len(p) for p, v in zip(prefixes, form_vectors)
                                                         if v.astype('<i8').tobytes() == triple[own_triple]})
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


def envelopes(metas, bank, libs, frozen):
    by = {c['id']: c for c in bank['screen']['cells']}
    old = transport()['libraries.json'][:8]
    jobs = []
    for m in metas:
        allowed = bank['split']['source'] if m['cell'].startswith('S:') and m['arm'] == 'R-tree' else bank['split']['development']
        if m['arm'] not in ARMS or m['cell'] not in allowed or m['cell'] in bank['split']['protected']:
            raise ValueError('unapproved/protected search')
        donors = (None if m['arm'] == 'R-tree' else frozen['rect'] if m['arm'] == 'R-rect'
                  else [e['prefix'] for e in (libs[m['build']]['semantic'] if m['arm'] == 'R-all'
                                             else old[m['build']]['semantic_all'])])
        jobs.append((m, dict(id=m['cell'], labels=by[m['cell']]['labels']), bank['inputs'], frozen['cutoff'], donors))
    return jobs


def throughput(rows, elapsed, workers):
    worker = sum(r['worker_seconds'] for r in rows)
    return dict(wall_seconds=elapsed, worker_seconds=worker, workers=workers,
                effective_concurrency=worker / elapsed, jobs_per_second=len(rows) / elapsed,
                evaluations_per_wall_second=sum(r['evaluations'] for r in rows) / elapsed,
                max_worker_seconds=max(r['worker_seconds'] for r in rows),
                projected_384_jobs_seconds=384 * elapsed / len(rows))


def prepare(args, out, deadline):
    start = time.monotonic()
    bank = load_bank()
    frozen, schedule, audit = freeze(bank), schedules(bank, args.smoke), seed_audit(bank)
    for name, data in [('bank.json', bank), ('method_freeze.json', frozen), ('schedules.json', schedule), ('seed_audit.json', audit)]:
        write_json(out, name, data)
    rows, elapsed = base.run_batch(out, 'acquisition.jsonl', envelopes(schedule['source'], bank, None, frozen), args.workers, deadline)
    rows = base.validate_rows(rows, schedule['source'], bank)
    libs = libraries_from(rows, bank, 1 if args.smoke else 8)
    write_json(out, 'libraries.json', libs)
    p = dict(admitted=True, smoke=args.smoke, source_rows_hash=digest(rows), libraries_hash=digest(libs),
             bank_hash=digest(bank), freeze_hash=digest(frozen), schedule_hash=digest(schedule), audit_hash=digest(audit),
             source_batch_seconds=elapsed, throughput=throughput(rows, elapsed, args.workers), seconds=time.monotonic()-start,
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
    rows = base.validate_rows([json.loads(line) for line in (path / 'acquisition.jsonl').read_text().splitlines()], schedules(bank, smoke)['source'], bank)
    if (not p['admitted'] or p['smoke'] != smoke or digest(bank) != BANK_HASH
            or digest(frozen) != digest(freeze(load_bank())) or schedule != schedules(bank, smoke) or audit != seed_audit(bank)
            or p['preparation_hash'] != digest({k: v for k, v in p.items() if k != 'preparation_hash'})
            or any(p[k + '_hash'] != digest(v) for k, v in
                   [('source_rows', rows), ('libraries', libs), ('bank', bank), ('freeze', frozen), ('schedule', schedule), ('audit', audit)])):
        raise ValueError('preparation provenance/method mismatch')
    start = time.monotonic()
    rebuilt = libraries_from(rows, bank, 1 if smoke else 8)
    if deterministic(libs) != deterministic(rebuilt):
        raise ValueError('source-only reconstruction mismatch')
    return bank, frozen, libs, schedule, p, time.monotonic()-start


def investment(covered, own_fraction, rect_solves, rect_ratio, all_ratio, helpers_present):
    gates = dict(coverage=covered >= 24, supplied_prior=rect_solves >= 0.9 and rect_ratio <= 0.5, saving=all_ratio <= 0.67)
    reasons = []
    if not gates['coverage']:
        reasons.append('low observed acquisition under this source effort' if own_fraction < 0.25
                       else 'coverage shortfall, cause unresolved')
    if not gates['supplied_prior']:
        reasons.append('supplied-prior performance below the investment threshold')
    if gates['coverage'] and gates['supplied_prior'] and not gates['saving']:
        reasons.append('helpers available but insufficient observed saving')
    elif not gates['saving']:
        reasons.append('R-all saving below the investment threshold')
    return dict(gates=gates, recommendation='price protected confirmation' if all(gates.values()) else 'return to strategy; recommend ending this candidate at current allocation',
                reasons=reasons, mechanism_lead=all_ratio <= 0.67 and not helpers_present,
                scope='advisory investment criteria; descriptive development probe; no categorical absence or causal conclusion')


def summarize(rows, libs, bank, smoke=False):
    metas = schedules(bank, smoke)['score']
    rows = base.validate_rows(rows, metas, bank)
    builds = 1 if smoke else 8
    cells = list(bank_module.SEEN) if smoke else bank['split']['development']
    repeats = 1 if smoke else 2
    by = {(r['build'], r['cell'], r['repeat'], r['arm']): r for r in rows}
    arrays = {metric: {a: np.asarray([[[by[b, c, r, a][metric] for r in range(repeats)]
                                      for c in cells] for b in range(builds)], dtype=float)
                      for a in ARMS} for metric in ('evaluations', 'worker_seconds', 'solved')}
    for row in rows:
        if not row['solved'] and row['evaluations'] != 524288:
            raise ValueError('failure not charged full cap')
    selected = np.random.default_rng(BOOTSTRAP_SEED).integers(builds, size=(DRAWS, builds))
    blocks = {m: {a: v.mean(axis=(1, 2)) for a, v in aa.items()} for m, aa in arrays.items()}
    def ratio(a, denominator):
        result = {}
        for metric in ('evaluations', 'worker_seconds'):
            num, den = blocks[metric][a], blocks[metric][denominator]
            samples = num[selected].mean(1) / den[selected].mean(1)
            result[metric] = dict(point=float(num.mean()/den.mean()), interval95=np.quantile(samples, [0.025, 0.975]).tolist())
        logs = np.log(arrays['evaluations'][a]).mean((1, 2)) - np.log(arrays['evaluations'][denominator]).mean((1, 2))
        result['geometric_evaluations'] = dict(point=float(np.exp(logs.mean())), interval95=np.exp(np.quantile(logs[selected].mean(1), [0.025, 0.975])).tolist())
        return result
    contrasts = {a + '/R-tree': ratio(a, 'R-tree') for a in ARMS if a != 'R-tree'}
    contrasts['R-all/R-order-all'] = ratio('R-all', 'R-order-all')
    arms = {}
    for a in ARMS:
        rr = [r for r in rows if r['arm'] == a]
        arms[a] = dict(jobs=len(rr), solves=sum(r['solved'] for r in rr),
                       first_attempt_rate=sum(r['attempts'][0]['solved'] for r in rr)/len(rr),
                       capped_mean=float(arrays['evaluations'][a].mean()),
                       geometric_mean=float(np.exp(np.log(arrays['evaluations'][a]).mean())),
                       worker_seconds=sum(r['worker_seconds'] for r in rr),
                       mean_worker_seconds=float(arrays['worker_seconds'][a].mean()))
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
    census = [c for lib in libs for c in lib['census']]
    solves = sum(c['solved'] for c in census)
    own = sum(bool(c['own_helper_sizes']) for c in census)
    covered = sum(bool(c['present']) for c in coverage)
    historical = transport()['libraries.json'][:builds]
    economics = {}
    for metric in ('evaluations', 'worker_seconds'):
        acq = np.asarray([lib['acquisition_evaluations'] if metric == 'evaluations' else
                          lib['acquisition_worker_seconds'] + lib['extraction_census_seconds'] + lib['validation_census_seconds'] for lib in libs])
        economics[metric] = {}
        for denominator in ('R-tree', 'R-order-all'):
            saving = blocks[metric][denominator] - blocks[metric]['R-all']
            economics[metric][denominator] = dict(mean_acquisition=float(acq.mean()), mean_saving=float(saving.mean()),
                                                  repayment_searches=None if saving.mean() <= 0 else float(acq.mean()/saving.mean()))
    historical_cost = [dict(build=b, evaluations=lib['acquisition_evaluations'],
                            worker_seconds=lib['acquisition_worker_seconds'],
                            preparation_worker_seconds=sum(lib.get(k, 0) for k in ('extraction_census_seconds', 'all_extraction_census_seconds', 'validation_seconds')))
                       for b, lib in enumerate(historical)]
    return dict(arms=arms, contrasts=contrasts, bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='paired whole builds; ratio of pooled capped means; descriptive'),
                coverage=coverage, coverage_pairs=covered, acquisition=acquisition, source_census=census,
                source_solver_census=dict(jobs=len(census), solves=solves, own_helper=own, own_helper_fraction=own/solves if solves else 0,
                                          first_attempt_rate=sum(c['first_attempt_solved'] for c in census)/len(census) if census else None,
                                          capped_mean=float(np.mean([c['evaluations'] for c in census])) if census else None,
                                          median_evaluations=float(np.median([c['evaluations'] for c in census])) if census else None,
                                          three_input_sum=sum(bool(c['three_input_sum_sizes']) for c in census),
                                          root_ops={op: sum(c['root_op'] == op for c in census) for op in sorted({c['root_op'] for c in census if c['root_op'] is not None})}),
                per_cell=[dict(arm=a, cell=c, solves=sum(r['solved'] for r in rows if r['arm']==a and r['cell']==c),
                               worker_seconds=sum(r['worker_seconds'] for r in rows if r['arm']==a and r['cell']==c),
                               capped_mean=float(np.mean([r['evaluations'] for r in rows if r['arm']==a and r['cell']==c]))) for a in ARMS for c in cells],
                economics=economics, transported_historical_acquisition=historical_cost,
                decision=dict(recommendation='smoke_only_no_recommendation') if smoke else investment(
                    covered, own/solves if solves else 0, arms['R-rect']['solves']/arms['R-rect']['jobs'],
                    contrasts['R-rect/R-tree']['evaluations']['point'], contrasts['R-all/R-tree']['evaluations']['point'],
                    any(a['helpers'] for a in acquisition)),
                scope='Development roster; stage 0 preceded freeze; protected cells unsearched. No helper causality, absence, unlimited time-to-solution or general portability conclusion.')


def score(args, out, deadline):
    bank, frozen, libs, schedule, p, replay = load_prepared(Path(args.prepared), args.smoke)
    for name, data in [('bank.json', bank), ('method_freeze.json', frozen), ('libraries.json', libs), ('schedules.json', schedule)]:
        write_json(out, name, data)
    rows, elapsed = base.run_batch(out, 'score.jsonl', envelopes(schedule['score'], bank, libs, frozen), args.workers, deadline)
    report = summarize(rows, libs, bank, args.smoke)
    report.update(admitted=True, smoke=args.smoke, protected_searches=0, throughput=throughput(rows, elapsed, args.workers),
                  replay_validation_seconds=replay, preparation_hash=p['preparation_hash'], score_rows_hash=digest(base.validate_rows(rows, schedule['score'], bank)))
    plots(out, rows, libs)
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'score'))
    parser.add_argument('--workers', type=int, default=11)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--prepared')
    parser.add_argument('--seconds', type=int)
    args = parser.parse_args()
    limit = 870 if args.phase == 'prepare' else 2370
    seconds = args.seconds or limit
    if args.workers < 1 or seconds <= 0 or seconds > limit or (args.phase == 'score' and not args.prepared):
        parser.error('positive workers, approved phase limits, and --prepared for score required')
    if os.environ.get('RAYON_NUM_THREADS') != '1':
        parser.error('RAYON_NUM_THREADS=1 required for comparable worker costs')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + seconds
    try:
        (prepare if args.phase == 'prepare' else score)(args, out, deadline)
        if time.monotonic() > deadline:
            raise TimeoutError('fixed phase deadline exceeded during verification/report')
    except Exception as error:
        write_json(out, 'failure.json', dict(admitted=False, phase=args.phase, smoke=args.smoke, error=str(error)))
        raise


if __name__ == '__main__':
    main()
