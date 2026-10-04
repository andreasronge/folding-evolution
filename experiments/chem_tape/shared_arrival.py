#!/usr/bin/env python3
"""Approved 2026-10-04-2135: frozen offspring census and natural-copy fates.

Uses the engine's reproduction step without changing its random stream. The
training task keeps the original source seed; continuation randomness is separate.
Outputs are exclusively under --out / $RUN_DIR. See the run's plan.md.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import multiprocessing as mp
import os
import subprocess
import time
from collections import Counter, OrderedDict
from dataclasses import asdict, fields
from pathlib import Path

import numpy as np
import yaml
from scipy.stats import beta

from folding_evolution.chem_tape import evolve, multi_output as mo, tagged
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import evaluate_population
from folding_evolution.chem_tape.metrics import ChemTapeStatsCollector
from folding_evolution.chem_tape.tasks import build_task

STRATA = ('shared', 'partly', 'duplicated', 'shortcut', 'other')
HELPERS = ('B-helper', 'A-only', 'other')
MIN_EXACT = 20
DEFAULT_SOURCE = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-04/mapbias_s32_mate')
_PARTLY = None


def write_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(path)


def config(raw):
    names = {f.name for f in fields(ChemTapeConfig)}
    return ChemTapeConfig(**{k: v for k, v in raw.items() if k in names})


def binomial_interval(k, n):
    """Two-sided exact 95% interval (zero-event upper bound ~3/n)."""
    if not n:
        return [0.0, 1.0]
    return [float(beta.ppf(.025, k, n-k+1)) if k else 0.0,
            float(beta.ppf(.975, k+1, n-k)) if k < n else 1.0]


def function_of(values, key):
    # All 10,000 cases, not training-only helper labels.
    order = np.argsort(key, kind='stable')
    return bool(np.all((np.diff(key[order]) != 0) | (np.diff(values[order]) == 0)))


class Measurements:
    """Bounded clone/semantic caches; engine scoring for uncached training rows."""
    def __init__(self, cfg):
        self.cfg = cfg
        self.task = build_task(cfg, cfg.seed)
        self.labels = mo.full_labels(self.task.label_fn)
        self.exact = mo.Exactness(self.task.output_tags, self.labels, cfg.tag_combine)
        self.full_machine = mo.machine()
        self.train = OrderedDict()
        self.clone = OrderedDict()
        self.forms = OrderedDict()
        self.full_bodies = {}

    @staticmethod
    def put(cache, key, value, cap=8192):
        cache[key] = value
        cache.move_to_end(key)
        if len(cache) > cap:
            cache.popitem(last=False)

    def semantic(self, g):
        raw = g.tobytes()
        key = self.clone.get(raw)
        if key is None:
            key = mo.semantic_key(g)
            self.put(self.clone, raw, key)
        return key

    def training(self, pop):
        keys = [self.semantic(g) for g in pop]
        missing = {}
        for key, g in zip(keys, pop):
            if key not in self.train:
                missing.setdefault(key, g)
        if missing:
            fs, preds = evaluate_population(list(missing.values()), self.task, self.cfg)
            # Keep current-batch values even if bounded insertion evicts a key.
            fresh = {key: (float(f), p == self.task.labels)
                     for key, f, p in zip(missing, fs, preds)}
        else:
            fresh = {}
        rows = [fresh[key] if key in fresh else self.train[key] for key in keys]
        for key, row in fresh.items():
            self.put(self.train, key, row)
        return np.array([r[0] for r in rows]), np.stack([r[1] for r in rows])

    def classify(self, g, perfect=True):
        if not perfect:
            return ('other', None)
        key = self.semantic(g)
        row = self.forms.get(key)
        if row is not None:
            return row
        if not self.exact(g).all():
            row = ('shortcut', None)
        else:
            c = mo.classify(g, self.full_machine, self.task.output_tags,
                            self.labels, self.full_bodies, self.cfg.tag_combine)
            helper = None
            if c['form'] == 'shared':
                values = tagged.genome_outputs(g, self.full_machine, self.full_bodies,
                                               combine=self.cfg.tag_combine, all_runs=True)
                types = []
                for i in c['pure_helpers']:
                    b = function_of(values[i], mo.X_ALL.sum(axis=1))
                    a = function_of(values[i], mo.X_ALL.max(axis=1))
                    types.append('B-helper' if b and not a else 'A-only' if a and not b else 'other')
                helper = 'B-helper' if 'B-helper' in types else 'A-only' if types and all(t == 'A-only' for t in types) else 'other'
            row = (c['form'], helper)
        self.put(self.forms, key, row)
        if len(self.exact.cache) > 8192:
            self.exact.cache.clear()
        # Full-case body caches otherwise retain 10,000-element arrays indefinitely.
        if len(self.full_bodies) > 512:
            self.full_bodies.clear()
        if len(self.exact.c_full) > 512:
            self.exact.c_full.clear()
        if len(self.exact.c_sub) > 2048:
            self.exact.c_sub.clear()
        return row

    def population(self, pop, flags=None, generation=0, cases=None):
        if cases is None:
            _, cases = self.training(pop)
        rows = [self.classify(g, bool(ok.all())) for g, ok in zip(pop, cases)]
        ne = self.cfg.elite_count
        exact = np.array([r[0] in STRATA[:3] for r in rows])
        shared = np.array([r[0] == 'shared' for r in rows])
        flags = np.zeros(len(pop), dtype=bool) if flags is None else flags
        n = int(exact[ne:].sum())
        shared_n = int(shared[ne:].sum())
        desc_n = int((shared[ne:] & flags[ne:]).sum())
        return dict(generation=generation, exact_nonelite=n,
                    forms=dict(Counter(r[0] for r in rows[ne:])),
                    total_shared_full=int(shared.sum()),
                    descendant_survival=bool(flags.any()), descendants_full=int(flags.sum()),
                    descendant_shared_full=int((shared & flags).sum()),
                    descendant_exact_shared_share=desc_n/n if n else None,
                    total_shared_share=shared_n/n if n else None,
                    descendant_helper_counts=dict(Counter(r[1] for r, f in zip(rows[ne:], flags[ne:])
                                                          if f and r[0] == 'shared')),
                    descendant_established=n >= MIN_EXACT and desc_n/n >= .5,
                    total_established=n >= MIN_EXACT and shared_n/n >= .5,
                    mean_fitness=float(self.training(pop)[0].mean()),
                    unique_genotypes=len({g.tobytes() for g in pop}))


def historical_exposure(stats, cfg):
    """Historical >90% first-form definition; 50% shared ends late exposure.

    Census is a saved 256-individual sample INCLUDING elites, unlike the new
    full non-elite verdict. Durations are explicitly a historical occupancy proxy.
    Count qualifying non-shared intervals after first establishment, until the
    first >=50% shared observation; exclude observed <20-exact occupancy intervals.
    """
    first = next((s for s in stats if s['n_fully_exact'] >= MIN_EXACT and
                  max((s.get(k) or 0) for k in STRATA[:3]) > .9), None)
    first_form = max(STRATA[:3], key=lambda k: first.get(k) or 0) if first else None
    if not first or first_form == 'shared':
        return dict(first_generation=first['gen'] if first else None, first_form=first_form,
                    duration=0, duration_known=first is not None,
                    duration_bounds=[0, 0 if first else cfg.generations],
                    midpoint=None, replacement_interval=None)
    stop = next((s for s in stats if s['gen'] > first['gen'] and
                 s['n_fully_exact'] >= MIN_EXACT and (s.get('shared') or 0) >= .5), None)
    end = stop['gen'] if stop else cfg.generations
    duration = sum(b['gen']-a['gen'] for a, b in zip(stats, stats[1:])
                   if first['gen'] <= a['gen'] < end and a['n_fully_exact'] >= MIN_EXACT
                   and (a.get('shared') or 0) < .5)
    # Lower bound counts intervals qualifying at BOTH endpoints; upper bound at EITHER.
    def occupied(s):
        return s['n_fully_exact'] >= MIN_EXACT and (s.get('shared') or 0) < .5
    low = high = 0
    for a, b in zip(stats, stats[1:]):
        if b['gen'] < first['gen'] or a['gen'] >= end:
            continue
        width = b['gen']-a['gen']
        low += width * (a['gen'] >= first['gen'] and occupied(a) and occupied(b))
        high += width * (occupied(a) or occupied(b))
    before_stop = next((a['gen'] for a, b in zip(stats, stats[1:]) if stop and b['gen'] == stop['gen']), None)
    return dict(first_generation=first['gen'], first_form=first_form, duration=duration, duration_known=True,
                duration_bounds=[low, high], midpoint=((first['gen']+end)//2//cfg.log_every)*cfg.log_every,
                replacement_interval=[before_stop, end] if stop else None)


def source_manifest(root, allow_small=False):
    sources = []
    for path in sorted(root.iterdir()):
        if not (path / 'config.yaml').exists():
            continue
        raw = yaml.safe_load((path / 'config.yaml').read_text())
        cfg = config(raw)
        if (cfg.task, cfg.arm, cfg.tape_length, cfg.crossover_rate, cfg.crossover_mate,
            cfg.n_examples, cfg.seed_tapes) != ('mbs_three', 'TAG', 64, .3, 'self', 64, ''):
            continue
        required = ('config.yaml', 'result.json', 'history.csv', 'final_population.npz')
        hashes = {name: hashlib.sha256((path/name).read_bytes()).hexdigest() for name in required}
        result = json.loads((path/'result.json').read_text())
        if result['generations_run'] != cfg.generations or result['shared_stats'][-1]['gen'] != cfg.generations:
            raise ValueError(f'Incomplete source: {path}')
        if (cfg.pop_size, cfg.elite_count, cfg.mutation_rate, cfg.selection_mode,
            cfg.tagged_crossover, cfg.tag_combine, cfg.fast_rng, cfg.n_islands) != (1024, 2, .015, 'lexicase', 'v2', 'leftmost', True, 1):
            raise ValueError(f'Unexpected source condition: {path}')
        sources.append(dict(id=path.name, path=str(path.resolve()), config=asdict(cfg), hashes=hashes,
                            historical=historical_exposure(result['shared_stats'], cfg)))
    seeds = sorted(s['config']['seed'] for s in sources)
    if not allow_small and seeds != list(range(50)):
        raise ValueError(f'Expected precisely 50 cohort seeds 0..49, found {seeds}')
    return sources


class Frozen:
    def __init__(self, source, seed, phase, pop=None):
        self.source = source
        self.cfg = config(source['config'])
        self.pop = list(np.load(Path(source['path'])/'final_population.npz')['genotypes']) if pop is None else list(pop)
        if np.stack(self.pop).shape != (self.cfg.pop_size, 2*self.cfg.tape_length):
            raise ValueError('Wrong source population shape')
        self.measure = Measurements(self.cfg)
        self.fits, self.cases = self.measure.training(self.pop)
        self.parent_forms = [self.measure.classify(g, bool(c.all()))[0] for g, c in zip(self.pop, self.cases)]
        self.rng_seed = seed + 1000*self.cfg.seed + (100 if phase == 'mid' else 0)
        self.rng = evolve.FastRandom(self.rng_seed)
        base = self.measure.population(self.pop, cases=self.cases)
        n = base['exact_nonelite']
        h = source['historical']
        # Keep the approved terminal cohort even where its historical sampled
        # census cannot date establishment (seed 23); do not invent exposure.
        self.target = n >= MIN_EXACT and h['first_form'] != 'shared'
        self.eligible = self.target and base['total_shared_share'] < .5
        self.record = dict(source=source['id'], phase=phase, seed=self.rng_seed, baseline=base,
                           target=self.target, insertion_eligible=self.eligible,
                           historical=h, generations=0, children=0, arrivals=0,
                           parent_strata={k: dict(children=0, arrivals=0, child_forms={}) for k in STRATA},
                           selected_parent_counts=[0]*len(self.pop), helper_counts={})

    def draw(self):
        parents = []
        children = evolve._reproduce_one_island(self.pop, self.fits, self.cfg, self.rng,
                                               cases=self.cases, lineage=parents)
        ne = self.cfg.elite_count
        children, parents = children[ne:], np.array(parents[ne:], dtype=np.int32)
        _, cases = self.measure.training(children)
        child_codes = np.empty(len(children), dtype=np.uint8)
        parent_codes = np.empty(len(children), dtype=np.uint8)
        helper_codes = np.zeros(len(children), dtype=np.uint8)
        events = []
        for slot, (g, row, ok) in enumerate(zip(children, parents, cases), ne):
            p = int(row[0])
            parent = self.parent_forms[p]
            child, helper = self.measure.classify(g, bool(ok.all()))
            child_codes[slot-ne], parent_codes[slot-ne] = STRATA.index(child), STRATA.index(parent)
            helper_codes[slot-ne] = HELPERS.index(helper)+1 if helper else 0
            st = self.record['parent_strata'][parent]
            st['children'] += 1
            st['child_forms'][child] = st['child_forms'].get(child, 0)+1
            self.record['selected_parent_counts'][p] += 1
            if helper:
                hc = self.record['helper_counts']
                hc[helper] = hc.get(helper, 0)+1
            if child == 'shared' and parent != 'shared':
                self.record['arrivals'] += 1
                st['arrivals'] += 1
                events.append(dict(source=self.source['id'], phase=self.record['phase'],
                                   frozen_generation=self.record['generations']+1,
                                   slot=slot, parent_index=p, parent_form=parent,
                                   parent_hex=self.pop[p].tobytes().hex(), child_hex=g.tobytes().hex(),
                                   helper=helper, census_seed=self.rng_seed))
        self.record['generations'] += 1
        self.record['children'] += len(children)
        return events, (parents, parent_codes, child_codes, helper_codes)


def finish_record(record, cfg):
    n, a = record['children'], record['arrivals']
    record['arrival_rate_all_offspring'] = a/n if n else None
    record['arrival_rate_ci95'] = binomial_interval(a, n)
    duration = record['historical']['duration'] if record['target'] else 0
    record['historical_offspring_exposure'] = duration*(cfg.pop_size-cfg.elite_count)
    known = record['historical']['duration_known']
    record['expected_arrivals'] = duration*(cfg.pop_size-cfg.elite_count)*a/n if n and known else None
    record['expected_arrivals_ci95'] = [d*(cfg.pop_size-cfg.elite_count)*v
                                       for d, v in zip(record['historical']['duration_bounds'], record['arrival_rate_ci95'])]
    for st in record['parent_strata'].values():
        st['conditional_rate'] = st['arrivals']/st['children'] if st['children'] else None
        st['conditional_ci95'] = binomial_interval(st['arrivals'], st['children'])
        st['all_offspring_contribution'] = st['arrivals']/n if n else None
    return record


def init_worker(counter):
    global _PARTLY
    _PARTLY = counter


def census_worker(payload):
    sources, seed, out, deadline, target, max_rounds = payload
    frozen = [Frozen(s, seed, 'final') for s in sources]
    buffers = {f.source['id']: [] for f in frozen}
    out = Path(out)
    handles = {f.source['id']: (out/'sources'/f.source['id']/'arrivals.jsonl').open('w') for f in frozen}
    batches = Counter()

    def flush(f):
        sid = f.source['id']
        if buffers[sid]:
            rows = buffers[sid]
            np.savez_compressed(out/'sources'/sid/f'offspring_{batches[sid]:05d}.npz',
                                parents=np.stack([r[0] for r in rows]),
                                parent_stratum=np.stack([r[1] for r in rows]),
                                child_form=np.stack([r[2] for r in rows]),
                                helper=np.stack([r[3] for r in rows]),
                                first_generation=f.record['generations']-len(rows)+1)
            buffers[sid].clear()
            batches[sid] += 1
        handles[sid].flush()
        write_json(out/'sources'/sid/'census.json', finish_record(f.record, f.cfg))

    rounds = 0
    try:
        while time.monotonic() < deadline and _PARTLY.value < target:
            if max_rounds and rounds >= max_rounds:
                break
            for f in frozen:
                if time.monotonic() >= deadline or _PARTLY.value >= target:
                    break
                before = f.record['parent_strata']['partly']['children']
                events, rows = f.draw()
                for event in events:
                    handles[f.source['id']].write(json.dumps(event)+'\n')
                buffers[f.source['id']].append(rows)
                with _PARTLY.get_lock():
                    _PARTLY.value += f.record['parent_strata']['partly']['children']-before
                if len(buffers[f.source['id']]) >= 32:
                    flush(f)
            rounds += 1
    finally:
        for f in frozen:
            flush(f)
            handles[f.source['id']].close()
    return [finish_record(f.record, f.cfg) for f in frozen]


def propagate(flags, parents):
    rows = np.asarray(parents, dtype=np.int32)
    result = flags[rows[:, 0]].copy()
    mate = rows[:, 1]
    valid = mate >= 0
    result[valid] |= flags[mate[valid]]
    return result


def loss_interval(trajectory, key):
    last = 1  # inserted copy is present immediately at generation one
    for row in trajectory:
        if row['generation'] < 1:
            continue
        if not row[key]:
            return dict(lower=last, upper=row['generation'], right_censored=False)
        last = row['generation']
    return dict(lower=last, upper=None, right_censored=True)


def continuation(payload):
    source, event, seed, horizon, out, trial = payload
    cfg = config(source['config'])
    measure = Measurements(cfg)
    original = np.load(Path(source['path'])/'final_population.npz')['genotypes']
    child = np.frombuffer(bytes.fromhex(event['child_hex']), dtype=np.uint8).copy()
    if len(child) != 2*cfg.tape_length or measure.classify(child)[0] != 'shared':
        raise ValueError('Insertion must be a fully exact natural shared child')
    arms = {}
    slot = int(np.random.default_rng([seed, 1]).integers(cfg.elite_count, cfg.pop_size))
    started = time.monotonic()
    for arm in ('insert', 'control'):
        pop = list(original.copy())
        rng = evolve.FastRandom(seed)
        flags = np.zeros(cfg.pop_size, dtype=bool)
        fits, cases = measure.training(pop)
        trajectory = [measure.population(pop, flags, 0, cases)]
        for generation in range(1, horizon+1):
            rows = []
            pop = evolve._reproduce_one_island(pop, fits, cfg, rng, cases=cases, lineage=rows)
            flags = propagate(flags, rows)
            if generation == 1 and arm == 'insert':
                pop[slot] = child.copy()
                flags[slot] = True
            fits, cases = measure.training(pop)
            if generation == 1 or generation % 10 == 0 or generation == horizon:
                trajectory.append(measure.population(pop, flags, generation, cases))
        end = trajectory[-1]
        lineage_outcome = ('established' if end['descendant_established'] else
                           'extinct' if not end['descendant_shared_full'] else 'unresolved')
        arms[arm] = dict(trajectory=trajectory, lineage_outcome=lineage_outcome if arm == 'insert' else None,
                         total_outcome='established' if end['total_established'] else
                         'extinct' if not end['total_shared_full'] else 'unresolved',
                         descendant_loss=loss_interval(trajectory, 'descendant_survival') if arm == 'insert' else None,
                         descendant_shared_first_absence=loss_interval(trajectory, 'descendant_shared_full') if arm == 'insert' else None,
                         total_shared_first_absence=loss_interval(trajectory, 'total_shared_full'))
    result = dict(trial=trial, source=source['id'], continuation_seed=seed, task_seed=cfg.seed,
                  insertion_slot=slot, arrival=event, horizon=horizon,
                  elapsed_seconds=time.monotonic()-started, arms=arms)
    write_json(Path(out)/'trials'/f'{trial:03d}.json', result)
    return result


def compare_dict(actual, expected):
    for key, value in expected.items():
        if key not in actual:
            return False
        if isinstance(value, (int, float)):
            if not np.isclose(actual[key], value, rtol=0, atol=1e-12):
                return False
        elif actual[key] != value:
            return False
    return True


def replay(source, seconds, out):
    """Verify every historical row/census, then full final population; retain midpoint."""
    cfg = config(source['config'])
    midpoint = source['historical']['midpoint']
    expected = json.loads((Path(source['path'])/'result.json').read_text())
    with (Path(source['path'])/'history.csv').open() as f:
        history = {int(r['generation']): r for r in csv.DictReader(f)}
    shared = {r['gen']: r for r in expected['shared_stats']}
    runs = {r['gen']: r for r in expected['run_stats']}
    rng = evolve.make_rng(cfg)
    pop = evolve.build_initial_population(cfg, rng, cfg.pop_size)
    task = build_task(cfg, cfg.seed)
    census = mo.SharedCensus(task, cfg.seed, cfg.tag_combine)
    stats = ChemTapeStatsCollector()
    measure = Measurements(cfg)
    mid = None
    deadline = time.monotonic()+seconds
    result = dict(source=source['id'], midpoint=midpoint, verified=False,
                  checks=['all history columns', 'all shared census fields', 'all run census fields', 'full final genotypes'])
    for gen in range(cfg.generations+1):
        if time.monotonic() >= deadline:
            result.update(reason='replay time cap', last_generation=gen-1)
            return result, None
        fits, cases = measure.training(pop)
        row = asdict(stats.record(gen, fits, pop, arm=cfg.arm))
        stats.history.clear()
        raw = history[gen]
        expected_row = {k: v if k == 'best_genotype_hex' else float(v) for k, v in raw.items()}
        if not compare_dict(row, expected_row):
            result.update(reason='history mismatch', last_generation=gen)
            return result, None
        if gen in shared:
            if not compare_dict(census.record(gen, pop, cases), shared[gen]):
                result.update(reason='shared census mismatch', last_generation=gen)
                return result, None
        if gen in runs:
            if not compare_dict(evolve._run_stats(gen, pop, cfg, task.output_tags), runs[gen]):
                result.update(reason='run census mismatch', last_generation=gen)
                return result, None
        if gen == midpoint:
            mid = np.stack(pop)
        if gen < cfg.generations:
            pop = evolve._reproduce_one_island(pop, fits, cfg, rng, cases=cases)
    saved = np.load(Path(source['path'])/'final_population.npz')['genotypes']
    result['verified'] = bool(np.array_equal(saved, np.stack(pop)))
    result['reason'] = 'exact replay' if result['verified'] else 'final population mismatch'
    if result['verified']:
        np.savez_compressed(Path(out)/'sources'/source['id']/'mid_population.npz', genotypes=mid)
    return result, mid if result['verified'] else None


def exposure_summary(records):
    target = [r for r in records if r['target']]
    total = sum(r['expected_arrivals'] or 0 for r in target)
    missing = [r['source'] for r in target if not r['historical']['duration_known']]
    # Conservative joint envelope: Bonferroni per-source binomial intervals.
    alpha = .05/max(1, len(target))
    lo = hi = 0
    for r in target:
        n, k = r['children'], r['arrivals']
        duration = r['historical']['duration_bounds']
        rate_lo = float(beta.ppf(alpha/2, k, n-k+1)) if k and n else 0
        rate_hi = float(beta.ppf(1-alpha/2, k+1, n-k)) if n and k < n else 1
        width = r['historical_offspring_exposure']/r['historical']['duration'] if r['historical']['duration'] else 1022
        lo += rate_lo*duration[0]*width
        hi += rate_hi*duration[1]*width
    return dict(target_sources=len(target), expected_arrivals_total=total if not missing else None,
                expected_arrivals_total_known_exposure=total,
                expected_arrivals_per_run=total/len(target) if target and not missing else None,
                measured_exposure_only_expected_arrivals_per_target_run=total/len(target) if target else None,
                historical_exposure_unmeasured_sources=missing,
                joint_rate_duration_envelope_per_run=[lo/len(target), hi/len(target)] if target else None,
                historical_offspring_exposure=sum(r['historical_offspring_exposure'] for r in target),
                observed_replacements=sum(r['historical']['replacement_interval'] is not None for r in target),
                duration_basis='sampled historical occupancy proxy; >90% first form, >=50% shared transition',
                terminal_shared_target_sources=[r['source'] for r in target if not r['insertion_eligible']])


def insertion_candidates(records, sources, out):
    by_id = {s['id']: s for s in sources}
    candidates, weights = [], []
    for r in records:
        if (not r['insertion_eligible'] or not r['arrivals'] or not r['children']
                or not r['historical_offspring_exposure']):
            continue
        with (out/'sources'/r['source']/'arrivals.jsonl').open() as f:
            for line in f:
                event = json.loads(line)
                candidates.append((by_id[r['source']], event))
                # One row per occurrence, weighted by historical exposure/draws.
                weights.append(r['historical_offspring_exposure']/r['children'])
    weights = np.array(weights, dtype=float)
    if weights.size:
        weights /= weights.sum()
    return candidates, weights


def trial_summary(trials):
    grouped = {}
    for sid in sorted({t['source'] for t in trials}):
        ts = [t for t in trials if t['source'] == sid]
        outcomes = Counter(t['arms']['insert']['lineage_outcome'] for t in ts)
        k = outcomes['established']
        grouped[sid] = dict(n=len(ts), lineage_outcomes=dict(outcomes), p=k/len(ts),
                            p_ci95=binomial_interval(k, len(ts)),
                            controls=dict(Counter(t['arms']['control']['total_outcome'] for t in ts)),
                            hypothesis_generating_only=len(ts) < 20)
    k = sum(t['arms']['insert']['lineage_outcome'] == 'established' for t in trials)
    return dict(n=len(trials), established=k, p=k/len(trials) if trials else None,
                p_ci95=binomial_interval(k, len(trials)), sources=grouped,
                unresolved=sum(t['arms']['insert']['lineage_outcome'] == 'unresolved' for t in trials))


def report(out, summary, records, trials):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    lines = ['# Shared arrival: exploratory readout', '',
             f"Scope: {summary['scope']}. First discovery is unmeasured.", '',
             f"Stage 1: {summary['children']:,} children; {summary['partly_children']:,} partly-parent children; "
             f"{summary['arrivals']} new exact-shared arrivals. Stop: {summary['stage1_stop']}.",
             f"Throughput: {summary['children']/max(summary['stage1_seconds'], .001):.1f} children/s.",
             f"Historical exposure estimate: {summary['exposure']}", '',
             'Historical durations use the saved sampled census including elites; they are an occupancy proxy,',
             'not a full non-elite historical count. Confidence bounds are exploratory frozen-draw bounds.',
             'Final shared populations cannot represent their earlier non-shared phase without a verified side check.', '',
             '| source | target | all offspring | arrivals | rate (95% CI) | exposure | expected arrivals |',
             '|---|---|---|---|---|---|---|']
    for r in records:
        lines.append(f"| {r['source']} | {r['target']} | {r['children']} | {r['arrivals']} | "
                     f"{r['arrival_rate_all_offspring']} {r['arrival_rate_ci95']} | "
                     f"{r['historical_offspring_exposure']} | {r['expected_arrivals']} |")
    lines += ['', 'Per-parent-stratum contributions and child forms are in census.json; all children and',
              'actual parent indices (including elites as eligible parents) are in sources/*/offspring_*.npz.',
              'Codebooks are in manifest.json. Every natural occurrence is in arrivals.jsonl.', '',
              f"Stage 2: {summary['stage2_stop']}; arrival-bearing eligible populations: {summary['arrival_sources']}.",
              'Sampling uses occurrence frequency times source exposure/draw denominator; no population cap.',
              'Fewer than five sources restrict the sampled mixture; no inference for absent sources.',
              f"Natural lineage trials: {summary['trials']}", '',
              'Five wins in 100 do not establish p >= 10%. Extinction observations are interval-censored.',
              'No natural arrivals means no foreign-genome controls and unmeasured establishment.',
              'Exact-shared lineage absence can reverse if surviving non-shared descendants mutate back;',
              'descendant loss (all forms) is absorbing. Both are reported separately.', '',
              f"Source-aligned expected lineage establishments: {summary['source_aligned_products']}",
              'Sources lacking trials have unmeasured p; do not multiply a pooled E by a different mixture p.',
              'The product is a consistency diagnostic against one historical replacement, not a claim gate.', '',
              f"Replay checks: {summary['replay']}",
              'Inspect source-specific endpoint/midpoint rates before making any historical-phase claim.',
              'Close or park the shared-helper line after review; unresolved reopens only with instrumented replay.']
    (out/'report.md').write_text('\n'.join(lines)+'\n')
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    rates = np.array([r['arrival_rate_all_offspring'] or 0 for r in records])
    bounds = np.array([r['arrival_rate_ci95'] for r in records])
    axes[0, 0].errorbar(range(len(records)), rates,
                        yerr=np.stack([rates-bounds[:, 0], bounds[:, 1]-rates]),
                        fmt='.', capsize=2)
    axes[0, 0].set(xlabel='source population', ylabel='new shared / all children',
                   title='Source rates and frozen-draw 95% intervals', ylim=(0, None))
    axes[0, 1].bar(STRATA, [sum(r['parent_strata'][k]['children'] for r in records) for k in STRATA])
    axes[0, 1].set(ylabel='children', title='Selection-weighted parent denominators')
    for trial in trials:
        tr = trial['arms']['insert']['trajectory']
        axes[1, 0].plot([r['generation'] for r in tr], [r['descendant_exact_shared_share'] or 0 for r in tr], alpha=.15, color='tab:blue')
        axes[1, 0].plot([r['generation'] for r in tr], [r['total_shared_share'] or 0 for r in tr], alpha=.1, color='tab:orange')
        axes[1, 1].plot([r['generation'] for r in tr], [r['mean_fitness'] for r in tr], alpha=.12, color='tab:green')
    if not trials:
        for ax in axes[1]:
            ax.text(.5, .5, 'No weightable natural arrivals:\ncontinuations skipped',
                    ha='center', va='center', transform=ax.transAxes)
    axes[1, 0].set(xlabel='generation', ylabel='share of exact non-elites', title='Descendant shared (blue), total shared (orange)')
    axes[1, 1].set(xlabel='generation', ylabel='mean fitness', title='Insertion population fitness; diversity logged per census')
    fig.tight_layout()
    fig.savefig(out/'diagnostics.png', dpi=140)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE)
    ap.add_argument('--out', type=Path, default=os.environ.get('RUN_DIR'))
    ap.add_argument('--workers', type=int, default=10)
    ap.add_argument('--seed', type=int, default=321350)
    ap.add_argument('--target-partly', type=int, default=30_000_000)
    ap.add_argument('--floor-partly', type=int, default=3_000_000)
    ap.add_argument('--stage1-seconds', type=float, default=7200)
    ap.add_argument('--replay-count', type=int, default=5)
    ap.add_argument('--replay-seconds', type=float, default=600, help='Total cheap side-check budget')
    ap.add_argument('--mid-rounds', type=int, default=32)
    ap.add_argument('--initial-trials', type=int, default=100)
    ap.add_argument('--max-trials', type=int, default=300)
    ap.add_argument('--horizon', type=int, default=500)
    ap.add_argument('--smoke', action='store_true', help='Two real sources, one frozen generation; never full-run evidence')
    ap.add_argument('--smoke-rounds', type=int, default=2)
    args = ap.parse_args()
    if args.out is None:
        ap.error('Specify --out or RUN_DIR')
    if args.workers < 1 or args.stage1_seconds <= 0 or args.target_partly <= 0:
        ap.error('Positive worker count, stage1 cap, and target required')
    if (args.max_trials > 300 or args.initial_trials < 1 or args.initial_trials > args.max_trials
            or args.horizon < 1 or args.smoke_rounds < 1 or args.mid_rounds < 1):
        ap.error('Invalid stage2 budget (hard cap 300 pairs)')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out/'manifest.json').exists():
        raise ValueError('Output already contains a manifest; use a fresh directory')
    sources = source_manifest(args.source_root.resolve())
    if args.smoke:
        args.seed = 321359
        # Preserve a target partly population and a descriptive unsolved one.
        target = next(s for s in sources if s['historical']['first_form'] == 'partly'
                      and s['historical']['replacement_interval'] is None)
        other = next(s for s in sources if s['historical']['first_form'] is None)
        sources = [target, other]
        args.replay_count = 0
        args.initial_trials = args.max_trials = 2
        args.horizon = 20
    for source in sources:
        (out/'sources'/source['id']).mkdir(parents=True, exist_ok=True)
    (out/'trials').mkdir(exist_ok=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    write_json(out/'manifest.json', dict(args={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                                         sources=sources, git_commit=commit,
                                         git_dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'])),
                                         codebooks=dict(strata=STRATA, helper=['none', *HELPERS],
                                                        parent_columns=['parent1', 'parent2', 'kind', 'mutated']),
                                         full_run_evidence=not args.smoke))
    ctx = mp.get_context('spawn')
    workers = min(args.workers, len(sources))
    partly = ctx.Value('q', 0)
    started = time.monotonic()
    jobs = [(sources[i::workers], args.seed, str(out), started+args.stage1_seconds,
             args.target_partly, args.smoke_rounds if args.smoke else 0) for i in range(workers)]
    with ctx.Pool(workers, initializer=init_worker, initargs=(partly,)) as pool:
        records = [r for group in pool.map(census_worker, jobs) for r in group]
    records.sort(key=lambda r: r['source'])
    stage1_seconds = time.monotonic()-started
    if any(not r['children'] for r in records):
        raise RuntimeError('Stage1 cap ended before every source had a draw; enlarge smoke cap or inspect throughput')
    if not args.smoke and sum(r['target'] for r in records) != 16:
        raise ValueError('Saved cohort no longer reproduces the approved 16-source target')
    write_json(out/'census.json', records)
    with (out/'arrivals.jsonl').open('w') as joined:
        for source in sources:
            joined.write((out/'sources'/source['id']/'arrivals.jsonl').read_text())
    print(f"Stage1: {sum(r['children'] for r in records):,} children, {partly.value:,} partly, "
          f"{sum(r['arrivals'] for r in records)} arrivals in {stage1_seconds:.1f}s", flush=True)
    exp = exposure_summary(records)
    replays = []
    replay_deadline = time.monotonic()+args.replay_seconds
    candidates = [s for s in sources if s['historical']['first_form'] == 'partly' and
                  not s['historical']['replacement_interval']]
    for source in candidates[:args.replay_count]:
        budget = replay_deadline-time.monotonic()
        if budget <= 0:
            break
        verified, pop = replay(source, budget, out)
        replays.append(verified)
        if pop is not None:
            f = Frozen(source, args.seed, 'mid', pop)
            mid_rows = []
            for _ in range(args.mid_rounds):
                if time.monotonic() >= replay_deadline:
                    break
                events, rows = f.draw()
                mid_rows.append(rows)
                with (out/'sources'/source['id']/'mid_arrivals.jsonl').open('a') as fh:
                    fh.writelines(json.dumps(e)+'\n' for e in events)
            if mid_rows:
                np.savez_compressed(out/'sources'/source['id']/'mid_offspring.npz',
                                    parents=np.stack([r[0] for r in mid_rows]),
                                    parent_stratum=np.stack([r[1] for r in mid_rows]),
                                    child_form=np.stack([r[2] for r in mid_rows]),
                                    helper=np.stack([r[3] for r in mid_rows]), first_generation=1)
            write_json(out/'sources'/source['id']/'mid_census.json', finish_record(f.record, f.cfg))
            verified['census'] = f.record
            final = next(r for r in records if r['source'] == source['id'])
            mid_ci, final_ci = f.record['arrival_rate_ci95'], final['arrival_rate_ci95']
            verified['endpoint_midpoint_ci_overlap'] = max(mid_ci[0], final_ci[0]) <= min(mid_ci[1], final_ci[1])
            verified['representativeness'] = ('rate difference detected; historical extrapolation unresolved'
                                             if not verified['endpoint_midpoint_ci_overlap'] else
                                             'difference not resolved; overlap is not equivalence')
    natural, weights = insertion_candidates(records, sources, out)
    sample_rng = np.random.default_rng([args.seed, 2])
    trials = []
    arrival_sources = sorted({s['id'] for s, _ in natural})
    stop = 'no weightable target natural arrivals; establishment unmeasured; no transfers'
    if natural:
        def run_trials(start, end):
            indices = sample_rng.choice(len(natural), size=end-start, p=weights)
            payload = [(natural[i][0], natural[i][1], 321351000+j, args.horizon, str(out), j)
                       for j, i in enumerate(indices, start)]
            with ctx.Pool(args.workers) as pool:
                for result in pool.imap_unordered(continuation, payload):
                    trials.append(result)
                    print(f"Trial {result['trial']}: {result['arms']['insert']['lineage_outcome']} "
                          f"({result['elapsed_seconds']:.1f}s)", flush=True)
        run_trials(0, args.initial_trials)
        ts = trial_summary(trials)
        e = exp['measured_exposure_only_expected_arrivals_per_target_run'] or 0
        if ts['established'] >= 5:
            stop = '>=5 lineage establishments at first stage; bounds reported, not p>=10%'
        elif e <= 1 and not exp['historical_exposure_unmeasured_sources']:
            stop = 'endpoint arrival estimate <=1 per historical target run'
        elif e >= 10 and args.max_trials > args.initial_trials:
            run_trials(args.initial_trials, args.max_trials)
            stop = 'extended stage completed at hard cap'
        else:
            stop = 'intermediate exposure: stopped after initial stage; comparison may remain unresolved'
    ts = trial_summary(trials)
    aligned = []
    for r in records:
        if not r['target']:
            continue
        p = ts['sources'].get(r['source'])
        aligned.append(dict(source=r['source'], E=r['expected_arrivals'], p=p['p'] if p else None,
                            E_times_p=r['expected_arrivals']*p['p'] if p and r['expected_arrivals'] is not None else None,
                            status='measured' if p and r['expected_arrivals'] is not None else 'E or p unmeasured'))
    summary = dict(scope='verified midpoint populations plus final populations; whole-phase representativeness unresolved' if len(replays) == 5 and all(r['verified'] and r.get('census', {}).get('children', 0) for r in replays)
                   else 'final populations only (historical exposures are a labelled extrapolation)',
                   children=sum(r['children'] for r in records), partly_children=partly.value,
                   arrivals=sum(r['arrivals'] for r in records), stage1_seconds=stage1_seconds,
                   stage1_stop='smoke' if args.smoke else 'target' if partly.value >= args.target_partly else 'wall cap',
                   target_reached=partly.value >= args.target_partly, floor_reached=partly.value >= args.floor_partly,
                   exposure=exp, stage2_stop=stop, arrival_sources=arrival_sources,
                   historical_scope_limitations=[
                       'sampled historical occupancy, not full non-elite census',
                       'one unknown historical duration',
                       'replacement source ends shared, unlike its historical non-shared phase',
                       'midpoint CI overlap does not establish equivalence'],
                   source_concentration={sid: float(sum(w for (s, _), w in zip(natural, weights) if s['id'] == sid)) for sid in arrival_sources},
                   trials=ts, source_aligned_products=aligned, replay=replays,
                   interpretation='Advisory only: inspect source rates, fidelity, bounds, lineage fates and controls against plan grid.')
    write_json(out/'summary.json', summary)
    report(out, summary, records, trials)
    (out/'COMPLETE').write_text('smoke\n' if args.smoke else 'ok\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
