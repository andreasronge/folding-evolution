"""1530 frozen 1228 R-all libraries on the complete protected order roster.

Preparation searches development cells only. Repeat barriers and fsynced rows
permit a balanced repeat-zero fallback; partial blocks never enter inference.
"""

import argparse
import hashlib
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
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_library import verify_entries
from experiments.chem_tape.tree_gp_search import Tree

TASK = '2026-10-11-1530'
ARMS = ('R-tree', 'R-all', 'R-order')
BOOTSTRAP_SEED = 202610111530
DRAWS = 8192
CAP = 524288
# The two opt-in extensions leave default search/extraction replay unchanged.
EXTENSIONS = {
    'experiments/chem_tape/tree_gp_search.py': '61598ff06dc7edcf3b0f25f05b195fae9007f01597708f426fd43194f97c3e5e',
    'experiments/chem_tape/order_library.py': '1e9a6402d2559e05f866cbce98694ebcd6f499f3376449c513ea5f3c82cb30e2',
}
SAVED_FILES = ('bank.json', 'method_freeze.json', 'libraries.json', 'schedules.json',
               'preparation.json', 'seed_audit.json', 'acquisition.jsonl')


def seed(domain, cell, build, repeat, attempt):
    raw = json.dumps([TASK, domain, cell, build, repeat, attempt], separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1 << 63) - 1)


def schedules(bank, smoke=False):
    cells = bank['split']['development' if smoke else 'protected']
    return [dict(build=b, cell=c, repeat=r, arm=a,
                 seeds=[seed('smoke_score' if smoke else 'score', c, b, r, k) for k in range(8)])
            for r in range(2) for b in range(1 if smoke else 24) for c in cells for a in ARMS]


def seed_audit(bank, artifacts):
    historical = set(range(7000, 7800)) | set(range(9000, 9006))
    audits = [base.seed_audit(bank), saved.seed_audit(bank), archive.audit_seeds(bank, artifacts)]
    for audit in audits:
        for values in audit['published_seed_sets'].values():
            historical.update(values)
    # archive's historical hash incorporates older raw seed artifacts, checked
    # again here so new seeds are compared against those values, not just hashes.
    import gzip
    def collect(obj, key=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                collect(v, k if 'seed' in k else key)
        elif isinstance(obj, list):
            for v in obj:
                collect(v, key)
        elif isinstance(obj, int) and 'seed' in key:
            historical.add(obj)
    collect(artifacts['schedules'])
    collect(artifacts['seed_audit'])
    for artifact in audits[0]['historical_artifacts']:
        path = Path(artifact['path'])
        raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != artifact['sha256']:
            raise ValueError('historical seed artifact changed')
        collect(json.loads(raw))
    published, seen = {}, set(historical)
    for smoke in (False, True):
        uses = {}
        for m in schedules(bank, smoke):
            for k, s in enumerate(m['seeds']):
                uses.setdefault(s, []).append((m, k))
        for records in uses.values():
            if (len(records) != 3 or {m['arm'] for m, _ in records} != set(ARMS)
                    or len({(m['build'], m['cell'], m['repeat'], k) for m, k in records}) != 1):
                raise ValueError('unintended seed reuse')
        values = set(uses)
        if values & seen:
            raise ValueError('historical/full/smoke seed collision')
        seen.update(values)
        published['smoke_score' if smoke else 'score'] = sorted(values)
    return dict(admitted=True, historical_count=len(historical), historical_hash=digest(sorted(historical)),
                prior_audit_hashes=[digest(a) for a in audits], published_seed_sets=published,
                pairing='across three arms only; independent builds/cells/repeats/attempts')


def freeze(bank, artifacts):
    current, old = method_hashes(), artifacts['method_freeze']['methods']
    # Pin every production Python and Rust source, and all experiment modules
    # actually used by the engine, verifier, bank or extractor. Other drivers
    # may have changed since 1228 without affecting this experiment.
    modules = ('tree_gp_search.py', 'tree_library.py', 'order_library.py', 'order_bank.py',
               'order_run.py', 'order_cap_run.py', 'composition_search.py', 'composition_run.py',
               'independent_input_bank.py', 'assembly_bank.py', 'tree_gp_validate.py')
    for path, expected in old.items():
        if path.startswith(('src/', 'rust/src/')) or path in ['experiments/chem_tape/' + n for n in modules]:
            if current.get(path) != EXTENSIONS.get(path, expected):
                raise ValueError('1228 method drift: ' + path)
    original = artifacts['method_freeze']
    if (original['task'] != saved.TASK or original['bank_hash'] != saved.BANK_HASH
            or original['cutoff'] != 65536 or original['attempts'] != 8
            or original['population'] != 256 or original['crossover'] != 0.5
            or original['extractor_all'] != saved.order_library.RECIPE | dict(cap=None)):
        raise ValueError('saved method parameters differ')
    prior = original['order']
    verify_entries([dict(prefix=p, nodes=len(p), compiled_length=len(Tree(tuple(p)).program))
                    for p in prior], bank['inputs'])
    if len(prior) != 12 or sum(c['disjoint'] for c in bank['screen']['cells']
                              if c['id'] in bank['split']['protected']) != 4:
        raise ValueError('wrong supplied prior or protected strata')
    return dict(task=TASK, bank_hash=digest(bank), methods=current,
                saved_preparation_hash=archive.SAVED_HASH,
                saved_libraries_hash=archive.LIBRARIES_HASH,
                saved_method_hash=digest(original), grammar=original['grammar'],
                extractor_all=original['extractor_all'], cutoff=65536, attempts=8,
                population=256, crossover=0.5, order=prior,
                donors=original['donors'], arms=list(ARMS), builds=24, repeats=2,
                protected_cells=bank['split']['protected'], schedule=schedules(bank),
                smoke_schedule=schedules(bank, True),
                bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='whole paired builds; cells fixed'),
                decision=dict(precedence=['lower > 0.67: end', 'upper < 0.80 and reliability: useful',
                                          'otherwise: unresolved'],
                              extra_unsolved_full=12, extra_unsolved_repeat_zero=6),
                fallback='complete balanced repeat zero only; otherwise incomplete with no verdict',
                acquisition_cost='historical source failures + both extractions/census + validation',
                scope='held-out combinations of a development bank; no fresh-bank transfer')


