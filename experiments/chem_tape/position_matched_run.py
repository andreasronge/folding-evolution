"""0306 rerun of frozen Q/P replacement on the complete paired 1548 row F roster."""

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

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.comparison_gate_run import CAP, Runner as SearchRunner
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import search
from experiments.chem_tape.frequency_matched_run import (
    deterministic, historical_source, implementation_hashes as legacy_hashes,
    key, schedules as legacy_schedules, PROVENANCE_SHA,
)
from experiments.chem_tape.then_addition_run import frozen_source
from experiments.chem_tape import then_addition_bank as bank_module
from experiments.chem_tape.position_matched import (
    METHOD, decoder_for, project, table_hash, validate_lookup, variation_diagnostics,
)

DATA = Path(__file__).with_name('data') / 'position_matched_0239'
K_PROVENANCE_SHA = '6d88de0c27f496f4bc05866a094f8492042aed42e80e90b884536f6e1ace1094'


def runtime_admission(sample, batch_projection, capped, fit_seconds, elapsed):
    """Apply safety to expected work and retain a separate zero-solve hard bound."""
    expected = 1.15 * max(sample, batch_projection) + fit_seconds + 120
    bound = capped + fit_seconds + 120
    return dict(
        admitted=elapsed <= 1800 and expected < 11700 and bound < 11700,
        expected_scoring_with_safety_seconds=expected,
        all_capped_scoring_bound_seconds=bound,
        admission_rule=dict(
            version='expected_safety_and_capped_bound_v1',
            predicate='elapsed <= 1800 and expected < 11700 and bound < 11700',
            expected='1.15 * max(sample, batch_projection) + fit_seconds + 120',
            bound='capped + fit_seconds + 120',
            safety_multiplier_scope='expected runtime; all-capped bound has no additional multiplier',
            conservative_price_role='diagnostic only; unchanged 1.15 * max(sample, batch_projection, capped) + fit_seconds + 120',
        ),
    )


def implementation_hashes():
    result = legacy_hashes()
    for name in ('position_matched.py', 'position_matched_run.py', 'position_matched_report.py'):
        result[name] = hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
    return result


