"""1427 standing variation and aggregate frozen readout; development cells only."""

import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import order_cap_run as saved, order_run as base
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.tree_gp_search import Tree, search
from experiments.chem_tape.tree_library import controls, verify_entries

TASK = '2026-10-11-1427'
EXPOSURE_ARMS = ('L', 'S', 'Z', 'N')
READOUT_ARMS = ('R-tree', 'initial', 'L-final', 'S-final', 'R-all')
LIBRARIES_HASH = '375c7b69544131cbea5683fd77bcc13e6299353ed6394eba4c90f17f759010d5'
SAVED_HASH = 'b7d6dd5939758e8f97c3c171ffb70dcbd2438bab8ef707b095dfb0fda9a82c5a'
DEFAULT_SAVED = '/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1228-prepare'
BOOTSTRAP_SEED = 202610111427
DRAWS = 8192


def seed(domain, *identity):
    raw = json.dumps([TASK, domain, *identity], separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1 << 63) - 1)


def load_saved(path):
    """Validate immutable acquisition, without asking the changed engine to be 1228."""
    path = Path(path)
    if (path / 'failure.json').exists():
        raise ValueError('saved acquisition has a failure')
    artifacts = {n: json.loads((path / (n + '.json')).read_text()) for n in
                 ('bank', 'method_freeze', 'libraries', 'schedules', 'preparation', 'seed_audit')}
    p = artifacts['preparation']
    if (not p['admitted'] or p['smoke'] or p['preparation_hash'] != SAVED_HASH
            or digest({k: v for k, v in p.items() if k != 'preparation_hash'}) != SAVED_HASH):
        raise ValueError('saved preparation identity mismatch')
    for name, key in [('bank', 'bank'), ('method_freeze', 'freeze'), ('libraries', 'libraries'),
                      ('schedules', 'schedule'), ('seed_audit', 'audit')]:
        if digest(artifacts[name]) != p[key + '_hash']:
            raise ValueError('saved artifact hash mismatch: ' + name)
    bank = saved.load_bank()
    if artifacts['bank'] != bank:
        raise ValueError('saved bank differs from immutable development roster')
    rows = base.validate_rows([json.loads(line) for line in (path / 'acquisition.jsonl').read_text().splitlines()],
                              saved.schedules(bank)['source'], bank)
    if digest(rows) != p['source_rows_hash'] or len(artifacts['libraries']) != 24:
        raise ValueError('saved corpus mismatch')
    rebuilt = saved.libraries_from(rows, bank, 24)
    if saved.deterministic(rebuilt) != saved.deterministic(artifacts['libraries']):
        raise ValueError('saved source-only library reconstruction mismatch')
    return bank, artifacts['libraries'], artifacts


def schedules(bank, smoke=False):
    cells = bank['split']['development']
    exposure = []
    for b in range(1 if smoke else 24):
        for arm in EXPOSURE_ARMS:
            for r in range(1 if smoke else (2 if arm == 'N' else 4)):
                rotation = (b + r) % 6
                sequence = cells[rotation:] + cells[:rotation]
                domain = 'smoke-' if smoke else ''
                exposure.append(dict(build=b, arm=arm, repeat=r, cells=sequence * 2,
                                     assignment_seed=seed(domain + 'assignment', b, r),
                                     program_seeds=[seed(domain + 'program', b, r, e) for e in range(12)],
                                     shuffle_seeds=[seed(domain + 'shuffle', b, r, e) for e in range(12)]))
    readout = [dict(build=b, cell=c, repeat=r, arm=a,
                    seeds=[seed(('smoke-' if smoke else '') + 'readout', b, c, r, k) for k in range(8)])
               for b in range(1 if smoke else 24) for c in cells
               for r in range(2) for a in READOUT_ARMS]
    return dict(exposure=exposure, readout=readout,
                null_seeds=[seed('null', b) for b in range(24)])