def envelopes(metas, bank, libs, frozen, smoke=False):
    allowed = bank['split']['development' if smoke else 'protected']
    by = {c['id']: c for c in bank['screen']['cells']}
    jobs = []
    for m in metas:
        if (m['cell'] not in allowed or m['arm'] not in ARMS
                or not 0 <= m['build'] < (1 if smoke else 24)):
            raise ValueError('unapproved cell/arm/build')
        donors = (None if m['arm'] == 'R-tree' else frozen['order'] if m['arm'] == 'R-order'
                  else [e['prefix'] for e in libs[m['build']]['semantic_all']])
        # Neither canonical witnesses, helper labels nor disjoint annotations
        # are passed to search or used to choose donors.
        c = by[m['cell']]
        jobs.append((m, dict(id=c['id'], labels=c['labels']), bank['inputs'], frozen['cutoff'], donors))
    return jobs


def validate_rows(rows, metas, bank):
    rows = base.validate_rows(rows, metas, bank)
    for row in rows:
        if (row['cap'] != CAP or row['cutoff'] != 65536 or row['pop_size'] != 256
                or not 256 <= row['evaluations'] <= CAP or row['evaluations'] % 256
                or (not row['solved'] and row['evaluations'] != CAP)
                or not np.isfinite(row['worker_seconds']) or row['worker_seconds'] <= 0):
            raise ValueError('invalid capped cost/parameters/timing')
    return rows


def coverage(bank, libs):
    by = {c['id']: c for c in bank['screen']['cells']}
    result = []
    for b, lib in enumerate(libs):
        included = {h for h, d in lib['all_helper_diagnostics'].items() if d['semantic']['included']}
        for c in bank['split']['protected']:
            needed = by[c]['helpers']
            result.append(dict(build=b, cell=c, needed_helpers=needed,
                               present=sorted(included & set(needed)),
                               needed_helpers_present=len(included & set(needed))))
    return result