def k_source(corpora, original):
    raw = (DATA / 'K_provenance.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != K_PROVENANCE_SHA:
        raise ValueError('0125 provenance SHA mismatch')
    provenance = json.loads(raw)
    saved = {}
    for name, sha in provenance['sha256'].items():
        raw = ((gzip.decompress((DATA / ('K_' + name + '.gz')).read_bytes()))
               if name == 'search.jsonl' else (DATA / ('K_' + name)).read_bytes())
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError('0125 source SHA mismatch: ' + name)
        saved[name] = ([json.loads(r) for r in raw.splitlines()] if name == 'search.jsonl' else json.loads(raw))
    cfg, metadata, freeze = [saved[n + '.json'] for n in ('config', 'metadata', 'freeze')]
    expected = [dict(r, arm='K') for r in original if r['arm'] == 'C']
    rows = saved['search.jsonl']
    indexed = {key(r): r for r in rows}
    if (cfg['prepare_only'] or cfg['git_commit'] != provenance['commit']
        or metadata['git_commit'] != provenance['commit'] or metadata['git_dirty']
        or metadata['status'] != 'done' or not saved['validation.json']['passed']
        or saved['progress.json'] != dict(completed_pairs=8, searches=2048)
        or saved['schedule.json'] != expected or len(rows) != 2048
        or set(indexed) != {key(r) for r in expected}
        or freeze['schedule_hash'] != digest(expected)
        or freeze['bank_sha256'] != bank_module.BANK_SHA
        or not freeze['frozen_before_scoring']
        or cfg['source_provenance_sha256'] != PROVENANCE_SHA):
        raise ValueError('0125 identity/freeze/roster mismatch')
    for r in rows:
        if (r['table_hash'] != table_hash(corpora[r['corpus']]['tables']['K'])
            or r['cap'] != CAP or r['pop_size'] != 256 or not 0 < r['evaluations'] <= CAP
            or r['evaluations'] % 256 or (not r['solved'] and r['evaluations'] != CAP)
            or r['training_indices'] != np.random.default_rng([r['seed'], 0]).choice(1331, 64, replace=False).tolist()):
            raise ValueError('0125 row identity/budget/cases mismatch')
    return saved, provenance, indexed


def schedules(original, cells):
    _, ct_replay, _ = legacy_schedules(original, cells)
    full = [dict(r, arm=a) for r in original if r['arm'] == 'C' for a in ('Q', 'P')]
    # All corpora; rotate the timing cell across the complete 16-cell roster.
    tids = [f'{f}{i}' for i in range(1, 9) for f in ('BE', 'PA')]
    timing = []
    k_replay = []
    for j, tid in enumerate(tids):
        ref = next(r for r in original if r['corpus'] == tid and r['arm'] == 'C' and r['cell'] == cells[j])
        timing.extend(dict(ref, arm=a) for a in ('Q', 'P'))
        k_replay.append(dict(ref, arm='K'))
    if len(full) != 4096 or len(ct_replay) != 32 or len(k_replay) != 16 or len(timing) != 32:
        raise ValueError('fixed roster size mismatch')
    return full, ct_replay, k_replay, timing


def positional_search(envelope):
    job, meta, save_solver = envelope
    if save_solver:
        raise ValueError('no solver collection in positional replacement run')
    row = search(job, decoder_factory=decoder_for)
    row.update(meta)
    return row


class Runner(SearchRunner):
    def __init__(self, args):
        os.environ['RAYON_NUM_THREADS'] = '1'
        self.args, self.started = args, time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 120
        self.out = Path(os.environ['RUN_DIR'])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / 'config.json').exists():
            raise ValueError('use a fresh RUN_DIR')
        self.bank, self.cells = bank_module.load()
        self.inputs = self.bank['inputs']
        self.saved, table_provenance = frozen_source()
        self.corpora = self.saved['corpora.json']
        self.history, history_provenance, self.reference = historical_source(self.corpora, self.saved['freeze.json'], self.bank)
        self.k_saved, k_provenance, self.k_reference = k_source(self.corpora, self.history['schedule.json'])
        self.full_schedule, self.ct_replay, self.k_replay, self.timing_schedule = schedules(self.history['schedule.json'], self.bank['selected_ids'])
        self.schedule = self.ct_replay + self.k_replay + self.timing_schedule if args.prepare else self.full_schedule
        self.rows, self.timings = [], {}
        self.validation = dict(passed=False, pairing_checks=0, solver_verifications=0, projections={})
        tick = time.monotonic()
        for i, (tid, record) in enumerate(self.corpora.items()):
            controls, diagnostics = project(record['tables']['C'])
            diagnostics['lookup_checks'] = {a: validate_lookup(t, 202610090239 + i) for a, t in controls.items()}
            record['tables'].update({a: t.tolist() for a, t in controls.items()})
            self.validation['projections'][tid] = diagnostics
        self.fit_seconds = time.monotonic() - tick
        self.projected_hashes = {t: {a: table_hash(r['tables'][a]) for a in ('Q', 'P')} for t, r in self.corpora.items()}
        hashes = implementation_hashes()
        self.config = dict(
            task='2026-10-09-0306', prepare_only=args.prepare, arguments=vars(args),
            workers=args.workers, cap=CAP, population=256, cases=64, tape_length=32,
            git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            implementation_hashes=hashes, bank_sha256=bank_module.BANK_SHA,
            source_provenance_sha256=PROVENANCE_SHA, K_provenance_sha256=K_PROVENANCE_SHA,
            source_table_hashes=self.saved['freeze.json']['fitted_table_hashes'],
            projected_table_hashes=self.projected_hashes, projection_method=METHOD,
            schedule_hash=digest(self.full_schedule), preparation_schedule_hash=digest(self.ct_replay + self.k_replay + self.timing_schedule),
            primary='C/Q = exp(mean_corpus(mean_cell_seed(log(cost_Q)-log(cost_C))))',
            unsolved_cost='2*cap', interval='95% t over 16 corpus means, 15 df', threshold=1.20,
            full_n=4096, fit_validation_seconds=self.fit_seconds,
            scope='Frozen external projections; then-addition development bank; uniform-prior marginals; supply and variation not separated',
        )
        self.preparation = None
        if not args.prepare:
            if not args.preparation:
                raise ValueError('full run requires admitted --preparation')
            raw = Path(args.preparation).read_bytes()
            p = self.preparation = json.loads(raw)
            if (not p['admitted'] or p['implementation_hashes'] != hashes or p['workers'] != args.workers
                or p['schedule_hash'] != self.config['schedule_hash'] or p['projected_table_hashes'] != self.projected_hashes
                or p['preparation_schedule_hash'] != self.config['preparation_schedule_hash']
                or p['K_provenance_sha256'] != K_PROVENANCE_SHA
                or p['source_provenance_sha256'] != PROVENANCE_SHA
                or not p['CT_replay']['passed'] or p['CT_replay']['rows'] != 32
                or not p['K_replay']['passed'] or p['K_replay']['rows'] != 16
                or len(p['timing_rows']) != 32):
                raise ValueError('preparation not admitted or implementation/frozen maps changed')
            self.config['preparation_sha256'] = hashlib.sha256(raw).hexdigest()
        for name, value in (
            ('config.json', self.config), ('bank.json', self.bank), ('schedule.json', self.schedule),
            ('source_provenance.json', dict(tables=table_provenance, row_F=history_provenance, K=k_provenance)),
            ('projected_tables.json', {t: {a: r['tables'][a] for a in ('Q', 'P')} for t, r in self.corpora.items()}),
            ('freeze.json', dict(frozen_before_scoring=True, schedule_hash=self.config['schedule_hash'],
                                 bank_sha256=bank_module.BANK_SHA, projection_method=METHOD,
                                 projected_table_hashes=self.projected_hashes, implementation_hashes=hashes)),
            ('preparation_schedules.json', dict(CT_replay=self.ct_replay, K_replay=self.k_replay, timing=self.timing_schedule)),
            ('validation.json', self.validation),
        ):
            write_json(self.out, name, value)
        (self.out / 'search.jsonl').touch()

    def envelope(self, row):
        if row not in self.schedule or row['cell'] not in self.cells:
            raise ValueError('search outside frozen roster')
        cell = self.cells[row['cell']]
        if set(cell) != {'id', 'labels'}:
            raise ValueError('program in search payload')
        t = self.corpora[row['corpus']]['tables'][row['arm']]
        if row['arm'] == 'K':
            t = np.tile(t, (32, 1, 1))  # Exercise actual positional path, not legacy optimization.
        return ((cell, row['arm'], t, row['seed'], CAP, 256, self.inputs, self.bank['alphabet']),
                {k: row[k] for k in ('phase', 'family', 'corpus')}, False)

    def jobs(self, roster_rows, name):
        envelopes = [self.envelope(r) for r in roster_rows]
        expected = {key(r): table_hash(j[2]) for r, (j, _, _) in zip(roster_rows, envelopes)}
        if len(expected) != len(envelopes):
            raise ValueError('duplicate jobs')
        rows = []
        tick = time.monotonic()
        with (self.out / 'search.jsonl').open('a', buffering=1) as stream:
            def save(r):
                if expected.pop(key(r)) != r['table_hash']:
                    raise ValueError('table hash mismatch')
                if (r['cap'] != CAP or r['pop_size'] != 256 or not 0 < r['evaluations'] <= CAP
                    or r['evaluations'] % 256 or (not r['solved'] and r['evaluations'] != CAP)
                    or r['training_indices'] != np.random.default_rng([r['seed'], 0]).choice(1331, 64, replace=False).tolist()):
                    raise ValueError('invalid budget/cases')
                for arm in ('C', 'T'):
                    if r['training_indices'] != self.reference[key(dict(r, arm=arm))]['training_indices']:
                        raise ValueError('reference training-case pairing failed')
                    self.validation['pairing_checks'] += 1
                rows.append(r)
                self.rows.append(r)
                stream.write(json.dumps(r, allow_nan=False) + '\n')
            try:
                complete = run_jobs(self.pool, positional_search, envelopes, self.deadline, save)
            finally:
                self.timings[name] = dict(wall_seconds=time.monotonic() - tick,
                                         worker_seconds=sum(r['seconds'] for r in rows),
                                         rows=len(rows), expected_rows=len(envelopes), complete=not expected)
                write_json(self.out, 'timing.json', self.timings)
        if not complete or expected:
            raise TimeoutError(name + ' incomplete at internal deadline')
        return rows

    def replay(self, roster, references, name):
        rows = self.jobs(roster, name)
        errors = [list(key(r)) for r in rows if deterministic(r) != deterministic(references[key(r)])]
        result = dict(passed=not errors, rows=len(rows), errors=errors,
                      hash_note='identical positional K copies retain canonical legacy table hash')
        self.validation[name] = result
        write_json(self.out, 'validation.json', self.validation)
        if errors:
            raise ValueError(name + ' not bit-exact')
        return result

    def prepare(self):
        ct = self.replay(self.ct_replay, self.reference, 'CT_replay')
        kr = self.replay(self.k_replay, self.k_reference, 'K_replay')
        timing = self.jobs(self.timing_schedule, 'QP_timing')
        # These diagnostics use independent uniform tapes and never select projections.
        write_json(self.out, 'variation.json', variation_diagnostics(self.corpora))
        price = {}
        for arm in ('Q', 'P'):
            rows = [r for r in timing if r['arm'] == arm]
            worker = sum(r['seconds'] for r in rows)
            lookup = [self.validation['projections'][t]['lookup_checks'][arm]['construction_seconds'] for t in self.corpora]
            # Actual measured average seconds/evaluation includes construction and exact checks.
            # Use the larger of pooled rate and observed capped-row mean; no hit-rate assumption.
            pooled_cap_seconds = worker / sum(r['evaluations'] for r in rows) * CAP
            capped = [r['seconds'] for r in rows if not r['solved']]
            per_cap = max(pooled_cap_seconds, float(np.mean(capped)) if capped else 0)
            price[arm] = dict(n=16, solved=sum(r['solved'] for r in rows),
                             mean_worker_seconds=worker / 16,
                             mean_decode_seconds=float(np.mean([r['decode_seconds'] for r in rows])),
                             capped_rows=len(capped), capped_worker_seconds=capped,
                             mean_lookup_construction_seconds=float(np.mean(lookup)),
                             lookup_bytes=self.validation['projections']['BE1']['lookup_checks'][arm]['lookup_bytes'],
                             pooled_capped_worker_seconds=pooled_cap_seconds,
                             per_search_capped_worker_seconds=per_cap,
                             sample_projection_seconds=worker / 16 * 2048 / self.args.workers,
                             all_capped_projection_seconds=per_cap * 2048 / self.args.workers)
        sample = sum(v['sample_projection_seconds'] for v in price.values())
        # Include observed finite-batch utilization loss in the average-cost projection;
        # all-capped work is evenly scheduled on all 10 workers, plus one capped tail.
        batch_projection = self.timings['QP_timing']['wall_seconds'] / 32 * 4096
        capped = sum(v['all_capped_projection_seconds'] for v in price.values())
        capped += max(v['per_search_capped_worker_seconds'] for v in price.values())
        scoring_projection = 1.15 * max(sample, batch_projection, capped) + self.fit_seconds + 120
        elapsed = time.monotonic() - self.started
        p = dict(**runtime_admission(sample, batch_projection, capped, self.fit_seconds, elapsed),
                 preparation_wall_seconds=elapsed, workers=self.args.workers,
                 implementation_hashes=self.config['implementation_hashes'],
                 schedule_hash=self.config['schedule_hash'], preparation_schedule_hash=self.config['preparation_schedule_hash'],
                 projected_table_hashes=self.projected_hashes,
                 source_provenance_sha256=PROVENANCE_SHA, K_provenance_sha256=K_PROVENANCE_SHA,
                 CT_replay=ct, K_replay=kr, timing_rows=timing, arms=price,
                 sample_projection_seconds=sample, batch_projection_seconds=batch_projection,
                 all_capped_projection_seconds=capped, safety_multiplier=1.15,
                 scoring_projection_with_safety_seconds=scoring_projection,
                 scoring_timeout_seconds=11700, reporting_reserve_seconds=120,
                 fit_validation_seconds=self.fit_seconds)
        write_json(self.out, 'preparation.json', p)
        if not p['admitted']:
            raise ValueError('preparation, expected runtime with safety, or all-capped bound exceeds approved budget')
        self.validation['passed'] = True

    def score(self):
        timed = {key(r): r for r in self.preparation['timing_rows']}
        for i in range(1, 9):
            rows = self.jobs([r for r in self.full_schedule if r['corpus'] in (f'BE{i}', f'PA{i}')], f'BE{i}+PA{i}')
            for r in rows:
                if key(r) in timed and deterministic(r) != deterministic(timed[key(r)]):
                    raise ValueError('Q/P timing replay changed deterministically')
            write_json(self.out, 'progress.json', dict(completed_pairs=i, searches=len(self.rows)))
            print(json.dumps(dict(completed_pairs=i, searches=len(self.rows), elapsed=time.monotonic() - self.started)), flush=True)
        write_json(self.out, 'variation.json', variation_diagnostics(self.corpora))
        self.validation['passed'] = len(self.rows) == 4096

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
            from experiments.chem_tape.position_matched_report import make_report, save_report
            references = self.history['search.jsonl'] + self.k_saved['search.jsonl']
            report = make_report(self.rows, references, self.full_schedule, self.config, error)
            save_report(self.out, report, self.rows + references)
        if error:
            raise RuntimeError(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--preparation')
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--deadline-seconds', type=float, default=11580)
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 120:
        parser.error('positive workers and deadline > 120 required')
    Runner(args).run()


if __name__ == '__main__':
    main()