def audit_seeds(bank, artifacts):
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
    collect(artifacts['schedules'])
    collect(artifacts['seed_audit'])
    for values in saved.seed_audit(bank)['published_seed_sets'].values():
        historical.update(values)
    # Include the earlier audit's raw historical sets as well as its 1228 sets.
    earlier = base.seed_audit(bank)
    for values in earlier['published_seed_sets'].values():
        historical.update(values)
    import gzip
    for artifact in earlier['historical_artifacts']:
        path = Path(artifact['path'])
        raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != artifact['sha256']:
            raise ValueError('historical artifact changed')
        collect(json.loads(raw))
    historical.update(range(7000, 7800))
    historical.update(range(9000, 9006))
    groups = {}
    for smoke in (False, True):
        sc = schedules(bank, smoke)
        prefix = 'smoke-' if smoke else ''
        for field in ('assignment_seed', 'program_seeds', 'shuffle_seeds'):
            vals = {v for m in sc['exposure'] for v in
                    ([m[field]] if isinstance(m[field], int) else m[field])}
            groups[prefix + field] = vals
        groups[prefix + 'readout'] = {s for m in sc['readout'] for s in m['seeds']}
    groups['null'] = set(schedules(bank)['null_seeds'])
    seen = set(historical)
    for name, vals in groups.items():
        if vals & seen:
            raise ValueError('seed namespace collision: ' + name)
        seen.update(vals)
    # Pairing is intentional across arms, never across builds/repeats/episodes.
    if len(groups['program_seeds']) != 24 * 4 * 12 or len(groups['readout']) != 24 * 6 * 2 * 8:
        raise ValueError('unintended seed duplication')
    return dict(admitted=True, historical_count=len(historical), historical_hash=digest(sorted(historical)),
                published_seed_sets={k: sorted(v) for k, v in groups.items()},
                pairing='program, assignment, shuffle paired across arms; readout across all five laws')


def methods():
    paths = ('inherited_library_run.py', 'tree_gp_search.py', 'tree_library.py', 'order_library.py',
             'order_cap_run.py', 'order_run.py', 'composition_search.py', 'order_bank.py')
    result = {str(Path(__file__).with_name(n).relative_to(Path.cwd())):
              hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in paths}
    from experiments.chem_tape.independent_input_run import method_hashes
    result.update(method_hashes())
    return result


def freeze(bank):
    return dict(task=TASK, bank_hash=digest(bank), saved_preparation_hash=SAVED_HASH, methods=methods(),
                exposure=dict(builds=24, repeats=dict(L=4, S=4, Z=4, N=2), initial_carriers=64,
                              population=256, episodes=12, evaluated_generations=64,
                              transitions_per_episode=63, crossover=0.5, elites=2,
                              inheritance='recipient including revert; elite aligned', bit_mutation=0,
                              initialization='programs reset independent of bits; slots retained',
                              shuffle='before selection every transition, including elite selection'),
                readout=dict(arms=READOUT_ARMS, repeats=2, attempts=8, cutoff=65536,
                             initial_probability=0.125, fixed_all_probability=0.5,
                             extraction='0.5 times mean final f of all four trajectories per build'),
                bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='whole library builds'),
                scope='descriptive development probe; externally acquired fixed content; no protected searches')


def execute_exposure(job):
    meta, cells, inputs, prefixes, generations = job
    rng = np.random.default_rng(meta['assignment_seed'])
    bits = np.zeros(256, dtype=np.int8)
    bits[rng.choice(256, 64, replace=False)] = 1
    donors = None if meta['arm'] == 'N' else [Tree(tuple(p)) for p in prefixes]
    episodes = []
    start = time.monotonic()
    for e, c in enumerate(meta['cells']):
        initial_f = float(bits.mean())
        row = search((cells[c], meta['program_seeds'][e], generations * 256, 256, inputs, 0.5),
                     donor_library=donors, modifier_bits=bits,
                     modifier_seed=meta['shuffle_seeds'][e], shuffle_modifiers=meta['arm'] == 'S',
                     continue_after_solve=True)
        bits = np.array(row.pop('modifier_bits'), dtype=np.int8)
        trace = row['modifier_trace']
        first = row['first_solve_evaluations']
        solve_g = None if first is None else first // 256 - 1
        solve_f = None if solve_g is None else trace[solve_g]['census_f']
        row.update(episode=e, initial_f=initial_f, final_f=float(bits.mean()),
                   pre_solve_delta=float(bits.mean()) - initial_f if solve_f is None else solve_f - initial_f,
                   post_solve_delta=None if solve_f is None else float(bits.mean()) - solve_f)
        episodes.append(row)
    return meta | dict(episodes=episodes, final_f=float(bits.mean()), final_bits=bits.tolist(),
                       worker_seconds=time.monotonic() - start)