def run_blocks(out, name, bank, libs, frozen, workers, deadline, smoke=False):
    """No repeat-one job is submitted until all repeat-zero rows validate."""
    schedule = schedules(bank, smoke)
    rows, completed = [], []
    started = time.monotonic()
    with (out / name).open('w') as file:
        def save(row):
            file.write(json.dumps(row, allow_nan=False) + '\n')
            file.flush()
            os.fsync(file.fileno())
            rows.append(row)
            if len(rows) % 60 == 0:
                print(name, len(rows), '/', len(schedule), 'wall', round(time.monotonic()-started, 1), flush=True)
        pool = mp.get_context('spawn').Pool(workers)
        try:
            for repeat in range(2):
                metas = [m for m in schedule if m['repeat'] == repeat]
                jobs = envelopes(metas, bank, libs, frozen, smoke)
                if not run_jobs(pool, base.execute, jobs, deadline, save):
                    break
                block = validate_rows([r for r in rows if r['repeat'] == repeat], metas, bank)
                completed.append(repeat)
                # Marker follows row fsync and exact-grid/cap/solver validation.
                write_json(out, name.replace('.jsonl', '_completion.json'), dict(
                    completed_repeats=completed, row_hashes={str(r): digest(validate_rows(
                        [x for x in rows if x['repeat'] == r],
                        [m for m in schedule if m['repeat'] == r], bank)) for r in completed},
                    rows=len(rows), last_block_rows=len(block)))
            pool.close()
        finally:
            pool.terminate()
            pool.join()
    return rows, completed, time.monotonic() - started


def balanced_rows(rows, bank, smoke=False):
    """Accept a full grid, or a full first block; never finished-fast jobs."""
    # Reject unknown keys, duplicate rows, altered seeds/caps even in a partial
    # repeat-one block. Completed attempts are validated independently of balance.
    schedule = schedules(bank, smoke)
    by_meta = {(m['build'], m['cell'], m['repeat'], m['arm']): m for m in schedule}
    keys = [(r['build'], r['cell'], r['repeat'], r['arm']) for r in rows]
    if len(set(keys)) != len(keys) or not set(keys) <= set(by_meta):
        raise ValueError('duplicate/unknown score keys')
    validate_rows(rows, [by_meta[k] for k in keys], bank)
    if len(rows) == len(schedule):
        return validate_rows(rows, schedule, bank), 2
    first = [r for r in rows if r['repeat'] == 0]
    first_metas = [m for m in schedule if m['repeat'] == 0]
    if len(first) == len(first_metas):
        return validate_rows(first, first_metas, bank), 1
    if any(r['repeat'] == 1 for r in rows):
        raise ValueError('repeat one started before balanced repeat zero')
    return [], 0


def classify(interval, extra_unsolved, units):
    low, high = interval
    if low > 0.67:
        return 'end_expansion_worthwhile_one_third_saving_excluded'
    if high < 0.80 and extra_unsolved <= units / 96:
        return 'useful_held_out_saving_return_to_strategy'
    return 'unresolved_return_to_strategy_price_resolution'


