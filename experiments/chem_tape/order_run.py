"""1129 bounded order-helper probe. Outputs only RUN_DIR; no protected search."""

import argparse
import gzip
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import order_bank as bank_module
from experiments.chem_tape import order_library
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_gp_search import GRAMMAR, Tree, search
from experiments.chem_tape.tree_hand_run import hand_prior, reviewed_methods
from experiments.chem_tape.tree_library import verify_entries

TASK = "2026-10-11-1129"
ARMS = ("R-tree", "R-sum", "R-order", "R-L", "R-S")


def seed(domain, cell, build, repeat, attempt):
    raw = json.dumps([TASK, domain, cell, build, repeat, attempt], separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], "big") & ((1 << 63) - 1)


def schedules(bank, smoke=False):
    count = 1 if smoke else 8
    return {phase: [dict(cell=c, arm=arm, build=b, repeat=r,
                         seeds=[seed(("smoke_" if smoke else "") + phase, c, b, r, k) for k in range(8)])
                    for c in bank['split']['source' if phase == 'source' else 'development']
                    for b in range(count) for r in range(2)
                    for arm in (("R-tree",) if phase == 'source' else ARMS)]
            for phase in ('source', 'score')}


def seed_audit(bank):
    historic = set(range(7000, 7800)) | set(range(9000, 9006))
    paths = []

    def collect(value, key=""):
        if isinstance(value, dict):
            for k, v in value.items():
                collect(v, k if 'seed' in k else key)
        elif isinstance(value, list):
            for v in value:
                collect(v, key)
        elif isinstance(value, int) and 'seed' in key:
            historic.add(value)

    for path in sorted(Path(__file__).with_name('data').rglob('*')):
        if path.is_file() and any(s in path.name for s in ('schedule', 'historical_seeds')) and path.suffix in ('.json', '.gz'):
            raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
            collect(json.loads(raw))
            paths.append(dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest()))
    published = {}
    for smoke in (False, True):
        for phase, metas in schedules(bank, smoke).items():
            uses = {}
            for m in metas:
                for k, s in enumerate(m['seeds']):
                    uses.setdefault(s, []).append((m, k))
            for records in uses.values():
                expected = {"R-tree"} if phase == 'source' else set(ARMS)
                if ({m['arm'] for m, _ in records} != expected or len(records) != len(expected)
                        or len({(m['cell'], m['build'], m['repeat'], k) for m, k in records}) != 1):
                    raise ValueError('unintended seed reuse')
            published[("smoke_" if smoke else "") + phase] = set(uses)
    for name, ss in published.items():
        if ss & historic:
            raise ValueError('historical seed collision: ' + name)
        for other, values in published.items():
            if other != name and ss & values:
                raise ValueError('phase seed collision')
    return dict(admitted=True, historical_count=len(historic), historic_hash=digest(sorted(historic)),
                historical_artifacts=paths, published_seed_sets={k: sorted(v) for k, v in published.items()})


