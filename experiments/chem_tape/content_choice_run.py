"""0250 inherited choice between immutable order and gate donor repertoires.

Development-only exposure and separately deployed population endpoints. No
acquisition, protected search, donor fitting, or performance-based pairing.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import inherited_library_run as old
from experiments.chem_tape import recurrent_library_run as recurrent
from experiments.chem_tape import signed_gate_run as gate
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_gp_search import Tree, search
from experiments.chem_tape.tree_library import verify_entries

TASK = '2026-10-12-0250'
FAMILIES = ('order', 'gate')
ARMS = ('L', 'S', 'N')
LAWS = ('L-matched', 'L-swapped', 'S', 'N', 'M')
PURE = ('O', 'G')
DRAWS = 8192
ARCHIVE = Path(__file__).with_name('data')/'signed_chain_2044'/'saved_1938.json.gz'
ARCHIVE_SHA = '2e6b84e2b1c74a39005eb17fa7b273bc2249bbbdec80ce62224d88b8059b81ca'


def seed(domain, *identity):
    raw = json.dumps([TASK, domain, *identity], separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1 << 63)-1)


def load_saved():
    ob, ol, oa = old.load_saved(old.DEFAULT_SAVED)
    raw = ARCHIVE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA:
        raise ValueError('1938 archive changed')
    archive = json.loads(gzip.decompress(raw))
    files = archive['files']
    if any(hashlib.sha256(v.encode()).hexdigest() != archive['file_sha256'][k]
           for k, v in files.items()):
        raise ValueError('1938 archive file changed')
    ga = {n: json.loads(files[n+'.json']) for n in
          ('bank', 'libraries', 'method_freeze', 'schedules', 'preparation', 'seed_audit')}
    gb, gl, p = ga['bank'], ga['libraries'], ga['preparation']
    rows = gate.validate_rows([json.loads(x) for x in files['acquisition.jsonl'].splitlines()],
                              gate.schedules(gb)['source'], gb)
    if (digest(gb) != gate.BANK_HASH or not p['admitted'] or p['smoke'] or len(gl) != 24
            or p['preparation_hash'] != digest({k: v for k, v in p.items() if k != 'preparation_hash'})
            or ga['schedules'] != gate.schedules(gb)
            or any(p[k+'_hash'] != digest(v) for k, v in
                   [('source_rows', rows), ('libraries', gl), ('bank', gb),
                    ('freeze', ga['method_freeze']), ('schedule', ga['schedules']), ('audit', ga['seed_audit'])])
            or gate.deterministic(gl) != gate.deterministic(gate.libraries_from(rows, gb, 24))):
        raise ValueError('1938 saved acquisition replay mismatch')
    banks, libs = dict(order=ob, gate=gb), dict(order=ol, gate=gl)
    if ob['inputs'] != gb['inputs']:
        raise ValueError('bank execution inputs differ')
    for family, field in [('order', 'semantic_all'), ('gate', 'semantic')]:
        for lib in libs[family]:
            if not lib[field]:
                raise ValueError('empty saved repertoire')
            verify_entries(lib[field], banks[family]['inputs'])
    return banks, libs, dict(order=oa, gate=ga)


def schedules(banks, smoke=False):
    builds, pops = (4, 1) if smoke else (24, 8)
    prefix = 'smoke-' if smoke else ''
    exposure, readout = [], []
    for fam in FAMILIES:
        cells = banks[fam]['split']['development']
        if len(cells) != 6 or set(cells) & set(banks[fam]['split']['protected']):
            raise ValueError('invalid development roster')
        repeats = 1 if smoke else (2 if fam == 'order' else 4)
        for b in range(builds):
            for p in range(pops):
                rotation = (b+p) % 6
                sequence = cells[rotation:]+cells[:rotation]
                for a in ARMS:
                    exposure.append(dict(family=fam, build=b, arm=a, repeat=p, cells=sequence*2,
                        assignment_seed=seed(prefix+'assignment', fam, b, p),
                        program_seeds=[seed(prefix+'program', fam, b, p, e) for e in range(12)],
                        modifier_seeds=[seed(prefix+'modifier', fam, b, p, e) for e in range(12)]))
                for c in cells:
                    for r in range(repeats):
                        for a in LAWS:
                            readout.append(dict(family=fam, build=b, population=p, cell=c,
                                repeat=p*repeats+r, scoring_repeat=r, arm=a,
                                seeds=[seed(prefix+'readout', fam, b, p, c, r, k) for k in range(8)]))
            for c in cells:
                for r in range(repeats):
                    for a in PURE:
                        readout.append(dict(family=fam, build=b, population=None, cell=c,
                            repeat=r, scoring_repeat=r, arm=a,
                            seeds=[seed(prefix+'pure', fam, b, c, r, k) for k in range(8)]))
    return dict(exposure=exposure, readout=readout)


def audit_seeds(banks, historical):
    previous = recurrent.audit_seeds(banks['order'], historical['order'])
    history = set()
    def collect(obj, field=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                collect(v, k if 'seed' in k else field)
        elif isinstance(obj, list):
            for v in obj:
                collect(v, field)
        elif isinstance(obj, int) and 'seed' in field:
            history.add(obj)
    collect(historical)
    collect(previous)
    # The previous audit publishes its own namespaces and hashes older sets;
    # inspect those raw sets as well, rather than treating a hash as a seed list.
    earlier = old.base.seed_audit(banks['order'])
    collect(earlier)
    for artifact in earlier['historical_artifacts']:
        path = Path(artifact['path'])
        raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != artifact['sha256']:
            raise ValueError('historical seed artifact changed')
        collect(json.loads(raw))
    collect(old.audit_seeds(banks['order'], historical['order']))
    gate_pre = Path(gate.DATA)/'presearch.json.gz'
    collect(json.loads(gzip.decompress(gate_pre.read_bytes())))
    # Include historical numeric rosters, and the steward's fixed headroom seeds.
    history.update(range(7000, 7800)); history.update(range(9000, 9006))
    for fam in FAMILIES:
        for b in range(24):
            for c in banks[fam]['split']['development']:
                for k in range(8):
                    raw = json.dumps(['steward-probe-'+TASK, fam, b, c, k], separators=(',', ':'))
                    history.add(int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1<<63)-1))
    groups = {}
    for smoke in (False, True):
        sc = schedules(banks, smoke)
        pre = 'smoke-' if smoke else ''
        for field in ('assignment_seed', 'program_seeds', 'modifier_seeds'):
            groups[pre+field] = {v for m in sc['exposure'] for v in
                                ([m[field]] if isinstance(m[field], int) else m[field])}
        for domain, pure in [('readout', False), ('pure', True)]:
            groups[pre+domain] = {v for m in sc['readout'] if (m['arm'] in PURE) == pure for v in m['seeds']}
    groups['bootstrap'] = {seed('bootstrap')}
    groups['validation'] = {seed('validation', k) for k in range(10)}
    seen = set(history)
    for name, values in groups.items():
        if seen & values:
            raise ValueError('seed collision: '+name)
        seen.update(values)
    expected = dict(assignment_seed=384, program_seeds=4608, modifier_seeds=4608,
                    readout=24*8*6*6*8, pure=24*6*6*8)
    if any(len(groups[k]) != v for k, v in expected.items()):
        raise ValueError('unintended seed duplication')
    return dict(admitted=True, historical_hash=digest(sorted(history)), historical_count=len(history),
                published_seed_sets={k: sorted(v) for k, v in groups.items()})


def freeze(banks, libs):
    methods = method_hashes()
    for name in ('content_choice_run.py', 'inherited_library_run.py', 'recurrent_library_run.py',
                 'order_run.py', 'order_cap_run.py', 'signed_gate_run.py', 'tree_library.py',
                 'order_library.py', 'tree_gp_search.py'):
        path = Path(__file__).with_name(name)
        methods[str(path.relative_to(Path.cwd()))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(task=TASK, methods=methods, banks={k: digest(v) for k, v in banks.items()},
        libraries={k: digest(v) for k, v in libs.items()}, saved_order=old.SAVED_HASH, saved_gate=ARCHIVE_SHA,
        pairing='build b to build b; all 24; unchanged semantic_all order / semantic gate',
        exposure=dict(builds=24, populations=8, families=FAMILIES, arms=ARMS, population=256,
            initial_ones=128, episodes=12, generations=64, crossover=0.5, elites=2,
            redraw_probability=1/32, redraw_one_probability=0.5, library_probability=0.5,
            state_zero='order', state_one='gate', neutral='both states normalized half/half',
            shuffle='before selection including elites', reset='programs independently reset; bit slots persist'),
        readout=dict(laws=LAWS+PURE, ordinary_probability=0.5, cutoff=65536, attempts=8,
            repeats=dict(order=2, gate=4), endpoint_law='order (1-f)/2; gate f/2; normalize within library'),
        bootstrap=dict(seed=seed('bootstrap'), draws=DRAWS, unit='paired builds jointly across families; populations within build; pure references once per build'),
        decision=dict(primary='geometric mean of family L-matched/M capped arithmetic mean cost ratios',
            useful_upper=0.90, directional_upper=1.0, twenty_percent_excluded_lower=0.80,
            precedence='usefulness first; saving-excluded label independent',
            headroom='own-pure/M upper >=0.90 is unresolved, cannot override direct L/M saving'),
        scope='supplied repertoires; development banks; new searches, no unseen-task transfer')


def libraries_for(libs, b):
    return tuple([Tree(tuple(e['prefix'])) for e in libs[fam][b][field]]
                 for fam, field in [('order', 'semantic_all'), ('gate', 'semantic')])


def execute_exposure(job):
    meta, cells, inputs, libraries = job
    bits = np.zeros(256, dtype=np.int8)
    bits[np.random.default_rng(meta['assignment_seed']).choice(256, 128, replace=False)] = 1
    episodes, start = [], time.monotonic()
    for e, c in enumerate(meta['cells']):
        initial = float(bits.mean())
        row = search((cells[c], meta['program_seeds'][e], 64*256, 256, inputs, 0.5),
            donor_libraries=libraries, gate_fraction=0.5 if meta['arm'] == 'N' else None,
            modifier_bits=bits, modifier_seed=meta['modifier_seeds'][e],
            shuffle_modifiers=meta['arm'] == 'S', modifier_mutation_probability=1/32,
            modifier_redraw_probability=0.5, continue_after_solve=True)
        bits = np.array(row.pop('modifier_bits'), dtype=np.int8)
        first = row['first_solve_evaluations']
        solve_f = None if first is None else row['modifier_trace'][first//256-1]['census_f']
        row.update(episode=e, initial_f=initial, final_f=float(bits.mean()),
            pre_solve_delta=float(bits.mean())-initial if solve_f is None else solve_f-initial,
            post_solve_delta=None if solve_f is None else float(bits.mean())-solve_f)
        episodes.append(row)
    return meta | dict(episodes=episodes, final_f=float(bits.mean()), final_bits=bits.tolist(),
                       worker_seconds=time.monotonic()-start)


def key(row):
    return row['family'], row['build'], row['arm'], row['repeat']


def validate_exposure(rows, schedule, banks):
    # Reuse existing exact execution/continuity validators, replacing only the
    # old off-state donor restriction; both content states must draw libraries.
    expected = {key(m): m for m in schedule}
    if len(rows) != len(expected) or len({key(r) for r in rows}) != len(rows) or {key(r) for r in rows} != set(expected):
        raise ValueError('exposure grid mismatch')
    for r in rows:
        if any(r[k] != v for k, v in expected[key(r)].items()):
            raise ValueError('exposure metadata mismatch')
        if len(r['episodes']) != 12 or len(r['final_bits']) != 256 or not np.isin(r['final_bits'], [0, 1]).all() or r['final_f'] != np.mean(r['final_bits']):
            raise ValueError('endpoint accounting mismatch')
        prior = 0.5
        bank = banks[r['family']]
        for e, ep in enumerate(r['episodes']):
            tr = ep['modifier_trace']
            if (ep['cell'] != r['cells'][e] or ep['seed'] != r['program_seeds'][e] or ep['episode'] != e
                    or ep['cap'] != 16384 or ep['pop_size'] != 256 or ep['crossover'] != 0.5 or ep['force_cap']
                    or ep['evaluations'] != 16384 or ep['generations'] != 64 or len(tr) != 64
                    or ep['initial_f'] != prior or tr[0]['census_f'] != prior
                    or tr[-1]['next_f'] != ep['final_f'] or ep['library_probability'] != 0.5
                    or ep['content_choice_gate_fraction'] != (0.5 if r['arm'] == 'N' else None)):
                raise ValueError('episode budget/continuity mismatch')
            totals = {k: 0 for k in ep['operator']}
            for g, t in enumerate(tr):
                if t['generation'] != g or (g and t['census_f'] != tr[g-1]['next_f']):
                    raise ValueError('generation continuity mismatch')
                first = ep['first_solve_evaluations']
                if t['phase'] != ('post' if first is not None and (g+1)*256 >= first else 'pre'):
                    raise ValueError('solve phase mismatch')
                if t['counters'] is None:
                    if g != 63:
                        raise ValueError('missing transition')
                    continue
                cc, transitions = t['counters'], np.asarray(t['modifier_transitions'])
                if (transitions.shape != (2, 2) or np.any(transitions < 0) or np.any(transitions != transitions.astype(int))
                        or transitions.sum() != 254 or transitions[1].sum()/254 != t['recipient_f']
                        or t['pre_mutation_f'] != t['recipient_f']
                        or transitions[:, 1].sum()/254 != t['post_mutation_f']
                        or any(transitions[:, s].sum() != cc[s]['recipients'] for s in (0, 1))
                        or not 0 <= t['modifier_redraws'] <= 254
                        or transitions[0, 1]+transitions[1, 0] > t['modifier_redraws']
                        or len(t['elite_bits']) != 2 or not np.isin(t['elite_bits'], [0, 1]).all()
                        or t['next_f'] != (transitions[:, 1].sum()+sum(t['elite_bits']))/256):
                    raise ValueError('modifier/redraw/elite accounting mismatch')
                for s, c in enumerate(cc):
                    if (c['crossover']+c['mutation'] != c['recipients']
                            or c['library_draws']+c['ordinary_donors'] != c['mutation']
                            or c['library_insertions']+c['rejected_library'] != c['library_draws']
                            or c['ordinary_insertions']+c['rejected_ordinary'] != c['ordinary_donors']
                            or c['rejected_mutation'] != c['rejected_library']+c['rejected_ordinary']
                            or c['order_draws']+c['gate_draws'] != c['library_draws'] or c['empty_fallbacks']
                            or (r['arm'] != 'N' and c['gate_draws' if s == 0 else 'order_draws'])):
                        raise ValueError('content donor accounting mismatch')
                    for k in totals:
                        totals[k] += c[k]
            if totals != ep['operator']:
                raise ValueError('episode operator totals mismatch')
            if ep['solved'] != (ep['first_solve_evaluations'] is not None):
                raise ValueError('solve accounting mismatch')
            if ep['solved']:
                from experiments.chem_tape.composition_search import outputs
                tree = Tree(tuple(ep['solver_tree']))
                labels = next(c['labels'] for c in bank['screen']['cells'] if c['id'] == ep['cell'])
                if (list(tree.program) != ep['solver'] or not 256 <= ep['first_solve_evaluations'] <= 16384
                        or outputs([tree.program], bank['inputs'], 'v2_x4')[0].tolist() != labels):
                    raise ValueError('invalid first exact witness')
            prior = ep['final_f']
        if prior != r['final_f']:
            raise ValueError('final episode/endpoint mismatch')
    return sorted(rows, key=key)


def fraction(meta, endpoints):
    if meta['arm'] in ('M', 'O', 'G'):
        return {'M': 0.5, 'O': 0.0, 'G': 1.0}[meta['arm']]
    family = meta['family']
    if meta['arm'] == 'L-swapped':
        family = 'gate' if family == 'order' else 'order'
    arm = 'L' if meta['arm'].startswith('L-') else meta['arm']
    return endpoints[family, meta['build'], arm, meta['population']]['final_f']


def execute_readout(job):
    meta, cell, inputs, libraries, f = job
    start, attempts = time.monotonic(), []
    for s in meta['seeds']:
        row = search((cell, s, 65536, 256, inputs, 0.5), donor_libraries=libraries, gate_fraction=f)
        attempts.append(row)
        if row['solved']:
            break
    return meta | dict(gate_fraction=f, solved=attempts[-1]['solved'], solver=attempts[-1]['solver'],
        evaluations=sum(a['evaluations'] for a in attempts), cap=524288, cutoff=65536,
        pop_size=256, worker_seconds=time.monotonic()-start, attempts=attempts)


def validate_scores(rows, metas, banks, endpoints):
    result = []
    for fam in FAMILIES:
        rr = [r for r in rows if r['family'] == fam]
        mm = [m for m in metas if m['family'] == fam]
        result.extend(old.base.validate_rows(rr, mm, banks[fam]))
        for r in rr:
            if (r['gate_fraction'] != fraction(r, endpoints) or r['cap'] != 524288 or r['cutoff'] != 65536
                    or r['pop_size'] != 256 or (not r['solved'] and r['evaluations'] != 524288)):
                raise ValueError('readout fraction/budget mismatch')
            for a in r['attempts']:
                op = a['operator']
                if (a['cap'] != 65536 or a['pop_size'] != 256 or a['crossover'] != 0.5 or a['force_cap']
                        or a['library_probability'] != 0.5 or a['content_choice_gate_fraction'] != r['gate_fraction']
                        or op['order_draws']+op['gate_draws'] != op['library_draws']
                        or op['library_draws']+op['ordinary_donors'] != op['mutation']
                        or op['library_insertions']+op['rejected_library'] != op['library_draws']
                        or op['empty_fallbacks']):
                    raise ValueError('readout operator mismatch')
    return sorted(result, key=lambda r: (r['family'], r['build'], r['population'] or 0, r['arm'], r['cell'], r['repeat']))


def exposure(args, out, deadline):
    start = time.monotonic()
    banks, libs, history = load_saved()
    artifacts = dict(banks=banks, libraries=libs, schedules=schedules(banks, args.smoke),
                     method_freeze=freeze(banks, libs), seed_audit=audit_seeds(banks, history))
    for n, v in artifacts.items():
        write_json(out, n+'.json', v)
    cells = {f: {c['id']: dict(id=c['id'], labels=c['labels']) for c in banks[f]['screen']['cells']
                 if c['id'] in banks[f]['split']['development']} for f in FAMILIES}
    jobs = [(m, cells[m['family']], banks[m['family']]['inputs'], libraries_for(libs, m['build']))
            for m in artifacts['schedules']['exposure']]
    rows, elapsed = old.batch(out, 'exposure.jsonl', jobs, execute_exposure, args.workers, deadline)
    rows = validate_exposure(rows, artifacts['schedules']['exposure'], banks)
    manifest = dict(admitted=True, smoke=args.smoke, protected_searches=0,
        exposure_rows_hash=digest(rows), artifacts={n: digest(v) for n, v in artifacts.items()},
        exposure_batch_seconds=elapsed, seconds=time.monotonic()-start, workers=args.workers,
        worker_seconds=sum(r['worker_seconds'] for r in rows),
        episode_solves=sum(e['solved'] for r in rows for e in r['episodes']), episodes=12*len(rows),
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip())
    manifest['manifest_hash'] = digest(manifest)
    write_json(out, 'exposure_manifest.json', manifest)
    print('exposure complete', len(rows), 'wall', elapsed, flush=True)


def load_exposure(path, smoke):
    path = Path(path)
    if (path/'failure.json').exists():
        raise ValueError('exposure has recorded failure')
    manifest = json.loads((path/'exposure_manifest.json').read_text())
    if (not manifest['admitted'] or manifest['smoke'] != smoke or manifest['protected_searches']
            or manifest['manifest_hash'] != digest({k: v for k, v in manifest.items() if k != 'manifest_hash'})):
        raise ValueError('exposure manifest mismatch')
    artifacts = {n: json.loads((path/(n+'.json')).read_text()) for n in manifest['artifacts']}
    banks, libs, history = load_saved()
    expected = dict(banks=banks, libraries=libs, schedules=schedules(banks, smoke),
                    method_freeze=freeze(banks, libs), seed_audit=audit_seeds(banks, history))
    if (set(artifacts) != set(expected) or any(digest(v) != manifest['artifacts'][n]
            or digest(v) != digest(expected[n]) for n, v in artifacts.items())):
        raise ValueError('saved inputs/method/schedule/seed audit changed')
    rows = validate_exposure([json.loads(x) for x in (path/'exposure.jsonl').read_text().splitlines()],
                             artifacts['schedules']['exposure'], banks)
    if digest(rows) != manifest['exposure_rows_hash']:
        raise ValueError('exposure rows changed')
    return artifacts, rows, manifest


def cost_arrays(scores, builds, pops, metric):
    result = {}
    for fam in FAMILIES:
        rr = [r for r in scores if r['family'] == fam]
        for law in LAWS+PURE:
            by = {(r['build'], r['population']): [] for r in rr if r['arm'] == law}
            for r in rr:
                if r['arm'] == law:
                    by[r['build'], r['population']].append(r[metric])
            result[fam+'/'+law] = np.array([[np.mean(by[b, None if law in PURE else p])
                                           for p in range(pops)] for b in range(builds)])
    return result


def classify(primary, ratios):
    lo, hi = primary['interval95']
    directions = [fam for fam in FAMILIES if all(ratios[fam+'/'+k]['interval95'][1] < 1
                   for k in ('L-matched/M', 'L-matched/L-swapped'))]
    if hi < 0.90:
        outcome = ('useful_reciprocal' if len(directions) == 2 else
                   'useful_one_direction' if len(directions) == 1 else
                   'pooled_improvement_directional_dependence_unresolved')
    else:
        outcome = '20_percent_pooled_saving_excluded' if lo > 0.80 else 'unresolved'
    return dict(outcome=outcome, resolved_directions=directions, twenty_percent_pooled_saving_excluded=lo > 0.80)


def summarize(exposures, scores, artifacts, smoke):
    builds, pops = (4, 1) if smoke else (24, 8)
    metrics = ('evaluations', 'worker_seconds')
    costs = {m: cost_arrays(scores, builds, pops, m) for m in metrics}
    sampled = {m: recurrent.paired_draws(v, np.random.default_rng(seed('bootstrap')))
               for m, v in costs.items()}
    contrasts = [('L-matched', 'M'), ('L-matched', 'L-swapped'), ('S', 'M'), ('N', 'M'),
                 ('L-matched', 'S'), ('L-matched', 'N'), ('O', 'M'), ('G', 'M')]
    ratios = {m: {fam+'/'+n+'/'+d: old.estimate(costs[m][fam+'/'+n].mean()/costs[m][fam+'/'+d].mean(),
                   sampled[m][fam+'/'+n]/sampled[m][fam+'/'+d])
                  for fam in FAMILIES for n, d in contrasts} for m in metrics}
    primary = old.estimate(np.sqrt(np.prod([ratios['evaluations'][f+'/L-matched/M']['point'] for f in FAMILIES])),
        np.sqrt(np.prod([sampled['evaluations'][f+'/L-matched']/sampled['evaluations'][f+'/M'] for f in FAMILIES], axis=0)))
    headroom = old.estimate(np.sqrt(np.prod([ratios['evaluations'][f+'/'+law+'/M']['point'] for f, law in [('order', 'O'), ('gate', 'G')]])),
        np.sqrt((sampled['evaluations']['order/O']/sampled['evaluations']['order/M'])*(sampled['evaluations']['gate/G']/sampled['evaluations']['gate/M'])))
    stats, operators, economics = {}, {}, {}
    endpoints = {key(r): r for r in exposures}
    final = {f+'/'+a: np.array([[endpoints[f, b, a, p]['final_f'] for p in range(pops)] for b in range(builds)]) for f in FAMILIES for a in ARMS}
    fboot = recurrent.paired_draws(final, np.random.default_rng(seed('bootstrap')))
    for fam in FAMILIES:
        for arm in ARMS:
            name = fam+'/'+arm
            rr = [r for r in exposures if r['family'] == fam and r['arm'] == arm]
            traces = [t for r in rr for ep in r['episodes'] for t in ep['modifier_trace'] if t['counters'] is not None]
            stats[name] = dict(trajectories=len(rr), final_f=old.estimate(final[name].mean(), fboot[name]),
                final_by_endpoint=final[name].tolist(), episodes=12*len(rr),
                episode_solves=sum(ep['solved'] for r in rr for ep in r['episodes']),
                worker_seconds=sum(r['worker_seconds'] for r in rr),
                pre_solve_delta=float(np.mean([ep['pre_solve_delta'] for r in rr for ep in r['episodes']])),
                maintenance_delta=float(np.mean(v)) if (v := [ep['post_solve_delta'] for r in rr for ep in r['episodes'] if ep['post_solve_delta'] is not None]) else None,
                selection_differential={phase: float(np.mean(v)) if (v := [t['recipient_f']-t['census_f'] for t in traces if t['phase'] == phase]) else None for phase in ('pre', 'post')})
            operators[name] = {phase: {str(s): {k: sum(t['counters'][s][k] for t in traces if t['phase'] == phase)
                for k in traces[0]['counters'][s]} for s in (0, 1)} for phase in ('pre', 'post')}
            for states in operators[name].values():
                for cc in states.values():
                    cc['attempted_library_fraction'] = cc['library_draws']/cc['mutation'] if cc['mutation'] else None
                    cc['library_rejection_fraction'] = cc['rejected_library']/cc['library_draws'] if cc['library_draws'] else None
        for law in LAWS+PURE:
            economics[fam+'/'+law] = {}
            for metric in metrics:
                acquired = []
                for b in range(builds):
                    total = 0
                    for f in (('order',) if law == 'O' else ('gate',) if law == 'G' else FAMILIES):
                        lib = artifacts['libraries'][f][b]
                        timing_names = old.saved.TIMINGS if f == 'order' else gate.TIMINGS
                        total += lib['acquisition_evaluations'] if metric == 'evaluations' else lib['acquisition_worker_seconds']+sum(lib[k] for k in timing_names if k != 'literal_seconds')
                    acquired.append(total)
                exp_cost = 0.0
                if law not in ('M', 'O', 'G'):
                    source_f = ('gate' if fam == 'order' else 'order') if law == 'L-swapped' else fam
                    arm = 'L' if law.startswith('L-') else law
                    rr = [r for r in exposures if r['family'] == source_f and r['arm'] == arm]
                    exp_cost = float(np.mean([sum(ep['evaluations'] for ep in r['episodes']) if metric == 'evaluations' else r['worker_seconds'] for r in rr]))
                fresh = float(costs[metric][fam+'/'+law].mean())
                economics[fam+'/'+law][metric] = dict(acquisition=float(np.mean(acquired)), exposure=exp_cost,
                    fresh_search=fresh, total=float(np.mean(acquired))+exp_cost+fresh,
                    already_owned_libraries_total=exp_cost+fresh)
    arms = {fam+'/'+law: dict(jobs=len(rr), solves=sum(r['solved'] for r in rr),
                capped_mean=float(np.mean([r['evaluations'] for r in rr])), worker_seconds=sum(r['worker_seconds'] for r in rr))
            for fam in FAMILIES for law in LAWS+PURE
            for rr in [[r for r in scores if r['family'] == fam and r['arm'] == law]]}
    per_cell = {fam: {c: {a: dict(jobs=len(rr), solves=sum(r['solved'] for r in rr),
            capped_mean=float(np.mean([r['evaluations'] for r in rr])), mean_worker_seconds=float(np.mean([r['worker_seconds'] for r in rr])))
            for a in LAWS+PURE for rr in [[r for r in scores if r['family'] == fam and r['cell'] == c and r['arm'] == a]]}
            for c in artifacts['banks'][fam]['split']['development']} for fam in FAMILIES}
    linkage = all(ratios['evaluations'][f+'/L-matched/'+a]['interval95'][1] < 1 for f in FAMILIES for a in ('S', 'N'))
    decision = classify(primary, ratios['evaluations'])
    if smoke:
        decision['outcome'] = 'smoke_only'
    def headroom_status(estimate):
        lo, hi = estimate['interval95']
        return ('ten_percent_headroom_established' if hi < 0.90 else
                'ten_percent_pure_endpoint_saving_excluded' if lo > 0.90 else 'headroom_unresolved')
    return dict(admitted=True, smoke=smoke, protected_searches=0, primary=primary, decision=decision,
        ratios=ratios, headroom=dict(pooled=headroom, per_family={f: ratios['evaluations'][f+'/'+a+'/M'] for f, a in [('order', 'O'), ('gate', 'G')]},
        pooled_status=headroom_status(headroom), per_family_status={f: headroom_status(ratios['evaluations'][f+'/'+a+'/M']) for f, a in [('order', 'O'), ('gate', 'G')]},
        interpretation='upper >=0.90: headroom unresolved, not saturation; direct L/M saving takes precedence'),
        linkage_interpretation='cost advantage over both controls resolved in both directions; inspect dynamics' if linkage else 'linkage contribution unresolved; inspect dynamics',
        exposure=stats, frequency_contrasts={f+'/L-'+a: old.estimate((final[f+'/L']-final[f+'/'+a]).mean(), fboot[f+'/L']-fboot[f+'/'+a]) for f in FAMILIES for a in ('S', 'N')},
        operators_by_child_state_and_solve_phase=operators, acquisition_plus_search=economics,
        arms=arms, per_cell=per_cell, endpoint_costs={m: {k: v.tolist() for k, v in vv.items()} for m, vv in costs.items()},
        bootstrap=artifacts['method_freeze']['bootstrap'], scope=artifacts['method_freeze']['scope'])


def plots(out, exposures, scores):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for i, fam in enumerate(FAMILIES):
        for a in ARMS:
            rr = [r for r in exposures if r['family'] == fam and r['arm'] == a]
            axes[i, 0].plot(np.mean([[t['census_f'] for ep in r['episodes'] for t in ep['modifier_trace']] for r in rr], axis=0), label=a)
            axes[i, 1].plot(np.mean([[t['diversity'] for ep in r['episodes'] for t in ep['modifier_trace']] for r in rr], axis=0), label=a)
        axes[i, 0].axhline(0.5, color='black', linestyle='--')
        axes[i, 0].set(xlabel='Generation; reset each 64', ylabel=fam+' gate fraction')
        axes[i, 1].set(xlabel='Generation', ylabel='Correctness diversity')
        axes[i, 0].legend(); axes[i, 1].legend()
        axes[i, 2].bar(LAWS+PURE, [np.mean([r['evaluations'] for r in scores if r['family'] == fam and r['arm'] == a]) for a in LAWS+PURE])
        axes[i, 2].set(ylabel='Fresh capped mean evaluations')
        axes[i, 2].tick_params(axis='x', rotation=30)
    fig.tight_layout()
    fig.savefig(out/'dynamics.png', dpi=140)
    plt.close(fig)


def readout(args, out, deadline):
    artifacts, exposures, manifest = load_exposure(args.exposure, args.smoke)
    for n, v in artifacts.items():
        write_json(out, n+'.json', v)
    write_json(out, 'exposure_manifest.json', manifest)
    endpoints = {key(r): r for r in exposures}
    banks, libs = artifacts['banks'], artifacts['libraries']
    by = {f: {c['id']: dict(id=c['id'], labels=c['labels']) for c in banks[f]['screen']['cells']
              if c['id'] in banks[f]['split']['development']} for f in FAMILIES}
    metas = artifacts['schedules']['readout']
    jobs = [(m, by[m['family']][m['cell']], banks[m['family']]['inputs'], libraries_for(libs, m['build']), fraction(m, endpoints)) for m in metas]
    scores, elapsed = old.batch(out, 'score.jsonl', jobs, execute_readout, args.workers, deadline)
    scores = validate_scores(scores, metas, banks, endpoints)
    report = summarize(exposures, scores, artifacts, args.smoke)
    report.update(score_rows_hash=digest(scores), exposure_manifest_hash=manifest['manifest_hash'],
                  score_batch_seconds=elapsed, workers=args.workers)
    plots(out, exposures, scores)
    write_json(out, 'report.json', report)
    print('readout complete', len(scores), 'wall', elapsed, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=('exposure', 'readout'))
    p.add_argument('--exposure')
    p.add_argument('--workers', type=int, default=11)
    p.add_argument('--seconds', type=int)
    p.add_argument('--smoke', action='store_true')
    args = p.parse_args()
    limit = 2970 if args.phase == 'exposure' else 9570
    seconds = limit if args.seconds is None else args.seconds
    if args.workers < 1 or not 0 < seconds <= limit or (args.phase == 'readout' and not args.exposure):
        p.error('positive workers, approved deadline and --exposure for readout required')
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if any((out/n).exists() for n in ('failure.json', 'exposure.jsonl', 'score.jsonl', 'exposure_manifest.json', 'report.json', 'method_freeze.json')):
        p.error('RUN_DIR contains prior experiment artifacts')
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