def summarize(rows, libs, bank, smoke=False):
    selected_rows, repeats = balanced_rows(rows, bank, smoke)
    if not repeats:
        return dict(admitted=False, complete=False, analyzed_repeats=0, decision='incomplete_no_efficacy_verdict',
                    completed_jobs=len(rows), expected_jobs=len(schedules(bank, smoke)))
    cells = bank['split']['development' if smoke else 'protected']
    builds = 1 if smoke else 24
    by = {(r['build'], r['cell'], r['repeat'], r['arm']): r for r in selected_rows}
    arrays = {metric: {a: np.asarray([[[by[b, c, r, a][metric] for r in range(repeats)]
                                      for c in cells] for b in range(builds)], dtype=float)
                      for a in ARMS} for metric in ('evaluations', 'worker_seconds', 'solved')}
    selected = np.random.default_rng(BOOTSTRAP_SEED).integers(builds, size=(DRAWS, builds))
    blocks = {m: {a: v.mean(axis=(1, 2)) for a, v in aa.items()} for m, aa in arrays.items()}
    def contrasts(indices):
        result = {}
        for denominator in ('R-tree', 'R-order'):
            contrast = {}
            for metric in ('evaluations', 'worker_seconds'):
                num = arrays[metric]['R-all'][:, indices, :].mean(axis=(1, 2))
                den = arrays[metric][denominator][:, indices, :].mean(axis=(1, 2))
                contrast[metric] = saved.estimate(num.mean()/den.mean(), num[selected].mean(1)/den[selected].mean(1))
            logs = (np.log(arrays['evaluations']['R-all'][:, indices, :]) -
                    np.log(arrays['evaluations'][denominator][:, indices, :])).mean(axis=(1, 2))
            contrast['geometric_evaluations'] = saved.estimate(np.exp(logs.mean()), np.exp(logs[selected].mean(1)))
            diff = (arrays['solved']['R-all'][:, indices, :] -
                    arrays['solved'][denominator][:, indices, :]).mean(axis=(1, 2))
            contrast['solve_fraction_difference'] = saved.estimate(diff.mean(), diff[selected].mean(1))
            result['R-all/' + denominator] = contrast
        return result
    primary_contrasts = contrasts(list(range(len(cells))))
    arms = {}
    tree_log = np.log(arrays['evaluations']['R-tree']).mean()
    gap = tree_log - np.log(arrays['evaluations']['R-order']).mean()
    for a in ARMS:
        rr = [r for r in selected_rows if r['arm'] == a]
        operators = [p['operator'] for r in rr for p in r['attempts']]
        arms[a] = dict(jobs=len(rr), solves=sum(r['solved'] for r in rr),
                       capped_mean=float(arrays['evaluations'][a].mean()),
                       geometric_mean=float(np.exp(np.log(arrays['evaluations'][a]).mean())),
                       mean_worker_seconds=float(arrays['worker_seconds'][a].mean()),
                       worker_seconds=sum(r['worker_seconds'] for r in rr),
                       log_gap_recovered=None if gap <= 0 else float((tree_log - np.log(arrays['evaluations'][a]).mean())/gap),
                       operators={k: sum(p.get(k, 0) for p in operators) for k in sorted({k for p in operators for k in p})})
    extra = (arms['R-tree']['solves'] - arms['R-all']['solves'])
    units = builds * len(cells) * repeats
    def subset(indices):
        return dict(paired_units=builds*len(indices)*repeats, contrasts=contrasts(indices), arms={a: dict(
            solves=int(arrays['solved'][a][:, indices, :].sum()),
            jobs=builds*len(indices)*repeats,
            capped_mean=float(arrays['evaluations'][a][:, indices, :].mean())) for a in ARMS})
    cell_meta = {c['id']: c for c in bank['screen']['cells']}
    strata = {name: subset([i for i, c in enumerate(cells) if cell_meta[c]['disjoint'] == disjoint])
              for name, disjoint in [('disjoint', True), ('overlapping', False)]}
    economics = {}
    used_libs = libs[:builds]
    for metric in ('evaluations', 'worker_seconds'):
        acq = np.array([lib['acquisition_evaluations'] if metric == 'evaluations' else
                        lib['acquisition_worker_seconds'] + sum(lib[k] for k in saved.TIMINGS if k != 'literal_seconds')
                        for lib in used_libs])
        saving = blocks[metric]['R-tree'] - blocks[metric]['R-all']
        boot_rate = saving[selected].mean(1)/acq[selected].mean(1)
        lo, hi = np.quantile(boot_rate, [0.025, 0.975])
        economics[metric] = dict(mean_acquisition=float(acq.mean()), mean_saving=float(saving.mean()),
                                 repayment_searches=None if saving.mean() <= 0 else float(acq.mean()/saving.mean()),
                                 repayment_interval95=[None if hi <= 0 else float(1/hi), None if lo <= 0 else float(1/lo)],
                                 repayment_unbounded=bool(lo <= 0))
    primary = primary_contrasts['R-all/R-tree']['evaluations']
    return dict(admitted=True, complete=repeats == 2, analyzed_repeats=repeats,
                analyzed_jobs=len(selected_rows), ignored_partial_jobs=len(rows)-len(selected_rows),
                paired_units=units, arms=arms, contrasts=primary_contrasts,
                primary='R-all/R-tree pooled capped arithmetic mean evaluations',
                decision='smoke_only_no_decision' if smoke else classify(primary['interval95'], extra, units),
                reliability=dict(extra_unsolved=extra, allowance=units/96, allowance_rate=1/96,
                                 passed=extra <= units/96),
                smaller_saving_supported=primary['interval95'][1] < 1,
                bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='whole paired builds; all cells fixed'),
                per_cell_descriptive={c: subset([i]) for i, c in enumerate(cells)},
                strata_descriptive=strata, coverage=coverage(bank, used_libs),
                acquisition=[dict(build=b, evaluations=lib['acquisition_evaluations'],
                                  worker_seconds=lib['acquisition_worker_seconds'],
                                  source_jobs=lib['source_jobs'], source_solves=lib['source_solves'],
                                  library_size=len(lib['semantic_all']), timing={k: lib[k] for k in saved.TIMINGS})
                             for b, lib in enumerate(used_libs)],
                economics_against_R_tree=economics,
                economics_scope='historical source failures + extraction/census/validation; replay cost separate; no repayment claimed against R-order',
                scope='held-out combinations of a development bank; no fresh-bank transfer, helper causality or inherited acquisition')