def execute_readout(job):
    meta, cell, inputs, prefixes, probability, cutoff = job
    donors = None if probability == 0 else [Tree(tuple(p)) for p in prefixes]
    start, attempts = time.monotonic(), []
    for s in meta['seeds']:
        row = search((cell, s, cutoff, 256, inputs, 0.5), donor_library=donors,
                     library_probability=probability)
        attempts.append(row)
        if row['solved']:
            break
    return meta | dict(probability=probability, solved=attempts[-1]['solved'], solver=attempts[-1]['solver'],
                       evaluations=sum(a['evaluations'] for a in attempts), cap=8*cutoff, cutoff=cutoff,
                       pop_size=256, worker_seconds=time.monotonic() - start, attempts=attempts)


def batch(out, name, jobs, fn, workers, deadline):
    rows, start = [], time.monotonic()
    with (out / name).open('w') as file:
        def save(row):
            file.write(json.dumps(row, allow_nan=False) + '\n')
            file.flush()
            rows.append(row)
            if len(rows) % 12 == 0:
                print(name, len(rows), '/', len(jobs), 'wall', round(time.monotonic()-start, 1), flush=True)
        pool = mp.get_context('spawn').Pool(workers)
        try:
            if not run_jobs(pool, fn, jobs, deadline, save):
                raise TimeoutError('fixed deadline exceeded; partial rows preserved')
        finally:
            pool.terminate()
            pool.join()
    return rows, time.monotonic()-start


def key(row):
    return row['build'], row['arm'], row['repeat']


def validate_exposure(rows, schedule, bank, generations=64, initial_frequency=0.25):
    expected = {key(m): m for m in schedule}
    if len(rows) != len(expected) or {key(r) for r in rows} != set(expected):
        raise ValueError('incomplete/duplicate exposure grid')
    for row in rows:
        if any(row[k] != v for k, v in expected[key(row)].items()) or len(row['episodes']) != 12:
            raise ValueError('exposure metadata/episode mismatch')
        if (len(row['final_bits']) != 256 or not np.isin(row['final_bits'], [0, 1]).all()
                or row['final_f'] != np.mean(row['final_bits'])):
            raise ValueError('final bit accounting mismatch')
        prior = initial_frequency
        for e, ep in enumerate(row['episodes']):
            if (ep['cell'] != row['cells'][e] or ep['seed'] != row['program_seeds'][e]
                    or ep['generations'] != generations or ep['evaluations'] != 256*generations
                    or ep['initial_f'] != prior or len(ep['modifier_trace']) != generations):
                raise ValueError('exposure budget/seed/census mismatch')
            trace = ep['modifier_trace']
            if trace[0]['census_f'] != prior or trace[-1]['next_f'] != ep['final_f']:
                raise ValueError('trace endpoint mismatch')
            for g, t in enumerate(trace):
                if t['generation'] != g or (g and t['census_f'] != trace[g-1]['next_f']):
                    raise ValueError('trace continuity mismatch')
                if t['counters'] is not None:
                    cc = t['counters']
                    if (sum(c['recipients'] for c in cc) != 254
                            or t.get('post_mutation_f', t['recipient_f']) != cc[1]['recipients']/254):
                        raise ValueError('recipient accounting mismatch')
                    if cc[0]['library_draws'] or (row['arm'] == 'N' and cc[1]['library_draws']):
                        raise ValueError('bit-independent law invoked a library')
                    for c in cc:
                        if (c['crossover'] + c['mutation'] != c['recipients']
                                or c['library_draws'] + c['ordinary_donors'] != c['mutation']
                                or c['library_insertions'] + c['rejected_library'] != c['library_draws']
                                or c['ordinary_insertions'] + c['rejected_ordinary'] != c['ordinary_donors']):
                            raise ValueError('operator accounting mismatch')
            if ep['solved']:
                tree = Tree(tuple(ep['solver_tree']))
                from experiments.chem_tape.composition_search import outputs
                labels = next(c['labels'] for c in bank['screen']['cells'] if c['id'] == ep['cell'])
                if list(tree.program) != ep['solver'] or outputs([tree.program], bank['inputs'], 'v2_x4')[0].tolist() != labels:
                    raise ValueError('invalid first exact witness')
                if not 256 <= ep['first_solve_evaluations'] <= generations*256:
                    raise ValueError('first solve accounting mismatch')
            prior = ep['final_f']
    return sorted(rows, key=key)


def probabilities(rows, builds):
    return [dict(zip(READOUT_ARMS, [0.0, 0.125,
                0.5*np.mean([r['final_f'] for r in rows if r['build'] == b and r['arm'] == 'L']),
                0.5*np.mean([r['final_f'] for r in rows if r['build'] == b and r['arm'] == 'S']), 0.5]))
            for b in range(builds)]