def methods():
    reviewed_methods()  # unchanged engine, except the previously reviewed observer
    result = method_hashes()
    for name in ('order_bank.py', 'order_library.py', 'order_run.py', 'tree_library.py', 'tree_hand_run.py', 'tree_gp_validate.py', 'assembly_bank.py', 'independent_input_bank.py'):
        path = Path(__file__).with_name(name)
        result[str(path.relative_to(Path.cwd()))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def freeze(bank):
    return dict(task=TASK, bank_hash=digest(bank), methods=methods(), grammar=GRAMMAR,
                extractor=order_library.RECIPE, literal_recipe='tree_library.extract unchanged',
                cutoff=65536, attempts=8, population=256, crossover=0.5,
                donors='uniform library entries; unchanged engine half-library mutation draws',
                order=[list(bank_module.helper(kind, a, b).prefix) for kind in ('lo', 'hi')
                       for a in range(4) for b in range(a + 1, 4)],
                sum=hand_prior('v2_x4'))


def execute(envelope):
    meta, cell, inputs, cutoff, donor_prefixes = envelope
    donors = None if donor_prefixes is None else [Tree(tuple(p)) for p in donor_prefixes]
    start, attempts = time.monotonic(), []
    # Pass only id/labels: canonical programs and bank roles cannot seed search.
    for s in meta['seeds']:
        row = search((dict(id=cell['id'], labels=cell['labels']), s, cutoff, 256, inputs, 0.5), donor_library=donors)
        attempts.append(row)
        if row['solved']:
            break
    return meta | dict(solved=attempts[-1]['solved'], solver=attempts[-1]['solver'],
                       evaluations=sum(a['evaluations'] for a in attempts),
                       cap=8 * cutoff, cutoff=cutoff, pop_size=256,
                       worker_seconds=time.monotonic() - start, attempts=attempts)


def envelopes(metas, bank, libraries, frozen):
    by = {c['id']: c for c in bank['screen']['cells']}
    jobs = []
    for m in metas:
        allowed = bank['split']['source'] if m['arm'] == 'R-tree' and m['cell'].startswith('S:') else bank['split']['development']
        if m['cell'] not in allowed or m['cell'] in bank['split']['protected']:
            raise ValueError('unapproved/protected search requested')
        if m['arm'] == 'R-tree':
            prefixes = None
        elif m['arm'] == 'R-order':
            prefixes = frozen['order']
        elif m['arm'] == 'R-sum':
            prefixes = [e['prefix'] for e in frozen['sum']]
        else:
            name = 'literal' if m['arm'] == 'R-L' else 'semantic'
            prefixes = [e['prefix'] for e in libraries[m['build']][name]]
        jobs.append((m, by[m['cell']], bank['inputs'], frozen['cutoff'], prefixes))
    return jobs


def validate_rows(rows, metas, bank):
    def key(m):
        return (m['cell'], m['arm'], m['build'], m['repeat'])
    expected = {key(m): m for m in metas}
    if len(rows) != len(expected) or len({key(r) for r in rows}) != len(rows):
        raise ValueError('incomplete/duplicate rows')
    cells = {c['id']: c for c in bank['screen']['cells']}
    for row in rows:
        if key(row) not in expected or any(row[k] != v for k, v in expected[key(row)].items()):
            raise ValueError('row/schedule disagreement')
        attempts = row['attempts']
        if not 1 <= len(attempts) <= 8 or (not row['solved'] and len(attempts) != 8):
            raise ValueError('restart count mismatch')
        if row['evaluations'] != sum(a['evaluations'] for a in attempts) or row['solved'] != attempts[-1]['solved']:
            raise ValueError('restart accounting mismatch')
        for k, attempt in enumerate(attempts):
            if attempt['seed'] != row['seeds'][k] or not 256 <= attempt['evaluations'] <= 65536:
                raise ValueError('attempt budget/seed mismatch')
            if attempt['solved'] != (k == len(attempts) - 1 and row['solved']):
                raise ValueError('continued after solve')
            if attempt['solved']:
                from experiments.chem_tape.composition_search import outputs
                tree = Tree(tuple(attempt['solver_tree']))
                if (list(tree.program) != attempt['solver'] or len(tree.program) > 32
                        or outputs([tree.program], bank['inputs'], 'v2_x4')[0].tolist() != cells[row['cell']]['labels']):
                    raise ValueError('invalid exact solver')
    return sorted(rows, key=key)


def run_batch(out, name, jobs, workers, deadline):
    rows = []
    started = time.monotonic()
    with (out / name).open('w') as file:
        def save(row):
            file.write(json.dumps(row, allow_nan=False) + '\n')
            file.flush()
            rows.append(row)
            if len(rows) % 12 == 0:
                print(name, len(rows), '/', len(jobs), 'wall', round(time.monotonic()-started, 1), flush=True)
        pool = mp.get_context('spawn').Pool(workers)
        try:
            complete = run_jobs(pool, execute, jobs, deadline, save)
            if not complete:
                raise TimeoutError('fixed phase deadline exceeded; partial rows preserved')
            pool.close()
        finally:
            pool.terminate()
            pool.join()
    return rows, time.monotonic() - started


def deterministic_libraries(libraries):
    return [{k: v for k, v in lib.items() if k not in ('literal_seconds', 'extraction_census_seconds')}
            for lib in libraries]


def libraries_from(rows, bank, builds):
    libraries = []
    by = {c['id']: c for c in bank['screen']['cells']}
    for b in range(builds):
        lib = order_library.build([r for r in rows if r['build'] == b], bank['split']['source'], bank['inputs'])
        for row in lib['census']:
            own = by[row['cell']]['helpers'][0]
            row['own_helper'], row['own_helper_sizes'] = own, row['helpers'][own]
        libraries.append(lib)
    return libraries


def prepare(args, out, deadline):
    start = time.monotonic()
    if args.bank:
        if not args.smoke:
            raise ValueError('prebuilt bank is smoke-only; full prepare screens independently')
        bank = json.loads(Path(args.bank).read_text())
        bank_module.verify(bank['screen']['cells'])
    else:
        bank = bank_module.build(deadline)
    write_json(out, 'bank.json', bank)
    if not bank['admitted']:
        raise ValueError('bank infeasible: ' + bank['failure'])
    frozen = freeze(bank)
    verify_entries(frozen['sum'], bank['inputs'])
    verify_entries([dict(prefix=p, nodes=len(p), compiled_length=len(Tree(tuple(p)).program))
                    for p in frozen['order']], bank['inputs'])
    schedule = schedules(bank, args.smoke)
    audit = seed_audit(bank)
    for name, data in [('method_freeze.json', frozen), ('schedules.json', schedule), ('seed_audit.json', audit)]:
        write_json(out, name, data)
    rows, elapsed = run_batch(out, 'acquisition.jsonl', envelopes(schedule['source'], bank, None, frozen), args.workers, deadline)
    rows = validate_rows(rows, schedule['source'], bank)
    libraries = libraries_from(rows, bank, 1 if args.smoke else 8)
    write_json(out, 'libraries.json', libraries)
    preparation = dict(admitted=True, smoke=args.smoke, source_rows_hash=digest(rows),
                       libraries_hash=digest(libraries), bank_hash=digest(bank),
                       freeze_hash=digest(frozen), schedule_hash=digest(schedule), audit_hash=digest(audit),
                       source_batch_seconds=elapsed, source_worker_seconds=sum(r['worker_seconds'] for r in rows),
                       bank_seconds=bank['seconds'], seconds=time.monotonic() - start,
                       source_jobs=len(rows), source_solves=sum(r['solved'] for r in rows),
                       protected_searches=0, workers=args.workers,
                       git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip())
    if time.monotonic() > deadline:
        raise TimeoutError('preparation verification exceeded fixed deadline')
    preparation['preparation_hash'] = digest(preparation)
    write_json(out, 'preparation.json', preparation)
    print('prepared', preparation, flush=True)


def load_prepared(path, smoke):
    if (path / 'failure.json').exists():
        raise ValueError('preparation has a recorded phase failure')
    def read(name):
        return json.loads((path / name).read_text())
    bank, frozen, libs, schedule, preparation, audit = [read(name) for name in ('bank.json', 'method_freeze.json', 'libraries.json', 'schedules.json', 'preparation.json', 'seed_audit.json')]
    rows = [json.loads(line) for line in (path / 'acquisition.jsonl').read_text().splitlines()]
    rows = validate_rows(rows, schedules(bank, smoke)['source'], bank)
    if (not preparation['admitted'] or preparation['smoke'] != smoke
            or preparation['preparation_hash'] != digest({k: v for k, v in preparation.items() if k != 'preparation_hash'})
            or preparation['source_rows_hash'] != digest(rows)
            or preparation['libraries_hash'] != digest(libs)
            or preparation['bank_hash'] != digest(bank)
            or preparation['freeze_hash'] != digest(frozen)
            or preparation['schedule_hash'] != digest(schedule)
            or preparation['audit_hash'] != digest(audit)
            or schedule != schedules(bank, smoke) or digest(frozen) != digest(freeze(bank)) or audit != seed_audit(bank)):
        raise ValueError('preparation provenance/method mismatch')
    rebuilt = libraries_from(rows, bank, 1 if smoke else 8)
    if deterministic_libraries(rebuilt) != deterministic_libraries(libs):
        raise ValueError('same-source library reconstruction mismatch')
    for lib in libs:
        for kind in ('literal', 'semantic'):
            verify_entries(lib[kind], bank['inputs'])
    return bank, frozen, libs, schedule, preparation


def score(args, out, deadline):
    bank, frozen, libs, schedule, preparation = load_prepared(Path(args.prepared), args.smoke)
    for name, data in [('bank.json', bank), ('method_freeze.json', frozen), ('libraries.json', libs), ('schedules.json', schedule)]:
        write_json(out, name, data)
    rows, elapsed = run_batch(out, 'score.jsonl', envelopes(schedule['score'], bank, libs, frozen), args.workers, deadline)
    rows = validate_rows(rows, schedule['score'], bank)
    report = summarize(rows, libs, bank)
    report.update(admitted=True, smoke=args.smoke, protected_searches=0,
                  score_batch_seconds=elapsed, workers=args.workers,
                  preparation_hash=preparation['preparation_hash'], score_rows_hash=digest(rows))
    write_json(out, 'report.json', report)
    plots(out, rows, libs)
    print('scored', len(rows), 'wall', elapsed, 'arms', report['arms'], flush=True)


def summarize(rows, libs, bank):
    summaries = {}
    for arm in ARMS:
        rr = [r for r in rows if r['arm'] == arm]
        costs = np.asarray([r['evaluations'] for r in rr])
        build_logs = [np.mean([np.log(r['evaluations']) for r in rr if r['build'] == b]) for b in sorted({r['build'] for r in rr})]
        summaries[arm] = dict(jobs=len(rr), capped_mean=float(costs.mean()), geometric_mean=float(np.exp(np.log(costs).mean())),
                              solves=sum(r['solved'] for r in rr), first_attempt_rate=sum(r['attempts'][0]['solved'] for r in rr)/len(rr),
                              worker_seconds=sum(r['worker_seconds'] for r in rr),
                              between_build_sd_log_cost=float(np.std(build_logs, ddof=1)) if len(build_logs) > 1 else None)
    gap = np.log(summaries['R-tree']['geometric_mean'] / summaries['R-order']['geometric_mean'])
    for arm in ARMS:
        summaries[arm]['log_gap_recovered'] = float(np.log(summaries['R-tree']['geometric_mean'] / summaries[arm]['geometric_mean']) / gap) if gap > 0 else None
    needed = {h for c in bank['screen']['cells'] if c['id'] in bank['split']['development'] for h in c['helpers']}
    acquisition = []
    for b, lib in enumerate(libs):
        included = {arm: [h for h, d in lib['helper_diagnostics'].items() if
                          (d['semantic']['included'] if arm == 'R-S' else any(x['included'] for x in d['literal']))]
                    for arm in ('R-L', 'R-S')}
        acquisition.append(dict(build=b, helpers=included,
                                destination_needed={arm: sorted(set(hs) & needed) for arm, hs in included.items()},
                                evaluations=lib['acquisition_evaluations'], worker_seconds=lib['acquisition_worker_seconds'],
                                census_extraction_seconds=lib['extraction_census_seconds'],
                                source_jobs=lib['source_jobs'], source_solves=lib['source_solves']))
    counts = {arm: sum(bool(a['destination_needed'][arm]) for a in acquisition) for arm in ('R-L', 'R-S')}
    price = [arm for arm in counts if counts[arm] >= 6 and summaries[arm]['log_gap_recovered'] is not None and summaries[arm]['log_gap_recovered'] >= 0.5]
    return dict(arms=summaries, acquisition=acquisition, helper_build_counts=counts,
                descriptive_recommendation='price protected proposal' if price else 'return located or unresolved limit to strategy',
                qualifying_arms=price, qualification='development probe only; no mechanism confirmation or practical-advantage claim',
                own_helper_census=sum(bool(c['own_helper_sizes']) for lib in libs for c in lib['census']),
                source_solvers=sum(lib['source_solves'] for lib in libs), source_jobs=sum(lib['source_jobs'] for lib in libs))


def plots(out, rows, libraries):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for arm in ARMS:
        rr = [r for r in rows if r['arm'] == arm]
        costs = sorted(r['evaluations'] for r in rr if r['solved'])
        axes[0].step(costs, np.arange(1, len(costs)+1)/len(rr), where='post', label=arm)
        axes[1].bar(arm, np.exp(np.mean([np.log(r['evaluations']) for r in rr])))
    axes[0].set(xscale='log', xlabel='Primitive evaluations', ylabel='Solved fraction')
    axes[0].legend(fontsize=8)
    axes[1].set(yscale='log', ylabel='Geometric capped cost')
    axes[2].bar(range(len(libraries)), [sum(d['semantic']['included'] for d in lib['helper_diagnostics'].values()) for lib in libraries])
    axes[2].set(xlabel='Acquisition build', ylabel='R-S helper entries')
    fig.tight_layout()
    fig.savefig(out / 'probe.png', dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'score'))
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--bank')
    parser.add_argument('--prepared')
    parser.add_argument('--seconds', type=int)
    args = parser.parse_args()
    if args.workers < 1 or (args.phase == 'score' and not args.prepared):
        parser.error('positive workers and --prepared for score required')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    phase_limit = 1170 if args.phase == 'prepare' else 1770
    seconds = args.seconds or phase_limit
    if seconds <= 0 or (not args.smoke and seconds > phase_limit):
        parser.error('full phases must fit the approved 20/30-minute timeouts')
    deadline = time.monotonic() + seconds
    try:
        (prepare if args.phase == 'prepare' else score)(args, out, deadline)
        if time.monotonic() > deadline:
            raise TimeoutError('fixed phase deadline exceeded during verification/reporting')
    except Exception as error:
        write_json(out, 'failure.json', dict(admitted=False, error=str(error), phase=args.phase, smoke=args.smoke))
        raise


if __name__ == '__main__':
    main()
