"""1606 boundary-policy test: R versus replay-validated historical W and C."""

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import BANK_SHA, digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.fragment_reuse_run import pinned_history, schedule as old_schedule, target_ids
from experiments.chem_tape.fragment_run import Runner as BaseRunner, CORPORA, REPLAY_FIELDS, implementation_hashes, execute
from experiments.chem_tape.fragment_report import row_key
from experiments.chem_tape.suffix_preservation_audit import audit
from experiments.chem_tape.suffix_preservation_report import report
from experiments.chem_tape.then_addition_bank import load, BANK_SHA as TA_SHA

BASE = 206610091606
FIELDS = REPLAY_FIELDS + ('solver', 'operator')
PROVENANCE = Path(__file__).with_name('data') / 'pre_solve_1350' / 'provenance.json'


def historical():
    # Reuse the previously frozen byte hashes; no new mutable path discovery.
    provenance = json.loads(PROVENANCE.read_bytes())['historical']
    provenance['sha256'].update({
        'preparation.json': 'f14246c5eeaf81a477b18e1b42c9571474c1ad96c7a74ccb12a16e59e21e7e46',
        'libraries.json': '791d5f8c15b1fb7fe16be93c7aa1d012f776ece4c6068306af31b571e055a8fc',
        'operator_laws.json': 'fb1e0d79893c775fb3cea33351d616e75ce5d61dba69a5da7556f8a96711f3ab',
    })
    saved = {}
    for name, sha in provenance['sha256'].items():
        raw = (Path(provenance['path']) / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError(f'historical SHA mismatch: {name}')
        saved[name] = [json.loads(line) for line in raw.splitlines()] if name.endswith('.jsonl') else json.loads(raw)
    return saved, provenance


def roster(ids, paired):
    base = [r for r in old_schedule(ids, 16) if r['arm'] == 'C']
    if paired:
        return [dict(r, arm='R') for r in base]
    return [dict(r, arm=arm, seed=BASE + r['seed'] - 204610091036)
            for r in base if r['phase'] == 'then_addition' for arm in ('W', 'R')]


def timing_roster(ids, paired):
    # Cover all16 target cells, both source families and all16 corpora.
    keys = [dict(phase='smoke', corpus=f'{f}{ci % 8 + 1}', family=f, cell=cid,
                 seed=BASE + 2000000 + (f == 'PA') * 100000 + ci * 200)
            for ci, cid in enumerate(ids['then_addition']) for f in ('BE', 'PA')]
    if paired:
        return [dict(r, arm='R') for r in keys]
    # Sixteen paired keys cover each cell and each corpus once.
    return [dict(phase='smoke', corpus=f'{f}{ci % 8 + 1}', family=f, cell=cid, arm=arm,
                 seed=BASE + 2000000 + (f == 'PA') * 100000 + ci * 200)
            for ci, cid in enumerate(ids['then_addition'])
            for f in ('BE' if ci < 8 else 'PA',) for arm in ('W', 'R')]


def admit(rows, elapsed, prepare_wall, paired, workers=10):
    if len(rows) != 32:
        raise ValueError('expected32 timing searches')
    efficiency = min(workers, sum(r['seconds'] for r in rows) / elapsed)
    timings = {}
    for arm in (('R',) if paired else ('W', 'R')):
        rs = [r for r in rows if r['arm'] == arm]
        solved = [r['seconds'] for r in rs if r['solved']]
        capped = [r['seconds'] for r in rs if not r['solved']]
        # If no capped rows are observed, estimate a cap from the slowest
        # observed seconds/evaluation. This scenario is descriptive only.
        cap_seconds = max(capped) if capped else max(r['seconds'] / r['evaluations'] for r in rs) * 524288
        timings[arm] = dict(n=len(rs), solved=len(solved), capped=len(capped),
            mean_seconds=float(np.mean([r['seconds'] for r in rs])), max_seconds=max(r['seconds'] for r in rs),
            solved_mean_seconds=float(np.mean(solved)) if solved else None,
            capped_mean_seconds=float(np.mean(capped)) if capped else None,
            adverse_80pct_mean_seconds=.8 * (float(np.mean(solved)) if solved else cap_seconds) + .2 * cap_seconds,
            cap_scenario_seconds=cap_seconds, cap_scenario_measured=bool(capped))
    primary = 4096 * sum(v['mean_seconds'] for v in timings.values())
    # No extra holdout smoke is authorized. Conservatively cost holdouts like
    # primary searches, rather than assume the historical3.37/6.20 ratio.
    holdout = 1024 * timings['R']['mean_seconds'] if paired else 0
    projected = 1.15 * (primary + holdout) / efficiency
    adverse = 1.15 * (4096 * sum(v['adverse_80pct_mean_seconds'] for v in timings.values()) + holdout) / efficiency
    replay = 1.15 * sum(r['seconds'] for r in rows) / efficiency
    total = projected + replay + 180
    return dict(admitted=total <= 6480 and prepare_wall <= 1680, projected_seconds=projected,
                with_handoff_and_report_seconds=total, smoke_handoff_seconds=replay, report_reserve_seconds=180,
                adverse_80pct_projected_seconds=adverse, adverse_primary_solves_per_arm=3277,
                timings=timings, workers=workers, measured_cpu_efficiency=efficiency,
                smoke_wall_seconds=elapsed, prepare_wall_seconds=prepare_wall,
                paired=paired, primary_seeds=16, holdout_seeds=8 if paired else 0,
                rule='fixed complete roster; measured worker/concurrency projection x1.15 + handoff +180 <=6480s; prepare <=1680s',
                caveat='32 fixed primary searches; limited timing precision. Holdouts costed at primary mean. Adverse80% solves is a descriptive scenario, not efficacy-based sizing.')


class Runner(BaseRunner):
    execute = staticmethod(execute)

    def __init__(self, args):
        super().__init__(args)
        self.ta_bank, targets = load()
        if self.ta_bank['inputs'] != self.bank['inputs']:
            raise ValueError('bank domains differ')
        self.cells.update(targets)
        self.ids = target_ids(self.bank, self.ta_bank)
        self.cells.update({c['id']: dict(id=c['id'], labels=c['labels'])
                           for c in self.bank['cells'] if c['id'] in self.ids['holdout']})
        if len(self.ids['then_addition']) != 16 or len(self.ids['holdout']) != 8 or not set(sum(self.ids.values(), [])) <= set(self.cells):
            raise ValueError('target roster or labels incomplete')
        _, self.libraries = pinned_history()
        self.history, self.historical_provenance = historical()
        if self.history['libraries.json'] != self.libraries or self.history['freeze.json']['libraries_hash'] != digest(self.libraries):
            raise ValueError('historical whole libraries changed')
        self.laws = self.history['operator_laws.json']
        expected = old_schedule(self.ids, 16)
        saved_schedule = self.history['schedule.json']
        self.references = [r for r in self.history['search.jsonl'] if r['phase'] in self.ids]
        indexed = {row_key(r): r for r in self.references}
        if (len(indexed) != len(self.references) or len(indexed) != len(expected)
                or sorted(saved_schedule, key=row_key) != sorted(expected, key=row_key)
                or any(row_key(e) not in indexed or any(indexed[row_key(e)][k] != v for k, v in e.items()) for e in expected)):
            raise ValueError('full historical metadata/roster mismatch')
        # Validate table, initial population, cases, budgets and paired arm metadata
        # over ALL historical searches; representative replay is additional.
        table_hashes = {tid: Decoder(r['tables']['C']).hash() for tid, r in self.corpora.items()}
        for e in expected:
            r = indexed[row_key(e)]
            c = indexed[(*row_key(e)[:3], 'C')]
            if (r['family'] != r['corpus'][:2] or r['cap'] != 524288 or r['pop_size'] != 256
                    or r['table_hash'] != table_hashes[r['corpus']]
                    or r['training_indices'] != np.random.default_rng([r['seed'], 0]).choice(len(self.bank['inputs']), 64, replace=False).tolist()
                    or r['initial_tokens_hash'] != c['initial_tokens_hash']
                    or r['initial_source_hash'] != r['table_hash'] or r['initial_reencoded']
                    or r['evaluations'] != r['generations'] * 256 or not 0 < r['evaluations'] <= 524288
                    or not r['solved'] and r['evaluations'] != 524288):
                raise ValueError('historical pairing metadata changed')
        self.replay = []
        for tid in CORPORA:
            for arm in ('W', 'C'):
                r = min((r for r in self.references if r['corpus'] == tid and r['arm'] == arm and r['phase'] == 'then_addition'), key=row_key)
                self.replay.append({k: ('replay' if k == 'phase' else r[k]) for k in ('phase', 'corpus', 'family', 'cell', 'seed', 'arm')})
        self.rosters = {str(p): roster(self.ids, p) for p in (True, False)}
        self.smokes = {str(p): timing_roster(self.ids, p) for p in (True, False)}
        historical_seeds = {r['seed'] for r in self.references} | {r['seed'] for r in self.saved['schedule.json']}
        if (historical_seeds & {r['seed'] for r in self.rosters['False']}
                or {r['seed'] for r in self.smokes['True']} & (historical_seeds | {r['seed'] for r in self.rosters['False']})):
            raise ValueError('new seed overlap')
        self.hashes = implementation_hashes()
        self.config.update(task='2026-10-09-1606', arms=['R'], implementation_hashes=self.hashes,
                           then_addition_sha256=TA_SHA, method='historical W chain blocks; R neutral unrepaired-boundary refresh',
                           seed_base='1036 exact roster, fallback206610091606, smoke+2000000',
                           ordinary_variation=dict(crossover=.7, mutation=.03, elites=2, selection='lexicase'),
                           scope='development-bank boundary policy and downstream effects; externally fitted C')
        for name, value in (('config.json', self.config), ('historical_provenance.json', self.historical_provenance),
                            ('target_banks.json', dict(then_addition=self.ta_bank, comparison_gate=self.bank)),
                            ('candidate_schedules.json', self.rosters), ('libraries.json', self.libraries), ('operator_laws.json', self.laws),
                            ('preparation_schedules.json', dict(replay=self.replay, smoke=self.smokes))):
            write_json(self.out, name, value)

    def envelope(self, r, off=False):
        tid = r['corpus']
        job = (self.cells[r['cell']], r['arm'], self.corpora[tid]['tables']['C'],
               r['seed'], 524288, 256, self.bank['inputs'], 'v2_rmin_first')
        return job, r, self.libraries[tid]['fragments'], self.diagnostic_inputs, off

    def freeze(self):
        return dict(implementation_hashes=self.hashes, libraries_hash=digest(self.libraries),
                    historical_provenance_hash=digest(self.historical_provenance), operator_laws_hash=digest(self.laws), bank_sha256=BANK_SHA, then_addition_sha256=TA_SHA,
                    table_hashes={tid: Decoder(r['tables']['C']).hash() for tid, r in self.corpora.items()},
                    roster_hashes={k: digest(v) for k, v in self.rosters.items()}, smoke_hashes={k: digest(v) for k, v in self.smokes.items()},
                    replay_hash=digest(self.replay), frozen_before_scoring=True)

    def prepare(self):
        self.validation['forced_edits'] = audit(self.corpora, self.libraries)
        replayed = self.jobs(self.replay)
        refs = {row_key(r): r for r in self.references}
        differences = [dict(key=list(row_key(r)), fields=[k for k in FIELDS if r[k] != refs[row_key(r)][k]])
                       for r in replayed if any(r[k] != refs[row_key(r)][k] for k in FIELDS)]
        paired = not differences
        self.validation['historical_replay'] = dict(passed=paired, rows=32, fields=FIELDS, differences=differences)
        self.validation['historical_metadata'] = dict(passed=True, rows=len(self.references), full_roster=True)
        smoke_start = time.monotonic()
        smoke = self.jobs(self.smokes[str(paired)])
        admission = admit(smoke, time.monotonic() - smoke_start, time.monotonic() - self.started, paired, self.args.workers)
        self.validation.update(passed=True, smoke_rows=len(smoke), elite_exclusion=True)
        p = dict(admitted=admission['admitted'], workers=self.args.workers, historical_paired=paired,
                 freeze=self.freeze(), validation=self.validation, admission=admission, timing_rows=smoke,
                 historical_replay_worker_seconds=sum(r['seconds'] for r in replayed),
                 resolution_cost=self.history['preparation.json']['resolution_cost'])
        for name, value in (('freeze.json', p['freeze']), ('validation.json', self.validation), ('preparation.json', p),
                            ('schedule.json', self.rosters[str(paired)])):
            write_json(self.out, name, value)
        print(json.dumps(admission, indent=2), flush=True)
        if not p['admitted']:
            raise ValueError('runtime admission failed; stop for steward')

    def score(self):
        if not self.args.preparation:
            raise ValueError('requires admitted preparation')
        path = Path(self.args.preparation)
        p = json.loads(path.read_bytes())
        paired = p['historical_paired']
        if (not p['admitted'] or not p['validation']['passed'] or p['workers'] != self.args.workers
                or p['freeze'] != self.freeze()
                or json.loads((path.parent / 'schedule.json').read_bytes()) != self.rosters[str(paired)]):
            raise ValueError('preparation/source/code/backend/roster changed')
        self.config['arms'] = ['R'] if paired else ['W', 'R']
        self.config['preparation_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json(self.out, 'config.json', self.config)
        for name in ('freeze.json', 'preparation.json', 'schedule.json'):
            (self.out / name).write_bytes((path.parent / name).read_bytes())
        smoke = self.jobs(self.smokes[str(paired)])
        refs = {row_key(r): r for r in p['timing_rows']}
        if (len(refs) != 32 or {row_key(r) for r in smoke} != set(refs)
                or any(any(r[k] != refs[row_key(r)][k] for k in FIELDS) for r in smoke)):
            raise ValueError('smoke handoff scientific payload mismatch')
        write_json(self.out, 'validation.json', dict(passed=True, historical_paired=paired, smoke_replay_rows=32))
        if self.args.validate_preparation:
            print('All32 smoke payloads matched; no efficacy searches.', flush=True)
            return
        rows = self.jobs(self.rosters[str(paired)])
        historical_rows = [r for r in self.references if r['arm'] in ('W', 'C')] if paired else []
        write_json(self.out, 'historical_references.json', dict(paired=paired, rows=historical_rows))
        if paired:
            refs = {row_key(r): r for r in historical_rows}
            for r in rows:
                w = refs[(*row_key(r)[:3], 'W')]
                if any(r[k] != w[k] for k in ('initial_tokens_hash', 'training_indices', 'table_hash', 'cap', 'pop_size')):
                    raise ValueError('R/historical pairing changed')
        report(self.out, rows, self.rosters[str(paired)], p, historical_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--preparation')
    parser.add_argument('--validate-preparation', action='store_true')
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--deadline-seconds', type=int, default=1680)
    args = parser.parse_args()
    if args.workers != 10:
        parser.error('approved admission requires10 workers')
    Runner(args).run()


if __name__ == '__main__':
    main()
