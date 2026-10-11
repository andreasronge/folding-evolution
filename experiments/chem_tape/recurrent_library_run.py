"""1736 recurrent inherited operator choice; separate deployment of every endpoint.

Reuses 1427's immutable library replay, batch executor, search and exact-witness
checks. No acquisition, frequency pooling, protected search or efficacy tuning.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import inherited_library_run as old
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.tree_gp_search import Tree, search

TASK = '2026-10-11-1736'
EXPOSURE_ARMS = ('L', 'S', 'N')
READOUT_ARMS = ('initial', 'R-all', 'L-final', 'S-final', 'N-final')
DRAWS = 8192
INITIAL_F = 1/16
MUTATION = 1/32


def seed(domain, *identity):
    raw = json.dumps([TASK, domain, *identity], separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1 << 63)-1)


def schedules(bank, smoke=False):
    cells = bank['split']['development']
    prefix = 'smoke-' if smoke else ''
    builds, populations = (1, 1) if smoke else (24, 6)
    exposure = []
    for b in range(builds):
        for a in EXPOSURE_ARMS:
            for p in range(populations):
                rotation = (b+p) % 6
                sequence = cells[rotation:] + cells[:rotation]
                exposure.append(dict(build=b, arm=a, repeat=p, cells=sequence*2,
                    assignment_seed=seed(prefix+'assignment', b, p),
                    program_seeds=[seed(prefix+'program', b, p, e) for e in range(12)],
                    modifier_seeds=[seed(prefix+'modifier', b, p, e) for e in range(12)]))
    readout = [dict(build=b, cell=c, repeat=2*p+r, population=p, scoring_repeat=r, arm=a,
                   seeds=[seed(prefix+'readout', b, p, c, r, k) for k in range(8)])
               for b in range(builds) for c in cells for p in range(populations)
               for r in range(2) for a in READOUT_ARMS]
    return dict(exposure=exposure, readout=readout)


def audit_seeds(bank, artifacts):
    previous = old.audit_seeds(bank, artifacts)
    # The previous audit contains both prior historical seeds and 1427 namespaces.
    # Its construction already proves the 1427 namespaces disjoint from history.
    historical = {v for values in previous['published_seed_sets'].values() for v in values}
    def collect(obj, field=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                collect(v, k if 'seed' in k else field)
        elif isinstance(obj, list):
            for v in obj:
                collect(v, field)
        elif isinstance(obj, int) and 'seed' in field:
            historical.add(obj)
    collect(artifacts['schedules'])
    collect(artifacts['seed_audit'])
    for audit in (old.saved.seed_audit(bank), old.base.seed_audit(bank)):
        collect(audit)
    # Include raw historical artifacts checked by the previous audit.
    import gzip
    for artifact in old.base.seed_audit(bank)['historical_artifacts']:
        path = Path(artifact['path'])
        raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != artifact['sha256']:
            raise ValueError('historical artifact changed')
        collect(json.loads(raw))
    historical.update(range(7000, 7800))
    historical.update(range(9000, 9006))
    historical.add(old.BOOTSTRAP_SEED)
    groups = {}
    for smoke in (False, True):
        sc = schedules(bank, smoke)
        prefix = 'smoke-' if smoke else ''
        for f in ('assignment_seed', 'program_seeds', 'modifier_seeds'):
            groups[prefix+f] = {v for m in sc['exposure'] for v in
                               ([m[f]] if isinstance(m[f], int) else m[f])}
        groups[prefix+'readout'] = {v for m in sc['readout'] for v in m['seeds']}
    groups['bootstrap'] = {seed('bootstrap')}
    groups['precision'] = {seed('precision')}
    seen = set(historical)
    for name, values in groups.items():
        if values & seen:
            raise ValueError('seed namespace collision: '+name)
        seen.update(values)
    expected = dict(assignment_seed=24*6, program_seeds=24*6*12,
                    modifier_seeds=24*6*12, readout=24*6*6*2*8)
    if any(len(groups[k]) != n for k, n in expected.items()):
        raise ValueError('unintended seed duplication')
    return dict(admitted=True, task=TASK, historical_count=len(historical),
                historical_hash=digest(sorted(historical)),
                prior_audit_hash=digest(previous),
                published_seed_sets={k: sorted(v) for k, v in groups.items()},
                pairing='exposure across L/S/N; readout across five laws within population seed block')


def freeze(bank):
    methods = old.methods()
    methods[str(Path(__file__).relative_to(Path.cwd()))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return dict(task=TASK, bank_hash=digest(bank), saved_preparation_hash=old.SAVED_HASH,
        libraries_hash=old.LIBRARIES_HASH, methods=methods,
        exposure=dict(builds=24, repeats={a: 6 for a in EXPOSURE_ARMS}, population=256,
                      initial_carriers=16, episodes=12, evaluated_generations=64,
                      transitions_per_episode=63, crossover=0.5, elites=2,
                      bit_redraw_probability=MUTATION, redraw_carrier_probability=INITIAL_F,
                      inheritance='recipient then redraw before variation; retain child bit on rejection; aligned elites',
                      initialization='independent program resets, bit slots persist',
                      shuffle='before selection on every transition including elite selection'),
        readout=dict(arms=READOUT_ARMS, population_seed_blocks=6, repeats_per_cell=2,
                     attempts=8, cutoff=65536, initial_probability=1/32, fixed_all_probability=0.5,
                     extraction='each population separately: q=0.5*final_f; same library for all arms'),
        bootstrap=dict(seed=seed('bootstrap'), draws=DRAWS,
                       unit='paired libraries, populations nested; matching shared reference blocks attached'),
        scope='fixed external content, six development cells; mechanism/boundary test, no transfer')


def execute_exposure(job):
    meta, cells, inputs, prefixes, generations = job
    bits = np.zeros(256, dtype=np.int8)
    bits[np.random.default_rng(meta['assignment_seed']).choice(256, 16, replace=False)] = 1
    donors = None if meta['arm'] == 'N' else [Tree(tuple(p)) for p in prefixes]
    episodes = []
    start = time.monotonic()
    for e, c in enumerate(meta['cells']):
        initial_f = float(bits.mean())
        row = search((cells[c], meta['program_seeds'][e], generations*256, 256, inputs, 0.5),
                     donor_library=donors, modifier_bits=bits,
                     modifier_seed=meta['modifier_seeds'][e], shuffle_modifiers=meta['arm'] == 'S',
                     modifier_mutation_probability=MUTATION, modifier_redraw_probability=INITIAL_F,
                     continue_after_solve=True)
        bits = np.array(row.pop('modifier_bits'), dtype=np.int8)
        first = row['first_solve_evaluations']
        solve_g = None if first is None else first//256-1
        solve_f = None if solve_g is None else row['modifier_trace'][solve_g]['census_f']
        row.update(episode=e, initial_f=initial_f, final_f=float(bits.mean()),
                   pre_solve_delta=float(bits.mean())-initial_f if solve_f is None else solve_f-initial_f,
                   post_solve_delta=None if solve_f is None else float(bits.mean())-solve_f)
        episodes.append(row)
    return meta | dict(episodes=episodes, final_f=float(bits.mean()), final_bits=bits.tolist(),
                       worker_seconds=time.monotonic()-start)


def validate_exposure(rows, schedule, bank, generations=64):
    expected = {old.key(m): m for m in schedule}
    if (len(rows) != len(expected) or len({old.key(r) for r in rows}) != len(rows)
            or {old.key(r) for r in rows} != set(expected)):
        raise ValueError('incomplete/duplicate exposure grid')
    # The shared validator covers budgets, continuity, operators and exact witnesses.
    for row in rows:
        if any(row[k] != v for k, v in expected[old.key(row)].items()):
            raise ValueError('exposure metadata mismatch')
        prior = INITIAL_F
        for ep in row['episodes']:
            if ep['initial_f'] != prior:
                raise ValueError('episode bit persistence mismatch')
            for t in ep['modifier_trace']:
                if t['counters'] is None:
                    continue
                tr = np.asarray(t['modifier_transitions'])
                cc = t['counters']
                if (tr.shape != (2, 2) or np.any(tr < 0) or np.any(tr != tr.astype(int))
                        or tr.sum() != 254 or tr[1].sum()/254 != t['recipient_f']
                        or t['recipient_f'] != t['pre_mutation_f']
                        or tr[:, 1].sum()/254 != t['post_mutation_f']
                        or any(tr[:, s].sum() != cc[s]['recipients'] for s in range(2))
                        or not 0 <= t['modifier_redraws'] <= 254
                        or tr[0, 1]+tr[1, 0] > t['modifier_redraws']
                        or len(t['elite_bits']) != 2 or any(v not in (0, 1) for v in t['elite_bits'])
                        or t['next_f'] != (tr[:, 1].sum()+sum(t['elite_bits']))/256):
                    raise ValueError('modifier mutation/elite accounting mismatch')
            prior = ep['final_f']
    old.validate_exposure(rows, schedule, bank, generations, initial_frequency=INITIAL_F)
    return sorted(rows, key=old.key)


def probabilities(rows):
    result = {}
    for r in rows:
        identity = f"{r['build']}:{r['repeat']}"
        result.setdefault(identity, {'initial': 1/32, 'R-all': 0.5})[r['arm']+'-final'] = 0.5*r['final_f']
    if any(set(p) != set(READOUT_ARMS) for p in result.values()):
        raise ValueError('incomplete endpoint probability grid')
    return result


def exposure(args, out, deadline):
    start = time.monotonic()
    bank, libs, historical = old.load_saved(args.saved)
    schedule, frozen, audit = schedules(bank, args.smoke), freeze(bank), audit_seeds(bank, historical)
    artifacts = dict(bank=bank, libraries=libs, schedules=schedule, method_freeze=frozen, seed_audit=audit)
    for n, value in artifacts.items():
        write_json(out, n+'.json', value)
    cells = {c['id']: dict(id=c['id'], labels=c['labels']) for c in bank['screen']['cells']
             if c['id'] in bank['split']['development']}
    jobs = [(m, cells, bank['inputs'], [e['prefix'] for e in libs[m['build']]['semantic_all']], 64)
            for m in schedule['exposure']]
    rows, elapsed = old.batch(out, 'exposure.jsonl', jobs, execute_exposure, args.workers, deadline)
    rows = validate_exposure(rows, schedule['exposure'], bank)
    manifest = dict(admitted=True, smoke=args.smoke, protected_searches=0, workers=args.workers,
                    seconds=time.monotonic()-start, exposure_batch_seconds=elapsed,
                    git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
                    saved_preparation_hash=old.SAVED_HASH, exposure_rows_hash=digest(rows),
                    probabilities=probabilities(rows), artifacts={n: digest(v) for n, v in artifacts.items()})
    manifest['manifest_hash'] = digest(manifest)
    write_json(out, 'exposure_manifest.json', manifest)
    print('exposure complete', len(rows), 'wall', elapsed, flush=True)


def load_exposure(path, smoke):
    path = Path(path)
    if (path/'failure.json').exists():
        raise ValueError('exposure stage failed')
    manifest = json.loads((path/'exposure_manifest.json').read_text())
    if (not manifest['admitted'] or manifest['smoke'] != smoke or manifest['protected_searches'] != 0
            or manifest['saved_preparation_hash'] != old.SAVED_HASH
            or manifest['manifest_hash'] != digest({k: v for k, v in manifest.items() if k != 'manifest_hash'})):
        raise ValueError('exposure manifest mismatch')
    artifacts = {n: json.loads((path/(n+'.json')).read_text()) for n in manifest['artifacts']}
    if set(artifacts) != {'bank', 'libraries', 'schedules', 'method_freeze', 'seed_audit'}:
        raise ValueError('exposure artifact set mismatch')
    if any(digest(artifacts[n]) != h for n, h in manifest['artifacts'].items()):
        raise ValueError('exposure artifact mismatch')
    bank = old.saved.load_bank()
    if (artifacts['bank'] != bank or digest(artifacts['libraries']) != old.LIBRARIES_HASH
            or digest(artifacts['method_freeze']) != digest(freeze(bank)) or artifacts['schedules'] != schedules(bank, smoke)):
        raise ValueError('bank/library/method/schedule changed since exposure')
    historical = dict(schedules=old.saved.schedules(bank), seed_audit=old.saved.seed_audit(bank))
    if artifacts['seed_audit'] != audit_seeds(bank, historical):
        raise ValueError('exposure seed audit changed')
    rows = validate_exposure([json.loads(s) for s in (path/'exposure.jsonl').read_text().splitlines()],
                             artifacts['schedules']['exposure'], bank)
    if digest(rows) != manifest['exposure_rows_hash'] or probabilities(rows) != manifest['probabilities']:
        raise ValueError('endpoint extraction mismatch')
    return bank, artifacts, rows, manifest


def validate_scores(rows, metas, bank, probs):
    rows = old.base.validate_rows(rows, metas, bank)
    for row in rows:
        q = probs[f"{row['build']}:{row['population']}"][row['arm']]
        if (row['probability'] != q or row['cap'] != 524288 or row['cutoff'] != 65536
                or row['pop_size'] != 256 or (not row['solved'] and row['evaluations'] != 524288)
                or any(a['cap'] != 65536 or a['pop_size'] != 256 or a['crossover'] != 0.5
                       or a['force_cap'] for a in row['attempts'])):
            raise ValueError('readout probability/budget/failure cap mismatch')
    return rows


def paired_draws(arrays, rng, draws=DRAWS, nested=True):
    """Arrays have (library, population) shape; attach identical references once.

    Use common indices for every law, retaining each endpoint's reference and
    L/S/N pairing. Do not resample the 12 within-endpoint searches as acquisitions.
    """
    builds, pops = next(iter(arrays.values())).shape
    b = rng.integers(builds, size=(draws, builds))
    p = rng.integers(pops, size=(draws, builds, pops)) if nested else np.broadcast_to(np.arange(pops), (draws, builds, pops))
    return {a: x[b[..., None], p].mean(axis=(1, 2)) for a, x in arrays.items()}


def endpoint_arrays(scores, builds, populations, metric):
    values = {(r['build'], r['population'], r['arm'], r['cell'], r['scoring_repeat']): r[metric]
              for r in scores}
    if len(values) != len(scores):
        raise ValueError('duplicate endpoint scoring row')
    cells = sorted({r['cell'] for r in scores})
    return {a: np.array([[np.mean([values[b, p, a, c, r] for c in cells for r in range(2)])
                         for p in range(populations)] for b in range(builds)]) for a in READOUT_ARMS}


def classify(ratios):
    lo, hi = ratios['L-final/initial']['evaluations']['interval95']
    if hi < 0.90:
        if all(ratios['L-final/'+a+'-final']['evaluations']['interval95'][1] < 1 for a in ('N', 'S')):
            return 'useful_with_inheritance_controls'
        return 'saving_inheritance_unresolved'
    if lo > 0.80 and hi >= 0.90:
        return '20_percent_saving_excluded_for_this_procedure'
    return 'unresolved'


def summarize(exposure_rows, scores, bank, libs, smoke):
    builds, pops = (1, 1) if smoke else (24, 6)
    rng = np.random.default_rng(seed('bootstrap'))
    costs = {m: endpoint_arrays(scores, builds, pops, m) for m in ('evaluations', 'worker_seconds', 'solved')}
    boot = {m: paired_draws(costs[m], np.random.default_rng(seed('bootstrap'))) for m in ('evaluations', 'worker_seconds')}
    ratios = {n+'/'+d: {m: old.estimate(costs[m][n].mean()/costs[m][d].mean(), boot[m][n]/boot[m][d])
                      for m in ('evaluations', 'worker_seconds')}
              for n, d in [('L-final', 'initial'), ('L-final', 'N-final'), ('L-final', 'S-final'),
                           ('L-final', 'R-all'), ('initial', 'R-all')]}
    final = {a: np.array([[next(r['final_f'] for r in exposure_rows if
                              (r['build'], r['arm'], r['repeat']) == (b, a, p))
                          for p in range(pops)] for b in range(builds)]) for a in EXPOSURE_ARMS}
    fboot = paired_draws(final, rng)
    exposure_stats, operators, economics = {}, {}, {}
    by_endpoint = {(r['build'], r['arm'], r['repeat']): r for r in exposure_rows}
    for a in EXPOSURE_ARMS:
        rr = [r for r in exposure_rows if r['arm'] == a]
        traces = [t for r in rr for e in r['episodes'] for t in e['modifier_trace']]
        low = [t for t in traces if t['phase'] == 'pre' and 0 < t['census_f'] <= 0.25 and t['counters'] is not None]
        polymorphic = [t for t in traces if 0 < t['census_f'] < 1]
        transitions = np.sum([t['modifier_transitions'] for t in traces if t['counters'] is not None], axis=0)
        operators[a] = {phase: {str(s): {} for s in range(2)} for phase in ('pre', 'post')}
        for t in traces:
            if t['counters'] is None:
                continue
            for s, cc in enumerate(t['counters']):
                target = operators[a][t['phase']][str(s)]
                for k, v in cc.items():
                    target[k] = target.get(k, 0)+v
        for states in operators[a].values():
            for cc in states.values():
                cc['library_rejection_fraction'] = cc.get('rejected_library', 0)/cc['library_draws'] if cc.get('library_draws') else None
                cc['ordinary_rejection_fraction'] = cc.get('rejected_ordinary', 0)/cc['ordinary_donors'] if cc.get('ordinary_donors') else None
        low_differential = {a: np.array([[np.mean(v) if v else np.nan
            for p in range(pops)
            for v in [[t['recipient_f']-t['census_f'] for e in by_endpoint[b, a, p]['episodes']
                for t in e['modifier_trace'] if t['phase'] == 'pre' and 0 < t['census_f'] <= 0.25 and t['counters'] is not None]]]
            for b in range(builds)])}
        # Zero occupancy is explicit, rather than silently treated as a zero effect.
        low_arr = low_differential[a]
        low_estimate = None
        if np.isfinite(low_arr).all():
            low_boot = paired_draws(low_differential, np.random.default_rng(seed('bootstrap')))[a]
            low_estimate = old.estimate(low_arr.mean(), low_boot)
        exposure_stats[a] = dict(trajectories=len(rr), mean_final_f=old.estimate(final[a].mean(), fboot[a]),
            final_by_endpoint=final[a].tolist(), zero_endpoints=sum(r['final_f'] == 0 for r in rr),
            fixed_endpoints=sum(r['final_f'] == 1 for r in rr), polymorphic_generations=len(polymorphic),
            pre_solve_polymorphic_generations=sum(t['phase'] == 'pre' for t in polymorphic),
            zero_carrier_generations=sum(t['census_f'] == 0 for t in traces),
            fixed_carrier_generations=sum(t['census_f'] == 1 for t in traces),
            episodes_solved=sum(e['solved'] for r in rr for e in r['episodes']),
            episodes=len(rr)*12, evaluations=sum(e['evaluations'] for r in rr for e in r['episodes']),
            worker_seconds=sum(r['worker_seconds'] for r in rr), modifier_transitions=transitions.tolist(),
            off_to_on=float(transitions[0, 1]/transitions[0].sum()) if transitions[0].sum() else None,
            on_to_off=float(transitions[1, 0]/transitions[1].sum()) if transitions[1].sum() else None,
            low_f_pre_solve_generations=len(low), low_f_selection_differential=low_estimate,
            low_f_empty_endpoints=int(np.isnan(low_arr).sum()),
            low_f_generation_weighted_differential=float(np.mean([t['recipient_f']-t['census_f'] for t in low])) if low else None,
            low_f_generation_weighted_relative_advantage=float(np.mean([(t['recipient_f']-t['census_f'])/(t['census_f']*(1-t['census_f'])) for t in low])) if low else None,
            mean_distinct_recipients=float(np.mean([t['distinct_recipients'] for t in traces if t['counters'] is not None])))
        law = a+'-final'
        economics[law] = {}
        for m in ('evaluations', 'worker_seconds'):
            acq = np.array([[lib['acquisition_evaluations'] if m == 'evaluations' else
                           lib['acquisition_worker_seconds']+sum(lib[k] for k in old.saved.TIMINGS if k != 'literal_seconds')
                           for _ in range(pops)] for lib in libs[:builds]])
            modifier = np.array([[sum(e['evaluations'] for e in by_endpoint[b, a, p]['episodes']) if m == 'evaluations'
                                  else by_endpoint[b, a, p]['worker_seconds']
                                  for p in range(pops)] for b in range(builds)])
            total = acq+modifier+costs[m][law]
            # Fair total alternative also buys the same externally acquired library.
            arrays = dict(endpoint=total, initial=acq+costs[m]['initial'], fixed_all=acq+costs[m]['R-all'])
            sampled = paired_draws(arrays, np.random.default_rng(seed('bootstrap')))
            economics[law][m] = dict(acquisition=float(acq.mean()), modifier=float(modifier.mean()),
                fresh_search=float(costs[m][law].mean()), total=float(total.mean()),
                total_over_initial=old.estimate(total.mean()/arrays['initial'].mean(), sampled['endpoint']/sampled['initial']),
                total_over_fixed_all=old.estimate(total.mean()/arrays['fixed_all'].mean(), sampled['endpoint']/sampled['fixed_all']),
                total_over_initial_search_only=float(total.mean()/costs[m]['initial'].mean()),
                total_over_fixed_all_search_only=float(total.mean()/costs[m]['R-all'].mean()))
    per_cell = {c: {a: dict(jobs=len(rr), solves=sum(r['solved'] for r in rr),
                            capped_mean=float(np.mean([r['evaluations'] for r in rr])),
                            mean_worker_seconds=float(np.mean([r['worker_seconds'] for r in rr])))
                   for a in READOUT_ARMS for rr in [[r for r in scores if r['cell'] == c and r['arm'] == a]]}
                for c in bank['split']['development']}
    headroom = ratios['initial/R-all']['evaluations']['point'] >= 1.25
    return dict(smoke=smoke, protected_searches=0, readout_ratios=ratios,
        outcome='smoke_only' if smoke else classify(ratios), headroom_point_at_least_1_25=headroom,
        headroom_interpretation='Below 1.25 limits this candidate; it does not refute inheritance generally.',
        exposure=exposure_stats, final_frequency_L_minus={a: old.estimate((final['L']-final[a]).mean(), fboot['L']-fboot[a]) for a in ('N', 'S')},
        operators_by_child_state_and_solve_phase=operators, acquisition_plus_search=economics,
        endpoint_costs={m: {a: v.tolist() for a, v in values.items()} for m, values in costs.items()},
        arms={a: dict(jobs=sum(r['arm'] == a for r in scores), solves=sum(r['solved'] for r in scores if r['arm'] == a),
                     capped_mean=float(costs['evaluations'][a].mean()), mean_worker_seconds=float(costs['worker_seconds'][a].mean())) for a in READOUT_ARMS},
        per_cell=per_cell, bootstrap=freeze(bank)['bootstrap'],
        supplied_R_order_context='Historical 1228 R-all/R-order evaluations ratio 7.27 [5.49, 9.81] (research/runs/2026-10-11-1228/analysis.md); R-order is supplied domain knowledge, not scored anew here.',
        economics_scope='One historical library acquisition plus extraction and one modifier trajectory per endpoint; alternative totals include that same library but no modifier acquisition.',
        interpretation='Fixed recurrent mutation, exposure and individual deployment rule only. Allele movement or degraded shuffled control alone is insufficient. Broad uncertainty is unresolved; no future-learner strength bound.',
        scope=freeze(bank)['scope'])


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
    axes[0].axhline(INITIAL_F, color='black', linestyle='--')
    axes[0].set(xlabel='Evaluated generation; resets every 64', ylabel='Carrier frequency')
    axes[1].set(xlabel='Evaluated generation', ylabel='Training correctness diversity')
    for ax in axes[:2]:
        ax.legend()
    axes[2].bar(READOUT_ARMS, [np.mean([r['evaluations'] for r in scores if r['arm'] == a]) for a in READOUT_ARMS])
    axes[2].set(ylabel='Fresh capped mean evaluations')
    axes[2].tick_params(axis='x', rotation=25)
    fig.tight_layout()
    fig.savefig(out/'dynamics.png', dpi=140)
    plt.close(fig)


def readout(args, out, deadline):
    bank, artifacts, rows, manifest = load_exposure(args.exposure, args.smoke)
    for n, value in artifacts.items():
        write_json(out, n+'.json', value)
    write_json(out, 'exposure_manifest.json', manifest)
    by = {c['id']: dict(id=c['id'], labels=c['labels']) for c in bank['screen']['cells']}
    metas = artifacts['schedules']['readout']
    jobs = [(m, by[m['cell']], bank['inputs'], [e['prefix'] for e in artifacts['libraries'][m['build']]['semantic_all']],
             manifest['probabilities'][f"{m['build']}:{m['population']}"][m['arm']], 65536) for m in metas]
    scores, elapsed = old.batch(out, 'score.jsonl', jobs, old.execute_readout, args.workers, deadline)
    scores = validate_scores(scores, metas, bank, manifest['probabilities'])
    report = summarize(rows, scores, bank, artifacts['libraries'], args.smoke)
    report.update(admitted=True, score_rows_hash=digest(scores), exposure_manifest_hash=manifest['manifest_hash'],
                  score_batch_seconds=elapsed, workers=args.workers)
    plots(out, rows, scores)
    write_json(out, 'report.json', report)
    print('readout complete', len(scores), 'wall', elapsed, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=('exposure', 'readout'))
    p.add_argument('--saved', default=old.DEFAULT_SAVED)
    p.add_argument('--exposure')
    p.add_argument('--workers', type=int, default=10)
    p.add_argument('--seconds', type=int)
    p.add_argument('--smoke', action='store_true')
    args = p.parse_args()
    limit = 1770 if args.phase == 'exposure' else 7170
    seconds = limit if args.seconds is None else args.seconds
    if args.workers < 1 or not 0 < seconds <= limit or (args.phase == 'readout' and not args.exposure):
        p.error('positive workers, approved deadline and --exposure for readout required')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if any((out/n).exists() for n in ('failure.json', 'exposure.jsonl', 'score.jsonl', 'exposure_manifest.json', 'report.json', 'method_freeze.json')):
        p.error('RUN_DIR contains previous experiment artifacts')
    deadline = time.monotonic()+seconds
    try:
        (exposure if args.phase == 'exposure' else readout)(args, out, deadline)
        if time.monotonic() > deadline:
            raise TimeoutError('fixed deadline exceeded during validation/reporting')
    except Exception as error:
        write_json(out, 'failure.json', dict(admitted=False, phase=args.phase, smoke=args.smoke, error=str(error)))
        raise


if __name__ == '__main__':
    main()