def exposure(args, out, deadline):
    start = time.monotonic()
    bank, libs, artifacts = load_saved(args.saved)
    schedule, frozen, audit = schedules(bank, args.smoke), freeze(bank), audit_seeds(bank, artifacts)
    nulls = []
    for b, lib in enumerate(libs):
        entries, seconds = controls(lib['semantic_all'], schedule['null_seeds'][b])
        verify_entries(entries, bank['inputs'])
        nulls.append(dict(build=b, seed=schedule['null_seeds'][b], entries=entries, seconds=seconds))
    for name, value in [('bank', bank), ('libraries', libs), ('nulls', nulls), ('schedules', schedule),
                        ('method_freeze', frozen), ('seed_audit', audit)]:
        write_json(out, name + '.json', value)
    cells = {c['id']: dict(id=c['id'], labels=c['labels']) for c in bank['screen']['cells']
             if c['id'] in bank['split']['development']}
    jobs = [(m, cells, bank['inputs'], [e['prefix'] for e in
             (nulls[m['build']]['entries'] if m['arm'] == 'Z' else libs[m['build']]['semantic_all'])], 64)
            for m in schedule['exposure']]
    rows, elapsed = batch(out, 'exposure.jsonl', jobs, execute_exposure, args.workers, deadline)
    rows = validate_exposure(rows, schedule['exposure'], bank)
    probs = probabilities(rows, 1 if args.smoke else 24)
    manifest = dict(admitted=True, smoke=args.smoke, protected_searches=0, workers=args.workers,
                    seconds=time.monotonic()-start, exposure_batch_seconds=elapsed,
                    git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
                    saved_preparation_hash=SAVED_HASH, exposure_rows_hash=digest(rows), probabilities=probs,
                    artifacts={n: digest(v) for n, v in [('bank', bank), ('libraries', libs), ('nulls', nulls),
                               ('schedules', schedule), ('method_freeze', frozen), ('seed_audit', audit)]})
    manifest['manifest_hash'] = digest(manifest)
    write_json(out, 'exposure_manifest.json', manifest)
    print('exposure complete', len(rows), 'wall', elapsed, flush=True)


def load_exposure(path, smoke):
    path = Path(path)
    if (path / 'failure.json').exists():
        raise ValueError('exposure stage failed')
    manifest = json.loads((path / 'exposure_manifest.json').read_text())
    if (not manifest['admitted'] or manifest['smoke'] != smoke or
            manifest['manifest_hash'] != digest({k: v for k, v in manifest.items() if k != 'manifest_hash'})):
        raise ValueError('exposure manifest mismatch')
    artifacts = {n: json.loads((path / (n + '.json')).read_text()) for n in manifest['artifacts']}
    if manifest['saved_preparation_hash'] != SAVED_HASH or digest(artifacts['libraries']) != LIBRARIES_HASH:
        raise ValueError('exposure does not use the saved 1228 libraries')
    if any(digest(artifacts[n]) != h for n, h in manifest['artifacts'].items()):
        raise ValueError('exposure artifact mismatch')
    bank = saved.load_bank()
    if artifacts['bank'] != bank or digest(artifacts['method_freeze']) != digest(freeze(bank)) or artifacts['schedules'] != schedules(bank, smoke):
        raise ValueError('bank/method/schedule changed since exposure')
    expected_audit = audit_seeds(bank, dict(schedules=saved.schedules(bank), seed_audit=saved.seed_audit(bank)))
    if artifacts['seed_audit'] != expected_audit:
        raise ValueError('exposure seed audit changed')
    if len(artifacts['nulls']) != 24:
        raise ValueError('incomplete size-null cohort')
    for b, null in enumerate(artifacts['nulls']):
        expected, _ = controls(artifacts['libraries'][b]['semantic_all'], seed('null', b))
        if null['build'] != b or null['seed'] != seed('null', b) or null['entries'] != expected:
            raise ValueError('size-null reconstruction mismatch')
    rows = validate_exposure([json.loads(line) for line in (path / 'exposure.jsonl').read_text().splitlines()],
                             artifacts['schedules']['exposure'], bank)
    probs = probabilities(rows, 1 if smoke else 24)
    if digest(rows) != manifest['exposure_rows_hash'] or probs != manifest['probabilities']:
        raise ValueError('endpoint extraction mismatch')
    return bank, artifacts, rows, manifest


def estimate(point, draws):
    return dict(point=float(point), interval95=np.quantile(draws, [0.025, 0.975]).tolist())


