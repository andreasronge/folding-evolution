"""0125 frozen K replacement on the exact 1548 row F roster."""

import argparse
import gzip
import hashlib
import importlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.comparison_gate_run import CAP, Runner as SearchRunner
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.solver_corpus_fit import emitted, validate_table
from experiments.chem_tape.then_addition_run import (
    Runner as FrozenRunner, frozen_source, fresh_schedule,
)
from experiments.chem_tape import then_addition_bank as bank_module

SOURCE_COMMIT = '45b2bdb2cbe5dee7ef04c3b5ebc10c54ce3e233a'
DATA = Path(__file__).with_name('data') / 'then_addition_1548_frozen'
PROVENANCE_SHA = '5f3987bb2ff33f2ad24b1db4969b941a7dc1a1be806045c1aa705136761c5ea9'
TIMING_FIELDS = {'seconds', 'decode_seconds', 'budget_seconds', 'verification_seconds'}


def key(row):
    return tuple(row[k] for k in ('phase', 'family', 'corpus', 'cell', 'arm', 'seed'))


def deterministic(row):
    return {k: v for k, v in row.items() if k not in TIMING_FIELDS}


def implementation_hashes():
    files = [Path(__file__), Path(__file__).with_name('frequency_matched_report.py')]
    # Capture every local imported search/validation dependency, and the actual binary.
    for name in (
        'then_addition_run', 'then_addition_bank', 'comparison_gate_bank',
        'comparison_gate_run', 'composition_search', 'composition_run',
        'solver_corpus_run', 'solver_corpus_fit', 'four_reducer_maps',
        'four_reducer_bank', 'crossed_learning_run', 'map_learning', 'assembly_bank',
    ):
        files.append(Path(importlib.import_module('experiments.chem_tape.' + name).__file__))
    for name in ('_folding_rust._folding_rust', 'folding_evolution.chem_tape.evolve',
                 'folding_evolution.chem_tape.executor', 'folding_evolution.chem_tape.alphabet'):
        files.append(Path(importlib.import_module(name).__file__))
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def historical_source(corpora, source_freeze, bank):
    raw = (DATA / 'provenance.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != PROVENANCE_SHA:
        raise ValueError('1548 provenance SHA mismatch')
    provenance = json.loads(raw)
    saved = {}
    for name, sha in provenance['sha256'].items():
        raw = (gzip.decompress((DATA / (name + '.gz')).read_bytes())
               if name == 'search.jsonl' else (DATA / name).read_bytes())
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError(f'1548 source SHA mismatch: {name}')
        saved[name] = ([json.loads(r) for r in raw.splitlines()]
                       if name == 'search.jsonl' else json.loads(raw))
    cfg, freeze = saved['config.json'], saved['freeze.json']
    schedule = fresh_schedule(bank['selected_ids'])
    if (cfg['git_commit'] != SOURCE_COMMIT or cfg['row'] != 'F' or cfg['smoke_only']
        or saved['metadata.json']['git_commit'] != SOURCE_COMMIT
        or saved['metadata.json']['git_dirty'] or saved['metadata.json']['status'] != 'done'
        or not saved['validation.json']['passed']
        or saved['progress.json'] != dict(completed_pairs=8, g4_complete=True,
                                         stop_kind=None, stop_reason=None)
        or not freeze['complete'] or freeze['smoke_only']
        or freeze['fresh_bank_sha256'] != bank_module.BANK_SHA
        or freeze['fitted_table_hashes'] != source_freeze['fitted_table_hashes']
        or saved['schedule.json'] != schedule
        or digest(schedule) != freeze['schedule_hash']
        or digest(cfg['method']) != cfg['method_hash']
        or cfg['method_hash'] != freeze['method_hash']):
        raise ValueError('1548 freeze/config/roster mismatch')
    rows = saved['search.jsonl']
    indexed = {key(r): r for r in rows}
    if len(indexed) != 4352 or set(indexed) != {key(r) for r in schedule}:
        raise ValueError('1548 observations incomplete/duplicate')
    for r in rows:
        expected_hash = (cfg['method']['source_method']['g4_hash'] if r['arm'] == 'G4'
                         else validate_table(corpora[r['corpus']]['tables'][r['arm']]))
        indices = np.random.default_rng([r['seed'], 0]).choice(1331, 64, replace=False).tolist()
        if (r['table_hash'] != expected_hash or r['cap'] != CAP or r['pop_size'] != 256
            or r['training_indices'] != indices or not 0 < r['evaluations'] <= CAP
            or r['evaluations'] % 256 or (not r['solved'] and r['evaluations'] != CAP)):
            raise ValueError('1548 row identity/budget/cases mismatch')
    return saved, provenance, indexed


def schedules(original, cells):
    k = [dict(r, arm='K') for r in original if r['arm'] == 'C']
    replay = []
    timing = []
    for corpus in [f'{f}{i}' for i in range(1, 9) for f in ('BE', 'PA')]:
        cr = [r for r in original if r['corpus'] == corpus and r['arm'] == 'C']
        timing.append(dict(cr[0], arm='K'))
        if corpus in ('BE1', 'PA1'):
            for cid in cells[:8]:
                ref = next(r for r in cr if r['cell'] == cid)
                replay.extend([ref, dict(ref, arm='T')])
    if len(k) != 2048 or len(replay) != 32 or len(timing) != 16:
        raise ValueError('fixed preparation/full schedule size mismatch')
    return k, replay, timing


class Runner(SearchRunner):
    envelope = FrozenRunner.envelope

    def __init__(self, args):
        os.environ['RAYON_NUM_THREADS'] = '1'
        self.args = args
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 120
        self.out = Path(os.environ['RUN_DIR'])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / 'config.json').exists():
            raise ValueError('use a fresh RUN_DIR')
        self.bank, self.cells = bank_module.load()
        self.inputs = self.bank['inputs']
        self.saved, source_provenance = frozen_source()
        self.corpora = self.saved['corpora.json']
        self.historical, provenance, self.reference = historical_source(
            self.corpora, self.saved['freeze.json'], self.bank)
        full, replay, timing = schedules(self.historical['schedule.json'], self.bank['selected_ids'])
        self.full_schedule, self.replay_schedule, self.timing_schedule = full, replay, timing
        self.schedule = replay + timing if args.prepare else full
        # No G4 searches, but envelope retains the shared existing search path.
        self.g4 = None
        marginals = {}
        for tid, record in self.corpora.items():
            c, k = [emitted(record['tables'][a]) for a in ('C', 'K')]
            error = float(np.max(np.abs(c - k)))
            if error > 0.001:
                raise ValueError(f'{tid}: frozen marginal match failed: {error}')
            marginals[tid] = dict(C=c.tolist(), K=k.tolist(), max_absolute_error=error)
        hashes = implementation_hashes()
        historical_hashes = self.historical['config.json']['method']['code_hashes']
        self.config = dict(
            task='2026-10-09-0125', prepare_only=args.prepare, workers=args.workers,
            arguments=vars(args), cap=CAP, population=256, cases=64, tape_length=32,
            git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            implementation_hashes=hashes, historical_code_hashes=historical_hashes,
            source_commit=SOURCE_COMMIT, bank_sha256=bank_module.BANK_SHA,
            source_provenance_sha256=PROVENANCE_SHA,
            schedule_hash=digest(full), replay_schedule_hash=digest(replay),
            timing_schedule_hash=digest(timing),
            table_hashes=self.saved['freeze.json']['fitted_table_hashes'],
            primary='C/K = exp(mean_corpus(mean_cell_seed(log(cost_K)-log(cost_C))))',
            unsolved_cost='2*cap', interval='95% t over 16 corpus means, 15 df',
            threshold=1.20, full_n=2048,
            scope='G4-based pooled-frequency replacement; development bank; context not isolated',
        )
        self.rows, self.timings = [], {}
        self.validation = dict(passed=False, solver_verifications=0, pairing_checks=0,
                               source_tables_checked=48, marginals=marginals,
                               maximum_marginal_error=max(v['max_absolute_error'] for v in marginals.values()))
        self.preparation = None
        if not args.prepare:
            if not args.preparation:
                raise ValueError('full run requires --preparation from successful prepare run')
            self.preparation = json.loads(Path(args.preparation).read_bytes())
            p = self.preparation
            if (not p['admitted'] or p['implementation_hashes'] != hashes
                or p['schedule_hash'] != digest(full) or p['workers'] != args.workers
                or p['source_provenance_sha256'] != PROVENANCE_SHA
                or not p['replay']['passed'] or p['replay']['rows'] != 32
                or len(p['timing_rows']) != 16):
                raise ValueError('preparation not admitted or actual implementation changed')
            self.config['preparation_sha256'] = hashlib.sha256(Path(args.preparation).read_bytes()).hexdigest()
        for name, value in (
            ('config.json', self.config), ('bank.json', self.bank),
            ('schedule.json', self.schedule),
            ('preparation_schedules.json', dict(replay=replay, timing=timing)),
            ('source_provenance.json', dict(row_F=provenance, tables=source_provenance)),
            ('freeze.json', dict(frozen_before_scoring=True, schedule_hash=digest(full),
                                 bank_sha256=bank_module.BANK_SHA,
                                 table_hashes=self.config['table_hashes'],
                                 implementation_hashes=hashes)),
        ):
            write_json(self.out, name, value)
        (self.out / 'search.jsonl').touch()
        write_json(self.out, 'validation.json', self.validation)

    def check_pairs(self, rows):
        for r in rows:
            for arm in ('C', 'T'):
                ref = self.reference[key(dict(r, arm=arm))]
                if r['training_indices'] != ref['training_indices']:
                    raise ValueError('K/reference training case mismatch')
                self.validation['pairing_checks'] += 1

    def prepare(self):
        replay = self.jobs(self.replay_schedule, 'replay')
        errors = [dict(key=list(key(r))) for r in replay
                  if deterministic(r) != deterministic(self.reference[key(r)])]
        self.validation['replay'] = dict(passed=not errors, rows=len(replay), errors=errors,
                                         excluded_fields=sorted(TIMING_FIELDS))
        write_json(self.out, 'validation.json', self.validation)
        if errors:
            raise ValueError('current implementation/build does not replay 1548 bit-exactly')
        timing = self.jobs(self.timing_schedule, 'K_timing')
        self.check_pairs(timing)
        wall = self.timings['K_timing']['wall_seconds']
        worker = sum(r['seconds'] for r in timing)
        effective = min(self.args.workers, worker / wall)
        projected = wall / 16 * 2048
        # Small sample has a final idle tail. All-cap projection uses measured
        # per-evaluation rate at intended concurrency and retains historical bound.
        rate = worker / sum(r['evaluations'] for r in timing)
        capped_projection = max(1.7 * 3600, rate * CAP * 2048 / max(effective, 1))
        elapsed = time.monotonic() - self.started
        admitted = (elapsed <= 1800 and max(projected, capped_projection) * 1.15 < 8640)
        p = dict(admitted=admitted, preparation_wall_seconds=elapsed,
                 workers=self.args.workers, implementation_hashes=self.config['implementation_hashes'],
                 source_provenance_sha256=PROVENANCE_SHA,
                 schedule_hash=digest(self.full_schedule), replay=self.validation['replay'],
                 timing_rows=timing, timing_wall_seconds=wall,
                 mean_worker_seconds=worker / 16, effective_workers=effective,
                 solved=sum(r['solved'] for r in timing), n=16,
                 sample_projection_seconds=projected, all_capped_projection_seconds=capped_projection,
                 projection_margin=1.15, scoring_budget_seconds=8640,
                 maximum_marginal_error=self.validation['maximum_marginal_error'])
        write_json(self.out, 'preparation.json', p)
        if not admitted:
            raise ValueError('runtime projection/preparation exceeds approved admission budget')
        self.validation['passed'] = True

    def score(self):
        timed = {key(r): r for r in self.preparation['timing_rows']}
        for i in range(1, 9):
            rows = self.jobs([r for r in self.schedule if r['corpus'] in (f'BE{i}', f'PA{i}')], f'BE{i}+PA{i}')
            self.check_pairs(rows)
            for r in rows:
                if key(r) in timed and deterministic(r) != deterministic(timed[key(r)]):
                    raise ValueError('K timing replay changed deterministically')
            write_json(self.out, 'progress.json', dict(completed_pairs=i, searches=len(self.rows)))
            print(json.dumps(dict(completed_pairs=i, searches=len(self.rows),
                                  elapsed=time.monotonic() - self.started)), flush=True)
        self.validation['passed'] = len(self.rows) == 2048

    def run(self):
        self.pool = mp.get_context('spawn').Pool(self.args.workers)
        error = None
        try:
            self.prepare() if self.args.prepare else self.score()
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
            self.validation.update(passed=False, error=error)
        finally:
            self.pool.terminate()
            self.pool.join()
            write_json(self.out, 'validation.json', self.validation)
        if not self.args.prepare:
            from experiments.chem_tape.frequency_matched_report import make_report, save_report
            report = make_report(self.rows, self.historical['search.jsonl'], self.full_schedule,
                                 self.config, error)
            save_report(self.out, report, self.rows + self.historical['search.jsonl'])
        if error:
            raise RuntimeError(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--preparation', help='successful preparation.json from the same implementation/build')
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--deadline-seconds', type=float, default=8880)
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 120:
        parser.error('positive workers and deadline > 120 required')
    Runner(args).run()


if __name__ == '__main__':
    main()
