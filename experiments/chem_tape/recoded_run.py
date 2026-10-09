"""Fixed-prior Q recoding: replay/prepare, then the complete paired R30/R100 run."""

import argparse
from functools import lru_cache
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest, load_training
from experiments.chem_tape.comparison_gate_run import CAP
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import search
from experiments.chem_tape.frequency_matched_run import deterministic, historical_source, key
from experiments.chem_tape.position_matched_run import implementation_hashes as positional_hashes
from experiments.chem_tape.position_matched import decoder_for, table_hash
from experiments.chem_tape.then_addition_run import frozen_source
from experiments.chem_tape.solver_corpus_run import observed_search
from experiments.chem_tape import then_addition_bank as bank_module
from experiments.chem_tape.recoded import CORPORA, DOSES, METHOD, RecodedDecoder, audit, R
from experiments.chem_tape.recoded_smoke import q_source, Q_PROVENANCE_SHA


def implementation_hashes():
    result = positional_hashes()
    for name in ('recoded.py', 'recoded_run.py', 'recoded_smoke.py', 'recoded_report.py',
                 'comparison_gate_report.py', 'solver_corpus_report.py'):
        result[name] = hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
    result['Q_provenance'] = Q_PROVENANCE_SHA
    return result


def schedules(q_schedule, cells):
    base = [r for r in q_schedule if r['arm'] == 'Q']
    full, replay, timing = [], [], []
    for ci, tid in enumerate(CORPORA):
        for cid in cells:
            rs = sorted((r for r in base if r['corpus'] == tid and r['cell'] == cid), key=lambda r: r['seed'])
            if len(rs) != 8:
                raise ValueError('not eight seeds per cell')
            for i, r in enumerate(rs):
                full.extend(dict(r, arm=f'R{dose}', realization=i // 4) for dose in DOSES)
        rs = sorted((r for r in base if r['corpus'] == tid and r['cell'] == cells[ci]), key=lambda r: r['seed'])
        replay.extend((rs[0], dict(rs[0], arm='C')))
        timing.extend(dict(rs[k * 4], arm=f'R{dose}', realization=k) for dose in DOSES for k in (0, 1))
    # Group maps to amortize setup without altering any per-search RNG stream.
    full.sort(key=lambda r: (CORPORA.index(r['corpus']), r['arm'], r['realization'], r['cell'], r['seed']))
    if len(full) != 4096 or len(replay) != 32 or len(timing) != 64:
        raise ValueError('incorrect fixed roster')
    return full, replay, timing


@lru_cache(maxsize=1)
def cached_decoder(corpus, dose, k, table_json):
    return RecodedDecoder(dict(corpus=corpus, dose=dose, k=k, table=json.loads(table_json)))


def recoded_search(envelope):
    job, meta = envelope
    t = job[2]
    if isinstance(t, dict):
        tick = time.monotonic()
        d = cached_decoder(t['corpus'], t['dose'], t['k'], json.dumps(t['table']))
        setup = time.monotonic() - tick
        row = search(job, decoder_factory=lambda _: d, initial_transform=lambda pop, dec: dec.recode(pop))
        if t['dose']:
            row.update(initial_source_hash=d.source_hash, initial_reencoded=True,
                       realization=t['k'], setup_seconds=setup)
        row['seconds'] += setup
    else:
        row = search(job, decoder_factory=decoder_for)
    row.update(meta)
    return row


def stable(row):
    return deterministic({k: v for k, v in row.items() if k not in ('setup_seconds', 'solver', 'verification_seconds')})


def runtime_admission(sample, batch, capped, setup, elapsed):
    expected = 1.15 * max(sample, batch) + setup + 120
    bound = capped + setup + 120
    return dict(admitted=elapsed <= 1800 and expected < 11760 and bound < 11760,
                preparation_wall_seconds=elapsed, expected_scoring_with_safety_seconds=expected,
                all_capped_scoring_bound_seconds=bound,
                admission_rule='elapsed <= 1800 and 1.15*max(sample,batch)+setup+120 < 11760 and all_capped+setup+120 < 11760',
                sample_projection_seconds=sample, finite_batch_projection_seconds=batch,
                all_capped_projection_seconds=capped, setup_and_audit_seconds=setup,
                scoring_timeout_seconds=12000, internal_deadline_seconds=11880,
                reporting_reserve_seconds=120, outer_margin_seconds=120)


class Runner:
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
        self.history, history_provenance, self.c_reference = historical_source(self.corpora, self.saved['freeze.json'], self.bank)
        self.q_saved = q_source()
        qs = self.q_saved
        expected = [dict(r, arm=a) for r in self.history['schedule.json'] if r['arm'] == 'C' for a in ('Q', 'P')]
        indexed = {key(r): r for r in qs['search.jsonl']}
        if (qs['schedule.json'] != expected or len(indexed) != 4096 or len(qs['search.jsonl']) != 4096
            or set(indexed) != {key(r) for r in expected}
            or qs['progress.json'] != dict(completed_pairs=8, searches=4096)
            or qs['config.json']['prepare_only'] or not qs['freeze.json']['frozen_before_scoring']
            or qs['freeze.json']['schedule_hash'] != digest(expected)
            or qs['freeze.json']['bank_sha256'] != bank_module.BANK_SHA):
            raise ValueError('Q source identity/freeze/roster mismatch')
        self.q_reference = {k: r for k, r in indexed.items() if r['arm'] == 'Q'}
        for tid in CORPORA:
            t = qs['projected_tables.json'][tid]['Q']
            if table_hash(t) != qs['freeze.json']['projected_table_hashes'][tid]['Q']:
                raise ValueError('Q table SHA mismatch')
            self.corpora[tid]['tables']['Q'] = t
        for r in self.q_reference.values():
            if (r['table_hash'] != table_hash(self.corpora[r['corpus']]['tables']['Q'])
                or r['cap'] != CAP or r['pop_size'] != 256 or not 0 < r['evaluations'] <= CAP
                or r['evaluations'] % 256 or (not r['solved'] and r['evaluations'] != CAP)
                or r['training_indices'] != np.random.default_rng([r['seed'], 0]).choice(1331, 64, replace=False).tolist()):
                raise ValueError('Q source budget/cases/map mismatch')
        self.full_schedule, self.replay_schedule, self.timing_schedule = schedules(qs['schedule.json'], self.bank['selected_ids'])
        self.recovery_schedule = [{k: r[k] for k in ('phase', 'family', 'corpus', 'cell', 'arm', 'seed')}
            for r in self.saved['search.jsonl'] if r['phase'] == 'training' and r['arm'] == 'C' and r['solved']]
        if len(self.recovery_schedule) != 936:
            raise ValueError('C recovery roster changed')
        self.schedule = self.replay_schedule + self.timing_schedule if args.prepare else self.full_schedule
        self.rows, self.timings, self.maps, self.initial_hashes = [], {}, {}, {}
        self.validation = dict(passed=False, pairing_checks=0, initial_rows=0, row_counts_passed=False)
        hashes = implementation_hashes()
        self.config = dict(task='2026-10-09-0537', prepare_only=args.prepare, arguments=vars(args),
                           workers=args.workers, cap=CAP, population=256, full_n=4096,
                           git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                           implementation_hashes=hashes, bank_sha256=bank_module.BANK_SHA,
                           Q_provenance_sha256=Q_PROVENANCE_SHA,
                           schedule_hash=digest(self.full_schedule),
                           preparation_schedule_hash=digest(self.replay_schedule + self.timing_schedule),
                           recovery_schedule_hash=digest(self.recovery_schedule),
                           method=METHOD, primary='G = geometric cost_Q/cost_R30',
                           secondary='H = geometric cost_R30/cost_C', threshold=1.20,
                           scope='Frozen recoding at fixed uniform-prior supply; changes edit correlations and crossover as well as width; then-addition development bank; no transfer, acquisition or causal gap partition.')
        self.preparation = None
        if not args.prepare:
            if not args.preparation:
                raise ValueError('scoring requires admitted preparation')
            raw = Path(args.preparation).read_bytes()
            p = self.preparation = json.loads(raw)
            if (not p['admitted'] or p['workers'] != args.workers or p['implementation_hashes'] != hashes
                or any(p[n] != self.config[n] for n in ('schedule_hash', 'preparation_schedule_hash', 'recovery_schedule_hash', 'Q_provenance_sha256'))
                or not p['replay']['passed'] or p['replay']['rows'] != 32
                or not p['validation']['row_counts_passed'] or p['validation']['initial_rows'] != 4096
                or not p['validation']['C_recovery']['passed'] or p['validation']['C_recovery']['rows'] != 936
                or len(p['timing_rows']) != 64):
                raise ValueError('preparation not admitted or implementation/source/roster changed')
            self.config['preparation_sha256'] = hashlib.sha256(raw).hexdigest()
        for name, value in (
            ('config.json', self.config), ('bank.json', self.bank), ('schedule.json', self.schedule),
            ('preparation_schedules.json', dict(replay=self.replay_schedule, timing=self.timing_schedule, C_recovery=self.recovery_schedule)),
            ('source_provenance.json', dict(Q=Q_PROVENANCE_SHA, C=history_provenance, tables=table_provenance)),
            ('validation.json', self.validation),
        ):
            write_json(self.out, name, value)
        (self.out / 'search.jsonl').touch()

    def recover(self):
        training, cells = load_training()
        references = {key(r): r for r in self.saved['search.jsonl'] if r['phase'] == 'training' and r['arm'] == 'C' and r['solved']}
        envelopes = [((cells[r['cell']], 'C', self.corpora[r['corpus']]['tables']['C'], r['seed'], CAP, 256,
                       training['inputs'], training['alphabet']), {k: r[k] for k in ('phase', 'family', 'corpus')}, True)
                     for r in self.recovery_schedule]
        expected = set(references)
        recovered = []
        tick = time.monotonic()
        with (self.out / 'C_solvers.jsonl').open('w', buffering=1) as stream:
            def save(r):
                expected.remove(key(r))
                if not r['solved'] or r['solver'] is None or stable(r) != stable(references[key(r)]):
                    raise ValueError('historical C solver recovery is not bit-exact')
                recovered.append(r)
                stream.write(json.dumps(r, allow_nan=False) + '\n')
            complete = run_jobs(self.pool, observed_search, envelopes, self.deadline, save)
        if not complete or expected:
            raise TimeoutError('historical C recovery incomplete')
        recovered.sort(key=key)
        self.validation['C_recovery'] = dict(passed=True, rows=len(recovered), wall_seconds=time.monotonic() - tick,
                                             worker_seconds=sum(r['seconds'] for r in recovered))
        return recovered

    def construct_and_audit(self, recovered):
        grouped = {t: [r['solver'] for r in recovered if r['corpus'] == t] for t in CORPORA}
        variation = dict(seed=202610090537, uniform_n=4096, C_solver_n=936,
            solver_encoding='one conditionally uniform preimage per recovered historical C solver row; no new search seeds',
            offspring='two uniformly sampled audit parents; crossover .7, point 1..31, then Bernoulli .03 allele resampling; variation matches production, parent selection is descriptive', corpora={})
        for ci, tid in enumerate(CORPORA):
            variation['corpora'][tid] = {}
            a = np.random.default_rng(202610090537).integers(R, size=(4096, 32), dtype=np.int32)
            tokens = np.asarray(grouped[tid], dtype=np.uint8)
            for arm in ('C', 'Q', 'R30', 'R100'):
                for k in ((0, 1) if arm.startswith('R') else (0,)):
                    name = f'{tid}-{arm}-{k}'
                    if arm == 'C':
                        d = decoder_for(self.corpora[tid]['tables']['C'])
                        solver_a = d.encode(tokens, np.random.default_rng([537, ci, 999]))
                        uniform_a = a
                    else:
                        dose = int(arm[1:]) if arm.startswith('R') else 0
                        d = RecodedDecoder(dict(table=self.corpora[tid]['tables']['Q'], corpus=tid, dose=dose, k=k))
                        solver_a = d.encode(tokens, np.random.default_rng([537, ci, 999]))
                        uniform_a = d.recode(a)
                        if dose:
                            self.maps[name] = d.validate()
                            for r in self.full_schedule:
                                if r['corpus'] == tid and r['arm'] == arm and r['realization'] == k:
                                    pop = np.random.default_rng([r['seed'], 1]).integers(R, size=(256, 32), dtype=np.int32)
                                    h = hashlib.sha256(d.decode(d.recode(pop)).tobytes()).hexdigest()
                                    if h != self.q_reference[key(dict(r, arm='Q'))]['initial_tokens_hash']:
                                        raise ValueError('Q generation-zero tokens changed')
                                    self.initial_hashes['|'.join(map(str, key(r)))] = h
                                    self.validation['initial_rows'] += 1
                    variation['corpora'][tid][f'{arm}-{k}'] = dict(uniform=audit(d, uniform_a, [202610090537, ci]),
                                                           C_solvers=audit(d, solver_a, [202610090537, ci, 1]))
                    del d
            print(f'validated and audited {tid}', flush=True)
        if self.validation['initial_rows'] != 4096 or len(self.maps) != 64:
            raise ValueError('incomplete map/initial population gate')
        self.validation['row_counts_passed'] = True
        write_json(self.out, 'initial_hashes.json', self.initial_hashes)
        write_json(self.out, 'variation.json', variation)
        write_json(self.out, 'validation.json', self.validation)

    def map_hashes(self):
        return {name: {k: v[k] for k in ('map_hash', 'lookup_sha256', 'permutation_sha256', 'inverse_sha256')} for name, v in self.maps.items()}

    def envelope(self, r):
        t = self.corpora[r['corpus']]['tables']['Q' if r['arm'].startswith('R') else r['arm']]
        if r['arm'].startswith('R') or r['arm'] == 'Q':
            t = dict(table=t, corpus=r['corpus'], dose=int(r['arm'][1:]) if r['arm'].startswith('R') else 0,
                     k=r.get('realization', 0))
        return ((self.cells[r['cell']], r['arm'], t, r['seed'], CAP, 256, self.inputs, self.bank['alphabet']),
                {k: r[k] for k in ('phase', 'family', 'corpus')})

    def jobs(self, roster, name):
        expected = {key(r): r for r in roster}
        if len(expected) != len(roster):
            raise ValueError('duplicate search jobs')
        rows = []
        tick = time.monotonic()
        with (self.out / 'search.jsonl').open('a', buffering=1) as stream:
            def save(r):
                planned = expected.pop(key(r))
                h = (self.maps[f"{r['corpus']}-{r['arm']}-{r['realization']}"]['map_hash'] if r['arm'].startswith('R')
                     else table_hash(self.corpora[r['corpus']]['tables'][r['arm']]))
                if (r['table_hash'] != h or r['cap'] != CAP or r['pop_size'] != 256
                    or not 0 < r['evaluations'] <= CAP or r['evaluations'] % 256
                    or (not r['solved'] and r['evaluations'] != CAP)
                    or r.get('realization') != planned.get('realization')):
                    raise ValueError('search map/roster/budget mismatch')
                ref = (self.c_reference[key(r)] if r['arm'] == 'C' else self.q_reference[key(dict(r, arm='Q'))])
                if r['training_indices'] != ref['training_indices'] or r['initial_tokens_hash'] != ref['initial_tokens_hash']:
                    raise ValueError('case or initial-token pairing mismatch')
                self.validation['pairing_checks'] += 1
                rows.append(r)
                self.rows.append(r)
                stream.write(json.dumps(r, allow_nan=False) + '\n')
            try:
                complete = run_jobs(self.pool, recoded_search, [self.envelope(r) for r in roster], self.deadline, save)
            finally:
                self.timings[name] = dict(wall_seconds=time.monotonic() - tick, worker_seconds=sum(r['seconds'] for r in rows), rows=len(rows), complete=not expected)
                write_json(self.out, 'timing.json', self.timings)
        if not complete or expected:
            raise TimeoutError(name + ' incomplete')
        return rows

    def prepare(self):
        recovered = self.recover()
        tick = time.monotonic()
        self.construct_and_audit(recovered)
        self.setup_seconds = time.monotonic() - tick + self.initial_setup_seconds
        replay = self.jobs(self.replay_schedule, 'replay')
        errors = [list(key(r)) for r in replay if stable(r) != stable((self.q_reference if r['arm'] == 'Q' else self.c_reference)[key(r)])]
        self.validation['replay'] = dict(passed=not errors, rows=32, errors=errors, Q_rows=16, C_rows=16)
        if errors:
            raise ValueError('historical Q/C replay not bit-exact')
        timing = self.jobs(self.timing_schedule, 'recoded_timing')
        prices = {}
        for arm in ('R30', 'R100'):
            rows = [r for r in timing if r['arm'] == arm]
            worker = sum(r['seconds'] for r in rows)
            capped = [r['seconds'] for r in rows if not r['solved']]
            per_cap = max(worker / sum(r['evaluations'] for r in rows) * CAP, float(np.mean(capped)) if capped else 0)
            prices[arm] = dict(n=len(rows), solved=sum(r['solved'] for r in rows), mean_worker_seconds=worker / len(rows),
                               mean_setup_seconds=float(np.mean([r['setup_seconds'] for r in rows])),
                               per_search_capped_seconds=per_cap, capped_rows=len(capped),
                               sample_projection_seconds=worker / len(rows) * 2048 / self.args.workers,
                               all_capped_projection_seconds=per_cap * 2048 / self.args.workers)
        sample = sum(v['sample_projection_seconds'] for v in prices.values())
        batch = self.timings['recoded_timing']['wall_seconds'] / 64 * 4096
        capped = sum(v['all_capped_projection_seconds'] for v in prices.values()) + max(v['per_search_capped_seconds'] for v in prices.values())
        self.validation['passed'] = True
        p = dict(**runtime_admission(sample, batch, capped, self.setup_seconds, time.monotonic() - self.started),
                 arms=prices, timing_rows=timing, validation=self.validation, replay=self.validation['replay'],
                 map_hashes=self.map_hashes(), maps=self.maps,
                 workers=self.args.workers, implementation_hashes=self.config['implementation_hashes'],
                 **{k: self.config[k] for k in ('Q_provenance_sha256', 'schedule_hash', 'preparation_schedule_hash', 'recovery_schedule_hash')},
                 C_solvers_sha256=hashlib.sha256((self.out / 'C_solvers.jsonl').read_bytes()).hexdigest(),
                 initial_hashes_sha256=digest(self.initial_hashes),
                 variation_sha256=hashlib.sha256((self.out / 'variation.json').read_bytes()).hexdigest(),
                 freeze_snapshot_note='actual map arrays hashed after exact validation')
        write_json(self.out, 'preparation.json', p)
        write_json(self.out, 'freeze.json', dict(frozen_before_scoring=True, map_hashes=p['map_hashes'],
                    method=METHOD, schedule_hash=p['schedule_hash'], initial_hashes_sha256=p['initial_hashes_sha256']))
        if not p['admitted']:
            raise ValueError('runtime admission exceeds approved preparation/scoring budget')

    def score(self):
        # Reuse exactly the gated recovered tapes and descriptive audits; no recovery searches in scoring.
        folder = Path(self.args.preparation).parent
        raw = (folder / 'C_solvers.jsonl').read_bytes()
        if hashlib.sha256(raw).hexdigest() != self.preparation['C_solvers_sha256']:
            raise ValueError('recovered C tape snapshot changed')
        self.maps = self.preparation['maps']
        # Reconstruct/check each fixed map before use, without repeating the full initial/audit pass.
        for ci, tid in enumerate(CORPORA):
            for dose in DOSES:
                for k in (0, 1):
                    d = RecodedDecoder(dict(table=self.corpora[tid]['tables']['Q'], corpus=tid, dose=dose, k=k))
                    name = f'{tid}-R{dose}-{k}'
                    hashes = dict(map_hash=d.hash(), lookup_sha256=d.lookup_hash,
                                  permutation_sha256=d.permutation_hash, inverse_sha256=d.inverse_hash)
                    if hashes != self.preparation['map_hashes'][name]:
                        raise ValueError('actual map arrays differ from preparation')
                    del d
        for name in ('variation.json', 'initial_hashes.json', 'freeze.json'):
            raw = (folder / name).read_bytes()
            if name == 'variation.json' and hashlib.sha256(raw).hexdigest() != self.preparation['variation_sha256']:
                raise ValueError('descriptive audit snapshot changed')
            if name == 'initial_hashes.json' and digest(json.loads(raw)) != self.preparation['initial_hashes_sha256']:
                raise ValueError('initial hashes changed')
            (self.out / name).write_bytes(raw)
        self.validation.update(row_counts_passed=True, initial_rows=4096, C_recovery=self.preparation['validation']['C_recovery'])
        timed = {key(r): r for r in self.preparation['timing_rows']}
        for i in range(1, 9):
            rows = self.jobs([r for r in self.full_schedule if r['corpus'] in (f'BE{i}', f'PA{i}')], f'pair-{i}')
            for r in rows:
                if key(r) in timed and stable(r) != stable(timed[key(r)]):
                    raise ValueError('timing row deterministic replay changed')
            write_json(self.out, 'progress.json', dict(completed_pairs=i, searches=len(self.rows)))
            print(f'completed pair {i}, searches {len(self.rows)}', flush=True)
        self.validation['passed'] = len(self.rows) == 4096

    def run(self):
        self.initial_setup_seconds = time.monotonic() - self.started
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
            from experiments.chem_tape.recoded_report import make_report, save_report
            refs = list(self.q_reference.values()) + [r for r in self.history['search.jsonl'] if r['arm'] == 'C']
            result = make_report(self.rows, refs, self.full_schedule, self.config, self.preparation, error)
            save_report(self.out, result, self.rows + refs)
        if error:
            raise RuntimeError(error)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepare', action='store_true')
    p.add_argument('--preparation')
    p.add_argument('--workers', type=int, default=10)
    p.add_argument('--deadline-seconds', type=float, default=11880)
    args = p.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 120:
        p.error('positive workers and deadline > 120 required')
    Runner(args).run()


if __name__ == '__main__':
    main()