def summarize(exposure_rows, scores, bank, smoke):
    builds = 1 if smoke else 24
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    selected = rng.integers(builds, size=(DRAWS, builds))
    final = {a: np.array([np.mean([r['final_f'] for r in exposure_rows if r['build'] == b and r['arm'] == a])
                         for b in range(builds)]) for a in EXPOSURE_ARMS}
    contrasts = {a: estimate((final['L']-final[a]).mean(), (final['L']-final[a])[selected].mean(1))
                 for a in ('S', 'Z')}
    neutral = estimate(final['N'].mean(), final['N'][selected].mean(1))
    costs = {metric: {a: np.array([np.mean([r[metric] for r in scores if r['build'] == b and r['arm'] == a])
                                  for b in range(builds)]) for a in READOUT_ARMS}
             for metric in ('evaluations', 'worker_seconds', 'solved')}
    ratios = {}
    for num, den in [('initial', 'R-all'), ('L-final', 'initial'), ('L-final', 'S-final'), ('L-final', 'R-all')]:
        ratios[num+'/'+den] = {m: estimate(costs[m][num].mean()/costs[m][den].mean(),
                                          costs[m][num][selected].mean(1)/costs[m][den][selected].mean(1))
                               for m in ('evaluations', 'worker_seconds')}
    operators = {}
    for a in EXPOSURE_ARMS:
        operators[a] = {phase: {str(s): {} for s in range(2)} for phase in ('pre', 'post')}
        for row in (r for r in exposure_rows if r['arm'] == a):
            for ep in row['episodes']:
                for t in ep['modifier_trace']:
                    if t['counters'] is None:
                        continue
                    for s, cc in enumerate(t['counters']):
                        target = operators[a][t['phase']][str(s)]
                        for k, v in cc.items():
                            target[k] = target.get(k, 0) + v
        for phase in operators[a].values():
            for cc in phase.values():
                cc['library_rejection_fraction'] = cc.get('rejected_library', 0)/cc['library_draws'] if cc.get('library_draws') else None
                cc['ordinary_rejection_fraction'] = cc.get('rejected_ordinary', 0)/cc['ordinary_donors'] if cc.get('ordinary_donors') else None
    thresholds = dict(a=contrasts['S']['point'] >= 0.15 and contrasts['S']['interval95'][0] > 0,
                      b=contrasts['Z']['point'] >= 0.10,
                      c=ratios['initial/R-all']['evaluations']['point'] >= 1.25)
    per_cell = {c: {a: dict(jobs=len(rr), solves=sum(r['solved'] for r in rr),
                           capped_mean=float(np.mean([r['evaluations'] for r in rr])))
                   for a in READOUT_ARMS
                   for rr in [[r for r in scores if r['cell'] == c and r['arm'] == a]]}
                for c in bank['split']['development']}
    for cell in per_cell.values():
        cell['ratios'] = {n+'/'+d: cell[n]['capped_mean']/cell[d]['capped_mean']
                          for n, d in [('L-final', 'initial'), ('L-final', 'S-final')]}
    return dict(smoke=smoke, protected_searches=0, probe=True,
                final_by_build={a: f.tolist() for a, f in final.items()}, L_minus=contrasts, neutral=neutral,
                neutral_diagnostic_alarm=not neutral['interval95'][0] <= 0.25 <= neutral['interval95'][1],
                advisory_thresholds=thresholds, advisory_all_pass=all(thresholds.values()) and not smoke,
                readout_ratios=ratios, per_cell=per_cell, operators_by_state_and_solve_phase=operators,
                arms={a: dict(jobs=sum(r['arm'] == a for r in scores),
                              solves=sum(r['solved'] for r in scores if r['arm'] == a),
                              capped_mean=float(costs['evaluations'][a].mean()),
                              mean_worker_seconds=float(costs['worker_seconds'][a].mean())) for a in READOUT_ARMS},
                exposure={a: dict(trajectories=len(rr), fixation=sum(r['final_f'] == 1 for r in rr),
                                  loss=sum(r['final_f'] == 0 for r in rr),
                                  worker_seconds=sum(r['worker_seconds'] for r in rr),
                                  pre_solve_delta_mean=float(np.mean([e['pre_solve_delta'] for r in rr for e in r['episodes']])),
                                  post_solve_delta_mean=None if not post else float(np.mean(post)))
                          for a in EXPOSURE_ARMS for rr in [[r for r in exposure_rows if r['arm'] == a]]
                          for post in [[e['post_solve_delta'] for r in rr for e in r['episodes'] if e['post_solve_delta'] is not None]]},
                bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS, unit='whole paired library builds'),
                interpretation='Descriptive observations; thresholds advisory. Size control does not isolate robustness. Neutral alarm is diagnostic. Broad uncertainty is not absence. Inspect frozen usefulness before confirmation.',
                scope='Six development cells; fixed externally acquired content; aggregate deployment law from mean endpoint; no transfer or single-population deployment claim')


