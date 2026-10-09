"""1350 pre-solve fragment E versus its length/start-matched C-chain W_E."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import BANK_SHA, digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.fragment_operator import validate_edits
from experiments.chem_tape.fragment_report import row_key
from experiments.chem_tape.fragment_reuse_run import pinned_history, schedule as old_schedule
from experiments.chem_tape.fragment_run import Runner as BaseRunner, CORPORA, REPLAY_FIELDS
from experiments.chem_tape.fragment_run import execute as old_execute, implementation_hashes
from experiments.chem_tape.pre_solve_sources import load_sources, extract_partial
from experiments.chem_tape.pre_solve_report import report
from experiments.chem_tape.then_addition_bank import load, BANK_SHA as TA_SHA
from experiments.chem_tape.then_addition_run import PROVENANCE_SHA

ARMS = ('E', 'W_E')
BASE = 205610091350
PREP_TIMEOUT = 1800
SCORE_TIMEOUT = 9000
ADMISSION_SECONDS = 135 * 60
FIELDS = REPLAY_FIELDS + ('solver', 'operator')


def schedule(ids, n):
    return [dict(r, arm=arm) for r in old_schedule(dict(then_addition=ids, holdout=[]), n)
            if r['arm'] == 'C' for arm in ARMS]


def smoke_schedule(ids):
    return [dict(phase='smoke', corpus=f'{f}{ci % 8 + 1}', family=f, cell=cid,
                 arm=arm, seed=BASE + (f == 'PA') * 100000 + ci * 200)
            for ci, cid in enumerate(ids) for f in ('BE', 'PA') for arm in ARMS]


def execute(envelope):
    job, meta, fragments, diagnostic_inputs, off = envelope
    if meta['arm'] in ('C', 'F', 'W'):
        return old_execute(envelope)
    arm = 'F' if meta['arm'] == 'E' and not meta.get('fallback', False) else 'W'
    # Use exactly the reviewed executor; only adapt public arm names at the interface.
    adapted = dict(meta, arm=arm)
    result = old_execute((job, adapted, fragments, diagnostic_inputs, off))
    result.update(meta)
    return result


def admit(rows, smoke_wall, prepare_wall, workers=10):
    timings = {}
    for arm in ARMS:
        rs = [r for r in rows if r['arm'] == arm]
        if len(rs) != 32:
            raise ValueError('timing roster incomplete')
        timings[arm] = dict(n=32, solved=sum(r['solved'] for r in rs),
                            mean_seconds=float(np.mean([r['seconds'] for r in rs])),
                            max_seconds=max(r['seconds'] for r in rs),
                            worker_seconds=sum(r['seconds'] for r in rs))
    efficiency = min(workers, sum(r['seconds'] for r in rows) / smoke_wall)
    candidates = []
    for n in (16, 12):
        projected = 1.15 * 256 * n * sum(v['mean_seconds'] for v in timings.values()) / efficiency
        replay = 1.15 * sum(r['seconds'] for r in rows) / efficiency
        candidates.append(dict(seeds=n, searches_per_arm=256 * n, projected_seconds=projected,
                               smoke_handoff_seconds=replay, reporting_reserve_seconds=180,
                               fits=projected <= ADMISSION_SECONDS and projected + replay + 180 <= SCORE_TIMEOUT))
    chosen = next((c for c in candidates if c['fits']), None)
    return dict(admitted=chosen is not None and prepare_wall <= PREP_TIMEOUT,
                selected_seeds=chosen['seeds'] if chosen else None,
                projected_seconds=chosen['projected_seconds'] if chosen else None,
                timings=timings, measured_cpu_efficiency=efficiency, smoke_wall_seconds=smoke_wall,
                prepare_wall_seconds=prepare_wall, workers=workers, candidates=candidates,
                rule='timing only: measured projection x1.15 <=135min at16 else12; prepare<=30min; handoff/report fit150min',
                rate_caveat='Fixed representative32 searches/arm; solve counts descriptive, not used in admission')


class Runner(BaseRunner):
    arms = ARMS
    execute = staticmethod(execute)

    def __init__(self, args):
        super().__init__(args)
        self.ta_bank, targets = load()
        if self.ta_bank['inputs'] != self.bank['inputs']:
            raise ValueError('bank domains differ')
        self.cells.update(targets)
        self.ids = self.ta_bank['selected_ids']
        self.collection, self.historical, self.provenance, self.provenance_sha = load_sources()
        _, self.exact_libraries = pinned_history()
        self.references = [r for r in self.historical['search.jsonl'] if r['phase'] == 'then_addition']
        expected = old_schedule(dict(then_addition=self.ids, holdout=[]), 16)
        if (len(self.references) != len(expected)
                or {row_key(r) for r in self.references} != {row_key(r) for r in expected}
                or any(any(r[k] != v for k, v in e.items())
                       for r, e in zip(sorted(self.references, key=row_key), sorted(expected, key=row_key)))):
            raise ValueError('historical then-addition roster changed')
        self.replay = []
        for tid in CORPORA:
            for arm in ('C', 'F', 'W'):
                r = min((r for r in self.references if r['corpus'] == tid and r['arm'] == arm), key=row_key)
                self.replay.append({k: ('replay' if k == 'phase' else r[k])
                                    for k in ('phase', 'corpus', 'family', 'cell', 'seed', 'arm')})
        self.rosters = {str(n): schedule(self.ids, n) for n in (16, 12)}
        self.smoke = smoke_schedule(self.ids)
        if (len(self.smoke) != 64 or {r['corpus'] for r in self.smoke} != set(CORPORA)
                or {r['seed'] for r in self.smoke} & ({r['seed'] for r in expected}
                    | {r['seed'] for r in self.collection} | {r['seed'] for r in self.saved['schedule.json']})):
            raise ValueError('smoke coverage/seed collision')
        self.hashes = implementation_hashes()
        self.hashes['pre_solve_run.py'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.config.update(task='2026-10-09-1350', arms=ARMS, seed_base='1036 same score seeds; smoke205610091350',
                           implementation_hashes=self.hashes, then_addition_sha256=TA_SHA,
                           partial_historical_provenance_sha256=self.provenance_sha,
                           method='pre-solve S minimum-slot/cp64,128,256; -cells,-occurrences,-length,tokens; top32; matched W_E',
                           scope='then-addition development procedure test, conditional on exact-solver C')
        for name, value in (('config.json', self.config), ('target_banks.json', dict(then_addition=self.ta_bank, comparison_gate=self.bank)),
                            ('archive_provenance.json', self.provenance), ('candidate_schedules.json', self.rosters),
                            ('preparation_schedules.json', dict(smoke=self.smoke, replay=self.replay))):
            write_json(self.out, name, value)

    def envelope(self, r, off=False):
        tid = r['corpus']
        lib = self.exact_libraries[tid] if r['arm'] in ('C', 'F', 'W') else self.libraries[tid]
        fallback = r['arm'] in ARMS and not lib['fragments']
        fragments = self.exact_libraries[tid]['fragments'] if fallback else lib['fragments']
        meta = dict(r)
        if r['arm'] in ARMS:
            meta['fallback'] = fallback
        job = (self.cells[r['cell']], r['arm'], self.corpora[tid]['tables']['C'],
               r['seed'], self.config['cap'], 256, self.bank['inputs'], 'v2_rmin_first')
        return job, meta, fragments, self.diagnostic_inputs, off

    def laws(self):
        result = {}
        for tid, lib in self.libraries.items():
            fs = lib['fragments'] or self.exact_libraries[tid]['fragments']
            counts = Counter(len(f['tokens']) for f in fs)
            result[tid] = dict(length_counts=dict(counts), length_probabilities={str(k): v / len(fs) for k, v in counts.items()},
                               rate=.2, start='uniform0..32-length', fallback=not bool(lib['fragments']),
                               empty_library_law='both E/W_E use historical whole-library lengths and C-chain content',
                               suffix='unchanged0843 conditional window+next preimage; decoded suffix retained')
        # Round-trip JSON normalizes integer histogram keys for freeze verification.
        return json.loads(json.dumps(result))

    def freeze(self):
        return dict(frozen_before_scoring=True, implementation_hashes=self.hashes,
                    bank_sha256=BANK_SHA, then_addition_sha256=TA_SHA,
                    exact_source_provenance_sha256=PROVENANCE_SHA,
                    archive_provenance_sha256=self.provenance_sha,
                    libraries_hash=digest(self.libraries), operator_laws_hash=digest(self.laws()),
                    table_hashes={tid: Decoder(r['tables']['C']).hash() for tid, r in self.corpora.items()},
                    candidate_schedule_hashes={n: digest(rs) for n, rs in self.rosters.items()},
                    smoke_schedule_hash=digest(self.smoke), replay_schedule_hash=digest(self.replay))

    def prepare(self):
        built = []
        extraction_start = time.monotonic()
        envelopes = [(tid, [r for r in self.collection if r['corpus'] == tid],
                      self.bank['inputs'], self.cells, self.indices) for tid in CORPORA]

        def save(record):
            built.append(record)
            self.libraries[record['corpus']] = record['whole_corpus']
            write_json(self.out, 'libraries.json', self.libraries)

        if not run_jobs(self.pool, extract_partial, envelopes, self.deadline, save):
            raise TimeoutError('partial extraction incomplete')
        if set(self.libraries) != set(CORPORA):
            raise ValueError('missing corpus libraries')
        extraction_wall = time.monotonic() - extraction_start
        manifest = {r['corpus']: r['manifest'] for r in built}
        write_json(self.out, 'source_manifest.json', manifest)
        write_json(self.out, 'activity.json', {r['corpus']: r['activity'] for r in built})
        laws = self.laws()
        write_json(self.out, 'operator_laws.json', laws)
        from experiments.chem_tape.composition_search import outputs
        padded = {}
        for tid, lib in self.libraries.items():
            values = outputs([f['tokens'] + [0] * (32 - len(f['tokens'])) for f in lib['fragments']], self.bank['inputs'], 'v2_rmin_first') if lib['fragments'] else []
            padded[tid] = [dict(fragment_index=i, cell=cid, tokens=lib['fragments'][i]['tokens'])
                           for i, v in enumerate(values) for cid in self.ids
                           if np.array_equal(v, self.cells[cid]['labels'])]
        write_json(self.out, 'padded_solutions.json', dict(filtered=False, hits=padded,
                   tests=sum(len(lib['fragments']) for lib in self.libraries.values()) * len(self.ids)))
        audit = {tid + '|whole': (lib if lib['fragments'] else self.exact_libraries[tid]) for tid, lib in self.libraries.items()}
        self.validation['edits'] = validate_edits(self.corpora, audit, arms=('F', 'W'))
        replayed = self.jobs(self.replay)
        refs = {row_key(r): r for r in self.references}
        differences = [dict(key=list(row_key(r)), fields=[k for k in FIELDS if r[k] != refs[row_key(r)][k]])
                       for r in replayed if any(r[k] != refs[row_key(r)][k] for k in FIELDS)]
        paired = not differences
        self.validation['historical_replay'] = dict(passed=paired, rows=len(replayed), fields=FIELDS,
            differences=differences, status='paired' if paired else 'ALL C/F/W historical references only')
        smoke_start = time.monotonic()
        smoke = self.jobs(self.smoke)
        admission = admit(smoke, time.monotonic() - smoke_start, time.monotonic() - self.started, self.args.workers)
        self.validation.update(passed=True, source_attempts=len(self.collection),
                               selected_tapes=sum(m['tapes'] for m in manifest.values()),
                               library_sizes={tid: len(lib['fragments']) for tid, lib in self.libraries.items()},
                               fallback_corpora=[tid for tid, law in laws.items() if law['fallback']],
                               paired_initial_tokens=True, elite_exclusion=True, smoke_rows=len(smoke))
        shared = [r for r in self.saved['search.jsonl'] if r['phase'] == 'collection']
        p = dict(admitted=admission['admitted'], workers=self.args.workers, freeze=self.freeze(),
                 admission=admission, validation=self.validation, timing_rows=smoke,
                 historical_paired=paired, source_manifest_hash=digest(manifest),
                 extraction_cost=dict(worker_seconds=sum(r['seconds'] for r in built), wall_seconds=extraction_wall,
                                      scope='full source validation, activity/extraction and stack diagnostics'),
                 partial_collection_cost=dict(worker_seconds=sum(r['worker_seconds'] for r in self.collection),
                     archive_verification_seconds=sum(r['archive_verification_seconds'] for r in self.collection),
                     evaluations=sum(r['evaluations'] for r in self.collection), attempts=len(self.collection), sunk=True),
                 shared_exact_collection_cost=dict(worker_seconds=sum(r['seconds'] for r in shared), sunk=True),
                 historical_replay_cost=dict(worker_seconds=sum(r['seconds'] for r in replayed)),
                 resolution_cost=dict(source_worker_seconds_per_corpus=sum(r['worker_seconds'] for r in self.collection) / 16,
                     exact_source_worker_seconds_per_corpus=sum(r['seconds'] for r in shared) / 16,
                     library_worker_seconds_per_corpus=sum(r['seconds'] for r in built) / 16,
                     fit_worker_seconds_per_corpus=sum(r['fit_seconds'] for r in self.corpora.values()) / 16,
                     workers=self.args.workers, reporting_queue_seconds=600, agent_hours=3))
        for name, value in (('freeze.json', p['freeze']), ('validation.json', self.validation), ('preparation.json', p)):
            write_json(self.out, name, value)
        print(json.dumps(admission, indent=2), flush=True)
        if not p['admitted']:
            raise ValueError('runtime admission failed; feasibility stop')
        write_json(self.out, 'schedule.json', self.rosters[str(admission['selected_seeds'])])

    def score(self):
        if not self.args.preparation:
            raise ValueError('requires admitted preparation')
        path = Path(self.args.preparation)
        p = json.loads(path.read_bytes())
        self.libraries = json.loads((path.parent / 'libraries.json').read_bytes())
        n = p['admission']['selected_seeds']
        manifest = json.loads((path.parent / 'source_manifest.json').read_bytes())
        if (not p['admitted'] or not p['validation']['passed'] or n not in (16, 12)
                or p['workers'] != self.args.workers or p['freeze'] != self.freeze()
                or digest(manifest) != p['source_manifest_hash']
                or json.loads((path.parent / 'operator_laws.json').read_bytes()) != self.laws()
                or set(self.libraries) != set(CORPORA)
                or any(digest(lib['fragments']) != lib['hash'] for lib in self.libraries.values())):
            raise ValueError('preparation source/code/backend/library/law/roster changed')
        for name in ('libraries.json', 'operator_laws.json', 'freeze.json', 'source_manifest.json', 'activity.json', 'padded_solutions.json', 'preparation.json'):
            (self.out / name).write_bytes((path.parent / name).read_bytes())
        write_json(self.out, 'schedule.json', self.rosters[str(n)])
        self.config['preparation_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json(self.out, 'config.json', self.config)
        smoke = self.jobs(self.smoke)
        refs = {row_key(r): r for r in p['timing_rows']}
        if (len(refs) != 64 or {row_key(r) for r in smoke} != set(refs)
                or any(any(r[k] != refs[row_key(r)][k] for k in FIELDS + ('fallback',)) for r in smoke)):
            raise ValueError('smoke handoff scientific payload changed')
        write_json(self.out, 'validation.json', dict(passed=True, smoke_replay_rows=64, historical_paired=p['historical_paired']))
        if self.args.validate_preparation:
            print('All64 smoke payloads matched; no efficacy searches.', flush=True)
            return
        rows = self.jobs(self.rosters[str(n)])
        keys = {(r['corpus'], r['cell'], r['seed']) for r in rows}
        historical = [r for r in self.references if (r['corpus'], r['cell'], r['seed']) in keys]
        write_json(self.out, 'historical_references.json', dict(paired=p['historical_paired'], rows=historical))
        report(self.out, rows, self.rosters[str(n)], self.libraries, p, historical)


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