def prepare(args, out, deadline):
    started = time.monotonic()
    # Copy all historical evidence under RUN_DIR, so scoring never depends on
    # changing external artifacts. The archive loader checks recorded identities
    # and reconstructs all 24 libraries from their own complete source grids.
    source = Path(args.saved)
    copied = out / 'saved'
    copied.mkdir()
    if (source / 'failure.json').exists():
        raise ValueError('saved acquisition has recorded failure')
    for name in SAVED_FILES:
        shutil.copyfile(source / name, copied / name)
    bank, libs, artifacts = archive.load_saved(copied)
    frozen, audit = freeze(bank, artifacts), seed_audit(bank, artifacts)
    values = dict(bank=bank, libraries=libs, method_freeze=frozen,
                  schedules=dict(score=schedules(bank), smoke_score=schedules(bank, True)),
                  seed_audit=audit, coverage=coverage(bank, libs))
    for name, value in values.items():
        write_json(out, name + '.json', value)
    rows, completed, elapsed = run_blocks(out, 'smoke.jsonl', bank, libs, frozen, args.workers, deadline-30, True)
    if completed != [0, 1]:
        raise TimeoutError('development smoke incomplete')
    report = summarize(rows, libs, bank, True)
    report.update(score_batch_seconds=elapsed)
    write_json(out, 'smoke_report.json', report)
    plot(out, rows, libs, 'smoke_dynamics.png')
    p = dict(admitted=True, task=TASK, artifact_hashes={k: digest(v) for k, v in values.items()},
             saved_preparation_hash=archive.SAVED_HASH, smoke_rows_hash=digest(validate_rows(rows, schedules(bank, True), bank)),
             protected_searches=0, workers=args.workers, seconds=time.monotonic()-started,
             git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip())
    if time.monotonic() > deadline:
        raise TimeoutError('preparation deadline exceeded')
    p['preparation_hash'] = digest(p)
    write_json(out, 'preparation.json', p)
    print('prepared', p, flush=True)


def load_prepared(path):
    started = time.monotonic()
    if (path / 'failure.json').exists():
        raise ValueError('preparation has recorded failure')
    bank, libs, artifacts = archive.load_saved(path / 'saved')
    expected = dict(bank=bank, libraries=libs, method_freeze=freeze(bank, artifacts),
                    schedules=dict(score=schedules(bank), smoke_score=schedules(bank, True)),
                    seed_audit=seed_audit(bank, artifacts), coverage=coverage(bank, libs))
    p = json.loads((path / 'preparation.json').read_text())
    if (not p['admitted'] or p['task'] != TASK or p['saved_preparation_hash'] != archive.SAVED_HASH
            or p['preparation_hash'] != digest({k: v for k, v in p.items() if k != 'preparation_hash'})):
        raise ValueError('preparation identity mismatch')
    for name, value in expected.items():
        actual = json.loads((path / (name + '.json')).read_text())
        if actual != value or p['artifact_hashes'][name] != digest(actual):
            raise ValueError('preparation provenance/method mismatch: ' + name)
    smoke_rows = [json.loads(line) for line in (path / 'smoke.jsonl').read_text().splitlines()]
    if p['smoke_rows_hash'] != digest(validate_rows(smoke_rows, schedules(bank, True), bank)):
        raise ValueError('preparation smoke mismatch')
    return bank, libs, expected, p, time.monotonic()-started


