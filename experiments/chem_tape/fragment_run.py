"""0843 preparation/admission and frozen complete-roster fragment scoring.

Run with RAYON_NUM_THREADS=1 and RUN_DIR. Preparation is also the non-scoring smoke.
"""

import argparse
from collections import defaultdict
import hashlib
import importlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.stats import t

from experiments.chem_tape.comparison_gate_bank import BANK_SHA, TRAINING, digest, load_training
from experiments.chem_tape.comparison_gate_run import CAP
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import search, outputs, Decoder
from experiments.chem_tape.fragment_library import extract_corpus
from experiments.chem_tape.fragment_operator import ARMS, BlockOperator, validate_edits
from experiments.chem_tape.fragment_report import row_key, report
from experiments.chem_tape.solver_corpus_fit import seed_for, transition_counts, fit
from experiments.chem_tape.then_addition_run import frozen_source, PROVENANCE_SHA

BASE = 203610090843  # task timestamp + 1e9; disjoint from the historical roster
CORPORA = [f'{f}{i}' for i in range(1, 9) for f in TRAINING]
PREP_TIMEOUT = 2700
SCORE_TIMEOUT = 11700
RESERVE = 240


def implementation_hashes():
    # Include transitive locally loaded dependencies and the actual Rust extension.
    result = {'fragment_run.py': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    importlib.import_module('_folding_rust._folding_rust')
    for name, module in sorted(sys.modules.items()):
        if name.startswith(('experiments.chem_tape.', 'folding_evolution.chem_tape.', '_folding_rust')):
            path = getattr(module, '__file__', None)
            if path and Path(path).is_file():
                result[name] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return result


def schedule(n):
    return [dict(phase='training', family=tid[:2], corpus=tid, cell=cid, arm=arm,
                 seed=seed_for(0, tid[:2], int(tid[2:]) - 1, ci, si, BASE))
            for tid in CORPORA for ci, cid in enumerate(TRAINING[tid[:2]])
            for si in range(n) for arm in ARMS]


def smoke_schedule():
    rows = []
    for ci in range(4):
        for si in range(8):
            family = 'BE' if si < 4 else 'PA'
            k = (ci * 4 + si % 4) % 8
            for arm in ARMS:
                rows.append(dict(phase='smoke', family=family, corpus=f'{family}{k + 1}',
                                 cell=TRAINING[family][ci], arm=arm,
                                 seed=seed_for(1, family, k, ci, si, BASE)))
    if len(rows) != 128 or {r['corpus'] for r in rows} != set(CORPORA):
        raise ValueError('smoke must cover all corpora')
    return rows


def replay_schedule(saved):
    rows = []
    for tid in CORPORA:
        rows.append(next({k: r[k] for k in ('phase', 'family', 'corpus', 'cell', 'arm', 'seed')}
                         for r in saved['search.jsonl'] if r['phase'] == 'training' and r['corpus'] == tid and r['arm'] == 'C'))
    return rows


# The allowlist is fixed before running: runtime/bookkeeping and new diagnostics excluded.
REPLAY_FIELDS = ('cell', 'arm', 'seed', 'cap', 'pop_size', 'solved', 'evaluations',
                 'shortcuts', 'unique_shortcuts', 'training_perfect_individuals', 'generations',
                 'training_indices', 'curve', 'table_hash', 'initial_tokens_hash',
                 'initial_source_hash', 'initial_reencoded')


def substantive(row):
    return {k: row[k] for k in REPLAY_FIELDS}


def execute(envelope):
    job, meta, fragments, diagnostic_inputs, operator_off = envelope
    operator = None if operator_off else BlockOperator(meta['arm'], fragments, meta['seed'], diagnostic_inputs)
    row = search(job, return_solver=True, child_transform=operator)
    if row['solved'] and not np.array_equal(outputs([row['solver']], job[6], job[7])[0], job[0]['labels']):
        raise ValueError('solver failed full-domain recheck')
    row.update(meta)
    if operator is not None:
        row['operator'] = operator.stats
    return row


def precision(saved):
    rng = np.random.default_rng(202610090844)
    by = defaultdict(list)
    for r in saved['search.jsonl']:
        if r['phase'] == 'training' and r['arm'] == 'C':
            by[r['corpus'], r['cell']].append(np.log(r['evaluations'] if r['solved'] else 2 * CAP))
    samples = {}
    for n in (16, 24, 32):
        sds = []
        for _ in range(512):
            contrasts = []
            for tid in CORPORA:
                differences = []
                for cid in TRAINING[tid[:2]]:
                    x = by[tid, cid]
                    if len(x) != 16:
                        raise ValueError('historical C precision roster incomplete')
                    differences.append(rng.choice(x, size=n).mean() - rng.choice(x, size=n).mean())
                contrasts.append(np.mean(differences))
            sds.append(np.std(contrasts, ddof=1))
        samples[n] = dict(median_corpus_sd=float(np.median(sds)),
                          sd_quantiles=np.quantile(sds, [.025, .5, .975]).tolist(),
                          median_half_width_factor=float(np.exp(t.ppf(.975, 15) * np.median(sds) / 4)))
    return dict(seed=202610090844, replicates=512,
                procedure='within each historical corpus/cell, independent with-replacement C pseudo-arms of size n; equal-cell mean log contrasts; SD across 16 corpora',
                empirical=samples, steward_scenarios={n: dict(sd=sd, half_width_factor=float(np.exp(t.ppf(.975, 15) * sd / 4)))
                                                    for n, sd in ((16, .27), (24, .22), (32, .19))},
                caveat='C resampling estimates a noise scenario, not F benefit heterogeneity. Original .27/.19 calculation was not saved by the steward; this is an explicit reproducible reconstruction, not asserted identical.')


def admit(rows, elapsed, workers):
    timings = {}
    for arm in ARMS:
        rs = [r for r in rows if r['arm'] == arm]
        if len(rs) != 32:
            raise ValueError('timing roster incomplete')
        timings[arm] = dict(n=len(rs), solved=sum(r['solved'] for r in rs),
                            mean_seconds=float(np.mean([r['seconds'] for r in rs])),
                            max_seconds=max(r['seconds'] for r in rs),
                            worker_seconds=sum(r['seconds'] for r in rs),
                            capped=sum(not r['solved'] for r in rs),
                            seconds_per_evaluation=sum(r['seconds'] for r in rs) / sum(r['evaluations'] for r in rs),
                            expected_full_solves={n: int(round(64 * n * sum(r['solved'] for r in rs) / len(rs))) for n in (32, 24, 16)})
    replay_seconds = sum(v['worker_seconds'] for v in timings.values()) * 1.15 / workers
    candidates = []
    for n in (32, 24, 16):
        projected = sum(64 * n * v['mean_seconds'] for v in timings.values()) * 1.15 / workers
        candidates.append(dict(seeds=n, searches_per_arm=64 * n, projected_seconds=projected,
                               with_reserve_seconds=projected + replay_seconds + RESERVE,
                               fits=projected <= 3.5 * 3600 and projected + replay_seconds + RESERVE <= SCORE_TIMEOUT))
    selected = next((c for c in candidates if c['fits']), None)
    return dict(admitted=selected is not None and elapsed <= PREP_TIMEOUT, selected_seeds=selected['seeds'] if selected else None,
                projected_seconds=selected['projected_seconds'] if selected else None,
                prepare_wall_seconds=elapsed, workers=workers, timings=timings, candidates=candidates,
                scoring_timeout_seconds=SCORE_TIMEOUT, prepare_timeout_seconds=PREP_TIMEOUT, reserve_seconds=RESERVE,
                smoke_replay_projected_seconds=replay_seconds,
                rule='largest 32/24/16 with sum(64*n*arm_mean_worker_s)*1.15/workers <=12600 and +smoke_replay+240 <=11700; preparation <=2700',
                rate_caveat='32 smoke searches per arm across all corpora; not efficacy and limited rate precision')


class Runner:
    arms = ARMS

    def __init__(self, args):
        os.environ['RAYON_NUM_THREADS'] = '1'
        self.args, self.started = args, time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 120
        self.out = Path(os.environ['RUN_DIR'])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / 'config.json').exists():
            raise ValueError('fresh RUN_DIR required')
        self.bank, self.cells = load_training()
        self.saved, self.source = frozen_source()
        self.corpora = self.saved['corpora.json']
        self.hashes = implementation_hashes()
        self.indices = np.random.default_rng(0).choice(len(self.bank['inputs']), 96, replace=False).tolist()
        self.diagnostic_inputs = [self.bank['inputs'][i] for i in self.indices[:4]]
        self.libraries, self.rows, self.validation = {}, [], {}
        self.config = dict(task='2026-10-09-0843', arguments=vars(args), prepare_only=args.prepare,
                           git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                           implementation_hashes=self.hashes, source_provenance_sha256=PROVENANCE_SHA,
                           bank_sha256=BANK_SHA, seed_base=BASE, cap=CAP, population=256,
                           rate=.2, operator_seed='[search_seed,4]', diagnostic_indices=self.indices[:4],
                           knockout_indices=self.indices, arms=ARMS,
                           method='LOO all-active 3-6 windows; >=2 cells; rank -cells,-count,-length,tokens; full-domain NOP-pad filter; top32, min8; uniform conditional window+next encoding',
                           replay_fields=REPLAY_FIELDS)
        for name, value in (('config.json', self.config), ('bank.json', self.bank), ('source_provenance.json', self.source)):
            write_json(self.out, name, value)
        (self.out / 'search.jsonl').touch()

    def envelope(self, r, off=False):
        key = r['corpus'] + '|' + r['cell']
        fragments = [] if off else self.libraries[key]['fragments']
        job = (self.cells[r['cell']], r['arm'], self.corpora[r['corpus']]['tables']['C'],
               r['seed'], CAP, 256, self.bank['inputs'], 'v2_rmin_first')
        return job, r, fragments, self.diagnostic_inputs, off

    def jobs(self, roster, off=False):
        expected = {row_key(r) for r in roster}
        rows = []
        envelopes = [self.envelope(r, off) for r in roster]
        with (self.out / 'search.jsonl').open('a', buffering=1) as stream:
            def save(r):
                k = row_key(r)
                if k not in expected:
                    raise ValueError('unexpected/duplicate result')
                expected.remove(k)
                if r['table_hash'] != Decoder(self.corpora[r['corpus']]['tables']['C']).hash():
                    raise ValueError('C table changed')
                if r['cap'] != CAP or r['pop_size'] != 256 or not 0 < r['evaluations'] <= CAP or r['evaluations'] % 256 or (not r['solved'] and r['evaluations'] != CAP):
                    raise ValueError('search budget changed')
                if r['training_indices'] != np.random.default_rng([r['seed'], 0]).choice(len(self.bank['inputs']), 64, replace=False).tolist():
                    raise ValueError('case draw changed')
                rows.append(r)
                stream.write(json.dumps(r, allow_nan=False) + '\n')
                write_json(self.out, 'progress.json', dict(completed=len(rows), total=len(roster), phase=r['phase']))
            if not run_jobs(self.pool, execute, envelopes, self.deadline, save) or expected:
                raise TimeoutError('incomplete roster; no efficacy decision')
        rows.sort(key=row_key)
        paired = defaultdict(list)
        for r in rows:
            paired[r['corpus'], r['cell'], r['seed']].append(r)
        if not off:
            for rs in paired.values():
                if {r['arm'] for r in rs} != set(self.arms) or len(rs) != len(self.arms) or len({r['initial_tokens_hash'] for r in rs}) != 1 or len({tuple(r['training_indices']) for r in rs}) != 1:
                    raise ValueError('paired initial tokens/cases mismatch')
                for r in rs:
                    stats = r['operator']
                    if stats['eligible_children'] != (r['generations'] - 1) * 254:
                        raise ValueError('elite was edited or variation count changed')
        return rows

    def prepare(self):
        collection = [r for r in self.saved['search.jsonl'] if r['phase'] == 'collection']
        if len(collection) != 16 * 4 * 48 or any(r['arm'] != 'G4' for r in collection):
            raise ValueError('G4 source roster changed')
        envelopes = [(tid, [r for r in collection if r['corpus'] == tid], self.bank['inputs'], self.cells, self.indices) for tid in CORPORA]
        built = []
        def save_library(record):
            built.append(record)
            self.libraries.update(record['libraries'])
            # Keep partial roster if any later gate fails.
            write_json(self.out, 'libraries.json', self.libraries)
        if not run_jobs(self.pool, extract_corpus, envelopes, self.deadline, save_library):
            raise TimeoutError('library preparation deadline exceeded')
        write_json(self.out, 'whole_libraries.json', {r['corpus']: r['whole_corpus'] for r in built})
        write_json(self.out, 'activity.json', {r['corpus']: r['activity'] for r in built})
        sizes = {k: len(v['fragments']) for k, v in self.libraries.items()}
        write_json(self.out, 'library_sizes.json', sizes)
        if len(sizes) != 64 or min(sizes.values()) < 8:
            write_json(self.out, 'preparation.json', dict(admitted=False, reason='library below eight', sizes=sizes))
            raise ValueError('library below eight; feasibility stop')
        self.validation['edits'] = validate_edits(self.corpora, self.libraries)
        self.validation['minimum_library_size'] = min(sizes.values())
        fit_started = time.monotonic()
        for tid in CORPORA:
            counts, _ = transition_counts([r for r in collection if r['corpus'] == tid], TRAINING[tid[:2]])
            fitted, _ = fit(counts)
            if not np.array_equal(fitted['C'], self.corpora[tid]['tables']['C']):
                raise ValueError('source collection does not reproduce frozen C')
        fit_seconds = time.monotonic() - fit_started
        self.validation['C_refit_check'] = dict(passed=True, corpora=16, seconds=fit_seconds,
                                               scope='verification only; searches always use original frozen C')
        replay = replay_schedule(self.saved)
        timing = smoke_schedule()
        score_seeds = {r['seed'] for r in schedule(32)}
        source_seeds = {r['seed'] for r in self.saved['schedule.json']}
        if score_seeds & source_seeds or {r['seed'] for r in timing} & (source_seeds | score_seeds):
            raise ValueError('source/smoke/scoring seed overlap')
        write_json(self.out, 'preparation_schedules.json', dict(replay=replay, smoke=timing))
        reference = {row_key(r): r for r in self.saved['search.jsonl'] if r['phase'] == 'training' and r['arm'] == 'C'}
        replayed = self.jobs(replay, off=True)
        if any(substantive(r) != substantive(reference[row_key(r)]) for r in replayed):
            raise ValueError('operator-off historical C replay changed')
        self.validation['C_replay'] = dict(passed=True, rows=len(replayed), fields=REPLAY_FIELDS)
        write_json(self.out, 'precision.json', precision(self.saved))
        smoke_start = time.monotonic()
        smoke = self.jobs(timing)
        elapsed = time.monotonic() - self.started
        admission = admit(smoke, elapsed, self.args.workers)
        build_seconds = sum(r['seconds'] for r in built)
        # Eight seeds/cell, 8 protected holdouts plus 16 then-addition development cells.
        reuse_searches_per_arm = 16 * (8 + 16) * 8
        reuse = dict(seeds_per_cell=8, cells_per_corpus=24, searches_per_arm=reuse_searches_per_arm,
                     arms=['F', 'C'], price_only=True,
                     library_build_worker_seconds=build_seconds,
                     library_build_queue_seconds=1.15 * build_seconds / self.args.workers,
                     scoring_queue_seconds=1.15 * reuse_searches_per_arm * sum(admission['timings'][a]['mean_seconds'] for a in ('F', 'C')) / self.args.workers,
                     validation_and_reporting_queue_seconds=600, agent_hours=2.5,
                     caveat='extrapolation from training smoke; held-out/then-addition difficulty can differ; full build uses cached corpus extraction and no scored reuse')
        reuse['complete_expected_hours'] = (reuse['library_build_queue_seconds'] + reuse['scoring_queue_seconds'] + 600) / 3600 + reuse['agent_hours']
        self.validation.update(passed=True, source_rows=len(collection), source_hash=PROVENANCE_SHA,
                               smoke_rows=len(smoke), paired_initial_tokens=True, elite_exclusion=True,
                               smoke_wall_seconds=time.monotonic() - smoke_start)
        write_json(self.out, 'validation.json', self.validation)
        freeze = dict(frozen_before_scoring=True, implementation_hashes=self.hashes, bank_sha256=BANK_SHA,
                      source_provenance_sha256=PROVENANCE_SHA, libraries_hash=digest(self.libraries),
                      whole_libraries_hash=digest({r['corpus']: r['whole_corpus'] for r in built}),
                      table_hashes={tid: Decoder(r['tables']['C']).hash() for tid, r in self.corpora.items()},
                      smoke_schedule_hash=digest(timing), schedule_hash=digest(schedule(admission['selected_seeds'])) if admission['admitted'] else None)
        write_json(self.out, 'freeze.json', freeze)
        prepared = dict(admitted=admission['admitted'], workers=self.args.workers, implementation_hashes=self.hashes,
                        freeze=freeze, admission=admission, validation=self.validation,
                        timing_rows=smoke, library_sizes=sizes, reuse_price=reuse,
                        resolution_cost=dict(source_collection_worker_seconds_per_corpus=sum(r['seconds'] for r in collection) / 16,
                                             fit_worker_seconds_per_corpus=fit_seconds / 16,
                                             library_worker_seconds_per_corpus=build_seconds / 16,
                                             workers=self.args.workers, reporting_queue_seconds=600, agent_hours=2.5))
        write_json(self.out, 'preparation.json', prepared)
        print(json.dumps(dict(admission=admission, reuse_price=reuse), indent=2), flush=True)
        if not admission['admitted']:
            raise ValueError('runtime admission failed; feasibility stop')
        write_json(self.out, 'schedule.json', schedule(admission['selected_seeds']))

    def score(self):
        if not self.args.preparation:
            raise ValueError('scoring requires admitted preparation')
        path = Path(self.args.preparation)
        raw = path.read_bytes()
        p = json.loads(raw)
        self.libraries = json.loads((path.parent / 'libraries.json').read_bytes())
        freeze = p['freeze']
        n = p['admission']['selected_seeds']
        if not p['admitted'] or not p['validation']['passed'] or p['workers'] != self.args.workers or n not in (16, 24, 32) or p['implementation_hashes'] != self.hashes:
            raise ValueError('preparation is not admitted or implementation changed')
        roster = schedule(n)
        if (freeze['bank_sha256'] != BANK_SHA or freeze['source_provenance_sha256'] != PROVENANCE_SHA
            or not freeze['frozen_before_scoring'] or freeze['libraries_hash'] != digest(self.libraries)
            or freeze['schedule_hash'] != digest(roster)
            or freeze['table_hashes'] != {tid: Decoder(r['tables']['C']).hash() for tid, r in self.corpora.items()}
            or freeze['smoke_schedule_hash'] != digest(smoke_schedule()) or len(p['timing_rows']) != 128
            or set(self.libraries) != {tid + '|' + cid for tid in CORPORA for cid in TRAINING[tid[:2]]}):
            raise ValueError('preparation source/library/table/roster mismatch')
        self.config['preparation_sha256'] = hashlib.sha256(raw).hexdigest()
        write_json(self.out, 'config.json', self.config)
        for name, value in (('freeze.json', freeze), ('libraries.json', self.libraries), ('schedule.json', roster), ('preparation.json', p)):
            write_json(self.out, name, value)
        # Smoke replay catches implementation/backend nondeterminism before scientific scoring.
        smoke = self.jobs(smoke_schedule())
        smoke_fields = REPLAY_FIELDS + ('solver', 'operator')
        references = {row_key(r): r for r in p['timing_rows']}
        if any({k: r[k] for k in smoke_fields} != {k: references[row_key(r)][k] for k in smoke_fields} for r in smoke):
            raise ValueError('smoke replay changed scientific payload')
        write_json(self.out, 'validation.json', dict(passed=True, smoke_replay_rows=128, fields=smoke_fields))
        if self.args.validate_preparation:
            print('Preparation handoff and all 128 smoke payload replays passed; no efficacy searches.', flush=True)
            return
        rows = self.jobs(roster)
        report(self.out, rows, roster, self.libraries, p)

    def run(self):
        self.pool = mp.get_context('spawn').Pool(self.args.workers)
        try:
            if self.args.prepare:
                self.prepare()
            else:
                self.score()
        finally:
            self.pool.terminate()
            self.pool.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--preparation')
    parser.add_argument('--validate-preparation', action='store_true', help='validate scoring handoff and replay smoke, then exit without scoring')
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--deadline-seconds', type=int, default=2580)
    args = parser.parse_args()
    Runner(args).run()


if __name__ == '__main__':
    main()