def plots(out, exposure_rows, scores):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for a in EXPOSURE_ARMS:
        rr = [r for r in exposure_rows if r['arm'] == a]
        paths = [[t['census_f'] for e in r['episodes'] for t in e['modifier_trace']] for r in rr]
        axes[0].plot(np.mean(paths, axis=0), label=a)
        axes[1].plot(np.mean([[t['diversity'] for e in r['episodes'] for t in e['modifier_trace']] for r in rr], axis=0), label=a)
    axes[0].set(xlabel='Evaluated generation (episode resets every 64)', ylabel='Carrier frequency')
    axes[1].set(xlabel='Evaluated generation', ylabel='Training correctness diversity')
    for ax in axes[:2]:
        ax.legend()
    axes[2].bar(READOUT_ARMS, [np.mean([r['evaluations'] for r in scores if r['arm'] == a]) for a in READOUT_ARMS])
    axes[2].set(ylabel='Fresh capped mean evaluations')
    axes[2].tick_params(axis='x', rotation=25)
    fig.tight_layout()
    fig.savefig(out / 'dynamics.png', dpi=140)
    plt.close(fig)


def readout(args, out, deadline):
    bank, artifacts, exposure_rows, manifest = load_exposure(args.exposure, args.smoke)
    for n, value in artifacts.items():
        write_json(out, n + '.json', value)
    write_json(out, 'exposure_manifest.json', manifest)
    by = {c['id']: dict(id=c['id'], labels=c['labels']) for c in bank['screen']['cells']}
    metas = artifacts['schedules']['readout']
    jobs = [(m, by[m['cell']], bank['inputs'], [e['prefix'] for e in artifacts['libraries'][m['build']]['semantic_all']],
             manifest['probabilities'][m['build']][m['arm']], 65536) for m in metas]
    rows, elapsed = batch(out, 'score.jsonl', jobs, execute_readout, args.workers, deadline)
    rows = base.validate_rows(rows, metas, bank)
    for r in rows:
        if r['probability'] != manifest['probabilities'][r['build']][r['arm']] or (not r['solved'] and r['evaluations'] != 524288):
            raise ValueError('readout probability/failure cap mismatch')
    report = summarize(exposure_rows, rows, bank, args.smoke)
    report.update(admitted=True, score_rows_hash=digest(rows), exposure_manifest_hash=manifest['manifest_hash'],
                  score_batch_seconds=elapsed, workers=args.workers,
                  historical_acquisition=[dict(build=b, evaluations=lib['acquisition_evaluations'],
                                                worker_seconds=lib['acquisition_worker_seconds'])
                                          for b, lib in enumerate(artifacts['libraries'])])
    plots(out, exposure_rows, rows)
    write_json(out, 'report.json', report)
    print('readout complete', len(rows), 'wall', elapsed, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=('exposure', 'readout'))
    p.add_argument('--saved', default=DEFAULT_SAVED)
    p.add_argument('--exposure')
    p.add_argument('--workers', type=int, default=10)
    p.add_argument('--seconds', type=int)
    p.add_argument('--smoke', action='store_true')
    args = p.parse_args()
    limit = 1470 if args.phase == 'exposure' else 1770
    seconds = limit if args.seconds is None else args.seconds
    if args.workers < 1 or not 0 < seconds <= limit or (args.phase == 'readout' and not args.exposure):
        p.error('positive workers, approved deadline and --exposure for readout required')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if any((out / n).exists() for n in ('failure.json', 'exposure.jsonl', 'score.jsonl', 'exposure_manifest.json', 'report.json', 'method_freeze.json')):
        p.error('RUN_DIR contains previous experiment artifacts')
    deadline = time.monotonic() + seconds
    try:
        (exposure if args.phase == 'exposure' else readout)(args, out, deadline)
        if time.monotonic() > deadline:
            raise TimeoutError('fixed phase deadline exceeded during validation/reporting')
    except Exception as error:
        write_json(out, 'failure.json', dict(admitted=False, phase=args.phase, smoke=args.smoke, error=str(error)))
        raise


if __name__ == '__main__':
    main()