def plot(out, rows, libs, filename='dynamics.png'):
    # Reuse existing dynamics visualization, temporarily exposing only the
    # actually scored arms through a local implementation rather than globals.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(17, 4))
    xs = [256, 4096, 16384, 65536, 131072, 262144, CAP]
    for a in ARMS:
        rr = [r for r in rows if r['arm'] == a]
        axes[0].plot(xs, [np.mean([r['solved'] and r['evaluations'] <= x for r in rr]) for x in xs], label=a)
        for panel, field in [(1, 'curve'), (2, 'phenotype_diversity_curve')]:
            timelines = []
            for row in rr:
                line, offset = [], 0
                for attempt in row['attempts']:
                    line.extend((offset + p[0], p[1]) for p in attempt[field])
                    offset += attempt['evaluations']
                timelines.append(line)
            axes[panel].plot(xs, [np.mean([([v for t, v in line if t <= x] or [line[0][1]])[-1]
                                          for line in timelines]) for x in xs], label=a)
    for i, title in enumerate(('D625 solves', 'Training best score; restart resets', 'Training output diversity')):
        axes[i].set(xscale='log', xlabel='Evaluations', title=title)
        axes[i].legend(fontsize=7)
    axes[3].plot([len(lib['semantic_all']) for lib in libs], label='Frozen R-all')
    axes[3].set(xlabel='Build', ylabel='Library classes')
    axes[3].legend()
    fig.tight_layout()
    fig.savefig(out / filename, dpi=140)
    plt.close(fig)


def score(args, out, deadline):
    bank, libs, values, p, replay_seconds = load_prepared(Path(args.prepared))
    for name, value in values.items():
        write_json(out, name + '.json', value)
    rows, completed, elapsed = run_blocks(out, 'score.jsonl', bank, libs, values['method_freeze'],
                                         args.workers, deadline-30, args.smoke)
    report = summarize(rows, libs, bank, args.smoke)
    balanced, _ = balanced_rows(rows, bank, args.smoke)
    report.update(smoke=args.smoke, workers=args.workers, completed_repeats=completed,
                  protected_searches=0 if args.smoke else len(rows), score_batch_seconds=elapsed,
                  replay_validation_seconds=replay_seconds, preparation_hash=p['preparation_hash'],
                  score_rows_hash=digest(rows), analyzed_rows_hash=digest(balanced))
    write_json(out, 'report.json', report)
    if balanced:
        plot(out, balanced, libs)
    # An internal timeout returns a report (including a balanced fallback or
    # incomplete/no-verdict) normally so the driver can analyze it. External
    # termination still leaves fsynced rows and block completion markers.
    print('scored', len(rows), 'wall', elapsed, 'decision', report['decision'], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'score'))
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--saved', default=archive.DEFAULT_SAVED)
    parser.add_argument('--prepared')
    parser.add_argument('--smoke', action='store_true', help='score development smoke only')
    parser.add_argument('--seconds', type=int)
    args = parser.parse_args()
    limit = 1470 if args.phase == 'prepare' else 5370
    seconds = limit if args.seconds is None else args.seconds
    if (args.workers < 1 or not 30 < seconds <= limit or
            (args.phase == 'score' and not args.prepared) or (args.phase == 'prepare' and args.smoke)):
        parser.error('positive workers, approved deadline, --prepared for score; --smoke is score-only')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if any((out / name).exists() for name in ('failure.json', 'preparation.json', 'report.json', 'score.jsonl', 'saved')):
        parser.error('RUN_DIR contains previous experiment artifacts')
    deadline = time.monotonic() + seconds
    try:
        (prepare if args.phase == 'prepare' else score)(args, out, deadline)
    except Exception as error:
        write_json(out, 'failure.json', dict(admitted=False, phase=args.phase, error=str(error)))
        raise


if __name__ == '__main__':
    main()
