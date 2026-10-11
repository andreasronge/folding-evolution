"""2353 development-bank procedure comparison; unchanged 83c7c5b executor."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import signed_chain_run as chain, signed_gate_run as prior
from experiments.chem_tape import order_run as base, rebound_library as rebound
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json

TASK = "2026-10-11-2353"
ARMS = ("R-tree", "R-all", "R-bind", "R-gate")
LIBRARY_ARMS = ("R-all", "R-bind")
BOOTSTRAP_SEED = 202610112353
DRAWS = 8192
CHAIN_DRIVER_SHA = "623add858c0855c3c18d479a3eed76860950063821d587ad62a66d65cacd237a"
PAYLOADS = (
    "bank",
    "method_freeze",
    "libraries",
    "rebound_libraries",
    "schedules",
    "smoke_schedule",
    "seed_audit",
    "rebinding_validation",
    "helper_draws",
)


def roster(bank):
    return [c["id"] for c in bank["screen"]["cells"] if c["retained"]]


def schedules(bank, repeats=6, smoke=False):
    if repeats not in (5, 6):
        raise ValueError("approved repeat counts are five or six")
    cells = roster(bank)[:2] if smoke else roster(bank)
    return [
        dict(
            cell=c,
            build=b,
            repeat=r,
            arm=a,
            seeds=[
                (20580000 + (ci * 2 + b) * 8 + k)
                if smoke
                else (20481000 + ((ci * 24 + b) * 6 + r) * 8 + k)
                for k in range(8)
            ],
        )
        for ci, c in enumerate(cells)
        for b in range(2 if smoke else 24)
        for r in range(1 if smoke else repeats)
        for a in ARMS
        if smoke or r == 0 or a in LIBRARY_ARMS
    ]


def seed_audit(bank, old_schedule, old_audit, repeats=6):
    previous = chain.seed_audit(bank, old_schedule, old_audit, confirm=True)
    historic = set()

    def collect(value, key=""):
        if isinstance(value, dict):
            for k, v in value.items():
                collect(v, k if "seed" in k else key)
        elif isinstance(value, list):
            for v in value:
                collect(v, key)
        elif isinstance(value, int) and "seed" in key:
            historic.add(value)

    # Reconstruct the complete historical values, not just the prior hash.
    collect(old_schedule)
    collect(old_audit)
    import gzip

    collect(
        json.loads(gzip.decompress((prior.DATA / "presearch.json.gz").read_bytes()))
    )
    for lo, hi in (
        (19380000, 19384718),
        (19480000, 19484718),
        (19390000, 19393028),
        (20440000, 20443028),
    ):
        historic.update(range(lo, hi))
    for confirm in (False, True):
        for smoke in (False, True):
            for m in chain.schedules(bank, smoke, confirm):
                historic.update(m["seeds"])
    published, used = {}, set(historic)
    for smoke in (False, True):
        uses = {}
        for m in schedules(bank, repeats, smoke):
            for k, s in enumerate(m["seeds"]):
                uses.setdefault(s, []).append((m, k))
        for records in uses.values():
            m = records[0][0]
            arms = set(ARMS if smoke or m["repeat"] == 0 else LIBRARY_ARMS)
            if (
                len(records) != len(arms)
                or {v["arm"] for v, _ in records} != arms
                or len({(v["build"], v["cell"], v["repeat"], k) for v, k in records})
                != 1
            ):
                raise ValueError("unintended seed reuse")
        values = set(uses)
        if values & used:
            raise ValueError("historical/full/smoke seed collision")
        published["smoke" if smoke else "full"] = sorted(values)
        used.update(values)
    identity = set(range(20590000, 20590008))
    if identity & used:
        raise ValueError("identity replay seed collision")
    published["identity_replay"] = sorted(identity)
    return dict(
        admitted=True,
        historical_count=len(historic),
        historical_hash=digest(sorted(historic)),
        prior_2150_audit_hash=digest(previous),
        published_seed_sets=published,
        pairing="same unit across arms; reference arms only at repeat zero",
    )


def freeze(bank, libs, identities, repeats):
    if (
        hashlib.sha256(Path(chain.__file__).read_bytes()).hexdigest()
        != CHAIN_DRIVER_SHA
    ):
        raise ValueError("83c7c5b signed-chain driver changed")
    frozen = chain.freeze(bank, libs, identities, confirm=True)
    if len(roster(bank)) != 24 or any(
        lib["acquisition_evaluations"] <= 0 for lib in libs
    ):
        raise ValueError("full roster or historical acquisition charge mismatch")
    frozen.update(
        task=TASK,
        repeats=repeats,
        arms=list(ARMS),
        cells=roster(bank),
        reference_repeats=1,
        reference_pairing="repeat zero, independent build/cell seed groups",
        scope="All 24 cells are development; supplied symmetry on frozen acquired content",
        donors="uniform original entry x uniform all 24 permutations; duplicate slots retained",
        bootstrap=dict(
            seed=BOOTSTRAP_SEED,
            draws=DRAWS,
            unit="paired crossed build/cell resampling, repeats averaged within units",
        ),
        inference=dict(
            primary="R-bind/R-all pooled capped arithmetic mean evaluations",
            precedence=[
                "upper95 < .90: material_gain",
                "otherwise lower95 > .85: small_none_or_harm",
                "otherwise unresolved",
            ],
            harm="lower95 > 1.00",
        ),
        validity=dict(
            R_tree_first_attempt_max=0.85,
            R_tree_cap_max=0.25,
            R_gate_solve_min=0.95,
            R_all_R_tree_typical_range=[0.6, 1.0],
        ),
        r_selection="smoke mean R-bind worker seconds / R-all >1.3 =>5, otherwise6",
        authorized_searches=len(schedules(bank, repeats)),
        rebound_constructor="entry-major, lexicographic permutation order, no deduplication",
    )
    for key in (
        "protected_count",
        "protected_searches",
        "authorized_protected_searches",
    ):
        frozen.pop(key, None)
    return frozen


def helper_draws(bank, validation):
    result = []
    for d in validation["per_build"]:
        for cell in bank["screen"]["cells"]:
            if not cell["retained"]:
                continue
            arms = {}
            for arm in LIBRARY_ARMS:
                counts, slots = d["arms"][arm]["helper_counts"], d["arms"][arm]["slots"]
                probabilities = {h: counts.get(h, 0) / slots for h in cell["helpers"]}
                arms[arm] = dict(
                    needed_helper_probabilities=probabilities,
                    needed_helper_draw_probability=sum(probabilities.values()),
                    needed_helpers_present=sum(p > 0 for p in probabilities.values()),
                    total_helper_probability=d["arms"][arm]["helper_slots"] / slots,
                )
            arms["R-gate"] = dict(
                needed_helper_probabilities={h: 1 / 24 for h in cell["helpers"]},
                needed_helper_draw_probability=3 / 24,
                needed_helpers_present=3,
                total_helper_probability=1.0,
            )
            arms["R-tree"] = dict(
                needed_helper_draw_probability=None,
                scope="No library draws; ordinary tree-donor helper arrival unmeasured",
            )
            result.append(
                dict(
                    build=d["build"], cell=cell["id"], needed=cell["helpers"], arms=arms
                )
            )
    for b in range(24):
        means = [
            np.mean(
                [
                    r["arms"][a]["needed_helper_draw_probability"]
                    for r in result
                    if r["build"] == b
                ]
            )
            for a in LIBRARY_ARMS
        ]
        if not np.isclose(*means, rtol=0, atol=1e-14):
            raise ValueError("roster-averaged needed-helper draw mass changed")
    return result


def envelopes(metas, bank, libs, expanded, frozen, smoke=False):
    expected = {
        json.dumps(m, sort_keys=True) for m in schedules(bank, frozen["repeats"], smoke)
    }
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    jobs = []
    for m in metas:
        if json.dumps(m, sort_keys=True) not in expected:
            raise ValueError("unapproved search requested")
        donors = (
            None
            if m["arm"] == "R-tree"
            else frozen["gates"]
            if m["arm"] == "R-gate"
            else [e["prefix"] for e in libs[m["build"]]["semantic"]]
            if m["arm"] == "R-all"
            else [e["prefix"] for e in expanded[m["build"]]]
        )
        jobs.append(
            (
                m,
                dict(id=m["cell"], labels=by[m["cell"]]["labels"]),
                bank["inputs"],
                65536,
                donors,
            )
        )
    return jobs


def identity_replay(bank, libs, expanded, frozen):
    meta = dict(
        cell=roster(bank)[0],
        build=0,
        repeat=0,
        arm="R-all",
        seeds=list(range(20590000, 20590008)),
    )
    cell = next(c for c in bank["screen"]["cells"] if c["id"] == meta["cell"])
    envelope = (
        meta,
        dict(id=cell["id"], labels=cell["labels"]),
        bank["inputs"],
        65536,
        [e["prefix"] for e in libs[0]["semantic"]],
    )
    identity = [e["prefix"] for e in expanded[0] if e["permutation"] == [0, 1, 2, 3]]
    if identity != envelope[-1]:
        raise ValueError("identity donor order changed")
    first, second = base.execute(envelope), base.execute(envelope[:-1] + (identity,))

    # All deterministic fields must replay; only wall-clock measurements differ.
    def strip(value):
        if isinstance(value, dict):
            return {k: strip(v) for k, v in value.items() if "seconds" not in k}
        if isinstance(value, list):
            return [strip(v) for v in value]
        return value

    if strip(first) != strip(second):
        raise ValueError("identity production search replay mismatch")
    prior.validate_rows([first], [meta], bank)
    return dict(
        complete=True,
        deterministic_hash=digest(strip(first)),
        seeds=meta["seeds"],
        evaluations=first["evaluations"],
        worker_seconds=[first["worker_seconds"], second["worker_seconds"]],
        scope="Identity-only R-all replay, excluded from efficacy and r selection",
    )


def prepare(args, out, deadline):
    start = time.monotonic()
    bank = chain.load_bank()
    rebuilt = chain.bank_module.build(deadline)
    if not rebuilt["admitted"] or chain.admission_identity(
        rebuilt
    ) != chain.admission_identity(bank):
        raise ValueError("chain admission replay mismatch")
    libs, identities, old_schedule, old_audit = chain.saved_libraries()
    frozen = freeze(bank, libs, identities, args.repeats)
    audit = seed_audit(bank, old_schedule, old_audit, args.repeats)
    tick = time.monotonic()
    expanded = [rebound.expand(lib["semantic"]) for lib in libs]
    construction = time.monotonic() - tick
    validation = rebound.validate(libs, expanded, bank["inputs"], deadline)
    data = dict(
        bank=bank,
        method_freeze=frozen,
        libraries=libs,
        rebound_libraries=expanded,
        schedules=schedules(bank, args.repeats),
        smoke_schedule=schedules(bank, args.repeats, True),
        seed_audit=audit,
        rebinding_validation=validation,
        helper_draws=helper_draws(bank, validation),
    )
    p = dict(
        admitted=True,
        destination_searches=0,
        construction_seconds=construction,
        verification_seconds=validation["seconds"],
        seconds=time.monotonic() - start,
        admission_identity_hash=digest(chain.admission_identity(rebuilt)),
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"])
        .decode()
        .strip(),
    )
    for name, value in data.items():
        write_json(out, name + ".json", value)
        p[name + "_hash"] = digest(value)
    p["preparation_hash"] = digest(p)
    write_json(out, "preparation.json", p)
    print(
        "prepared",
        round(p["seconds"], 3),
        "seconds",
        frozen["authorized_searches"],
        "jobs",
        flush=True,
    )


def load_prepared(path):
    if (path / "failure.json").exists():
        raise ValueError("preparation has recorded failure")
    data = {
        name: json.loads((path / (name + ".json")).read_text()) for name in PAYLOADS
    }
    p = json.loads((path / "preparation.json").read_text())
    bank, libs = data["bank"], data["libraries"]
    original, identities, old_schedule, old_audit = chain.saved_libraries()
    r = data["method_freeze"]["repeats"]
    if (
        not p["admitted"]
        or digest(bank) != digest(chain.load_bank())
        or libs != original
        or data["rebound_libraries"]
        != [rebound.expand(lib["semantic"]) for lib in libs]
        or digest(data["method_freeze"]) != digest(freeze(bank, libs, identities, r))
        or data["schedules"] != schedules(bank, r)
        or data["smoke_schedule"] != schedules(bank, r, True)
        or data["seed_audit"] != seed_audit(bank, old_schedule, old_audit, r)
        or not data["rebinding_validation"]["complete"]
        or data["helper_draws"] != helper_draws(bank, data["rebinding_validation"])
        or p["admission_identity_hash"] != digest(chain.admission_identity(bank))
        or p["preparation_hash"]
        != digest({k: v for k, v in p.items() if k != "preparation_hash"})
        or any(p[name + "_hash"] != digest(v) for name, v in data.items())
    ):
        raise ValueError("rebinding preparation provenance mismatch")
    return data, p


def classify(interval):
    low, high = interval
    return (
        "material_gain"
        if high < 0.90
        else "harm"
        if low > 1
        else "small_none_or_harm"
        if low > 0.85
        else "unresolved"
    )


def timing_selection(arms):
    ratio = (
        arms["R-bind"]["worker_seconds"]["mean"]
        / arms["R-all"]["worker_seconds"]["mean"]
    )
    return dict(
        worker_cost_ratio=ratio,
        selected_repeats=5 if ratio > 1.3 else 6,
        rule="strict >1.3 selects five; otherwise six; timing only",
        efficacy_use=False,
    )


def summarize(rows, data, elapsed, workers, smoke=False):
    bank, frozen, draws = data["bank"], data["method_freeze"], data["helper_draws"]
    rows = prior.validate_rows(rows, schedules(bank, frozen["repeats"], smoke), bank)
    cells, builds = (roster(bank)[:2], 2) if smoke else (roster(bank), 24)
    by = {(r["build"], r["cell"], r["repeat"], r["arm"]): r for r in rows}
    arrays = {
        metric: {
            arm: np.asarray(
                [
                    [
                        [
                            by[b, c, r, arm][metric]
                            for r in range(
                                1
                                if smoke or arm not in LIBRARY_ARMS
                                else frozen["repeats"]
                            )
                        ]
                        for c in cells
                    ]
                    for b in range(builds)
                ],
                dtype=float,
            )
            for arm in ARMS
        }
        for metric in ("evaluations", "worker_seconds")
    }
    arms = {a: chain.stats([r for r in rows if r["arm"] == a]) for a in ARMS}
    report = dict(
        complete=True,
        task=TASK,
        smoke=smoke,
        arms=arms,
        decision="timing_only_no_efficacy_verdict",
        repeats=frozen["repeats"],
        per_cell=[
            dict(
                arm=a,
                cell=c,
                stats=chain.stats(
                    [r for r in rows if r["arm"] == a and r["cell"] == c]
                ),
            )
            for a in ARMS
            for c in cells
        ],
        per_build=[
            dict(
                arm=a,
                build=b,
                stats=chain.stats(
                    [r for r in rows if r["arm"] == a and r["build"] == b]
                ),
            )
            for a in ARMS
            for b in range(builds)
        ],
        throughput=dict(
            wall_seconds=elapsed,
            workers=workers,
            effective_concurrency=sum(r["worker_seconds"] for r in rows) / elapsed,
            jobs_per_second=len(rows) / elapsed,
        ),
        donor_diagnostics=data["rebinding_validation"]["per_build"],
        helper_draws=draws,
        bootstrap=dict(seed=BOOTSTRAP_SEED, draws=DRAWS),
        scope=frozen["scope"],
        next_action="Return to strategy; no automatic top-up",
    )
    if smoke:
        report["timing_selection"] = timing_selection(arms)
        return report
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    bi, ci = (
        rng.integers(builds, size=(DRAWS, builds)),
        rng.integers(len(cells), size=(DRAWS, len(cells))),
    )

    def boot(a):
        return prior.bootstrap_mean(a, bi, ci)

    contrasts = {}
    for numerator, denominator, pairing in (
        ("R-bind", "R-all", "all_library_repeats"),
        ("R-bind", "R-tree", "repeat_zero"),
        ("R-gate", "R-bind", "repeat_zero"),
        ("R-all", "R-tree", "repeat_zero"),
    ):
        contrasts[numerator + "/" + denominator] = dict(pairing=pairing)
        for metric, aa in arrays.items():
            a, b = aa[numerator], aa[denominator]
            if pairing == "repeat_zero":
                a, b = a[:, :, :1], b[:, :, :1]
            contrasts[numerator + "/" + denominator][metric] = prior.estimate(
                a.mean() / b.mean(), boot(a) / boot(b)
            )
    primary = contrasts["R-bind/R-all"]["evaluations"]
    validity = chain.validity_checks(arms)
    baseline_ratio = contrasts["R-all/R-tree"]["evaluations"]["point"]
    validity.update(
        R_all_R_tree=baseline_ratio,
        R_all_atypical=not 0.6 <= baseline_ratio <= 1,
        atypical_comparison="repeat-zero paired capped mean ratio",
    )
    validity["intended_interpretation_supported"] &= not validity["R_all_atypical"]
    coverage = {
        (r["build"], r["cell"]): r["arms"]["R-all"]["needed_helpers_present"]
        for r in draws
    }
    strata = []
    for n in range(4):
        rr = {
            a: [
                r
                for r in rows
                if r["arm"] == a and coverage[r["build"], r["cell"]] == n
            ]
            for a in LIBRARY_ARMS
        }
        strata.append(
            dict(
                needed_helpers_present=n,
                units=len(rr["R-all"]) // frozen["repeats"],
                stats={a: chain.stats(v) if v else None for a, v in rr.items()},
                ratio=None
                if not rr["R-all"]
                else float(
                    np.mean([r["evaluations"] for r in rr["R-bind"]])
                    / np.mean([r["evaluations"] for r in rr["R-all"]])
                ),
                scope="Descriptive, confounded; no stratum equality or causal test",
            )
        )
    economics = []
    aa = arrays["evaluations"]
    acq = np.asarray([lib["acquisition_evaluations"] for lib in data["libraries"]])
    acq_boot = acq[bi].mean(1)
    # r=0 for all reference comparisons; all repeats for the primary library contrast.
    for n in (10, 100):
        for a, b in (
            ("R-bind", "R-all"),
            ("R-bind", "R-tree"),
            ("R-all", "R-tree"),
            ("R-gate", "R-bind"),
        ):
            ca, cb = aa[a], aa[b]
            pairing = (
                "all_library_repeats"
                if (a, b) == ("R-bind", "R-all")
                else "repeat_zero"
            )
            if pairing == "repeat_zero":
                ca, cb = ca[:, :, :1], cb[:, :, :1]
            A, B = (
                acq.mean() if a in LIBRARY_ARMS else 0,
                acq.mean() if b in LIBRARY_ARMS else 0,
            )
            Ab, Bb = (
                acq_boot if a in LIBRARY_ARMS else 0,
                acq_boot if b in LIBRARY_ARMS else 0,
            )
            economics.append(
                dict(
                    searches=n,
                    contrast=a + "/" + b,
                    pairing=pairing,
                    numerator_total=float(A + n * ca.mean()),
                    denominator_total=float(B + n * cb.mean()),
                    ratio=prior.estimate(
                        (A + n * ca.mean()) / (B + n * cb.mean()),
                        (Ab + n * boot(ca)) / (Bb + n * boot(cb)),
                    ),
                    difference=prior.estimate(
                        A + n * ca.mean() - B - n * cb.mean(),
                        Ab + n * boot(ca) - Bb - n * boot(cb),
                    ),
                )
            )
    report.update(
        validity_checks=validity,
        primary="R-bind/R-all pooled capped arithmetic mean evaluations",
        contrasts=contrasts,
        decision=classify(primary["interval95"]),
        threshold_facts=dict(
            saving_above_10_percent_established=primary["interval95"][1] < 0.90,
            saving_above_15_percent_excluded=primary["interval95"][0] > 0.85,
            harm_established=primary["interval95"][0] > 1,
        ),
        R_all_coverage_strata=strata,
        economics=economics,
        economics_scope="A is each build's archived historical acquisition evaluations (proposal rounded mean 216k); both libraries charged once. Construction and production verification seconds reported separately; historical worker seconds not interchangeable with current load.",
        interpretation="Whole rebinding procedure, including non-helper/input-supply changes; distributional input symmetry, not identical-seed trajectories. Broad intervals do not establish equality or a bottleneck.",
    )
    return report


def plots(out, rows, libs, expanded):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 4, figsize=(17, 4))
    xs = [256, 4096, 16384, 65536, 131072, 262144, 524288]
    for a in ARMS:
        rr = [r for r in rows if r["arm"] == a]
        axes[0].plot(
            xs,
            [np.mean([r["solved"] and r["evaluations"] <= x for r in rr]) for x in xs],
            label=a,
        )
        for panel, field in ((1, "curve"), (2, "phenotype_diversity_curve")):
            lines = []
            for r in rr:
                line, offset = [], 0
                for attempt in r["attempts"]:
                    line.extend((offset + p[0], p[1]) for p in attempt[field])
                    offset += attempt["evaluations"]
                lines.append(line)
            axes[panel].plot(
                xs,
                [
                    np.mean(
                        [
                            ([v for t, v in line if t <= x] or [line[0][1]])[-1]
                            for line in lines
                        ]
                    )
                    for x in xs
                ],
                label=a,
            )
    for ax, title in zip(
        axes[:3],
        (
            "Exact D625 solves",
            "Training best; restarts",
            "Training phenotype diversity",
        ),
    ):
        ax.set(xscale="log", xlabel="Capped evaluations", title=title)
        ax.legend(fontsize=7)
    axes[3].plot([len(lib["semantic"]) for lib in libs], label="R-all")
    axes[3].plot([len(lib) for lib in expanded], label="R-bind (duplicates retained)")
    axes[3].set(xlabel="Saved build", ylabel="Donor slots", yscale="log")
    axes[3].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=140)
    plt.close(fig)


def score(args, out, deadline):
    started = time.monotonic()
    data, p = load_prepared(Path(args.prepared))
    bank, libs, expanded, frozen = (
        data[k] for k in ("bank", "libraries", "rebound_libraries", "method_freeze")
    )
    smoke = args.phase == "smoke"
    if smoke:
        write_json(
            out, "identity_replay.json", identity_replay(bank, libs, expanded, frozen)
        )
    metas = schedules(bank, frozen["repeats"], smoke)
    for name in ("bank", "method_freeze", "helper_draws", "rebinding_validation"):
        write_json(out, name + ".json", data[name])
    write_json(out, "schedules.json", metas)
    rows, elapsed = base.run_batch(
        out,
        "score.jsonl",
        envelopes(metas, bank, libs, expanded, frozen, smoke),
        args.workers,
        deadline,
    )
    report = summarize(rows, data, elapsed, args.workers, smoke)
    plots(out, rows, libs, expanded)
    report.update(
        preparation_hash=p["preparation_hash"],
        score_rows_hash=digest(prior.validate_rows(rows, metas, bank)),
        construction_seconds=p["construction_seconds"],
        verification_seconds=p["verification_seconds"],
        replay_and_reporting_seconds=time.monotonic() - started - elapsed,
        seconds=time.monotonic() - started,
    )
    if not smoke:
        write_json(out, "validity_checks.json", report["validity_checks"])
    write_json(out, "report.json", report)
    print(
        "scored",
        len(rows),
        "jobs",
        round(elapsed, 3),
        "batch seconds",
        report["decision"],
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "smoke", "score"))
    parser.add_argument("--prepared")
    parser.add_argument("--repeats", type=int, choices=(5, 6), default=6)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seconds", type=int)
    args = parser.parse_args()
    limit = 870 if args.phase == "prepare" else 870 if args.phase == "smoke" else 12870
    seconds = args.seconds or limit
    if (
        args.workers < 1
        or seconds <= 0
        or seconds > limit
        or os.environ.get("RAYON_NUM_THREADS") != "1"
        or (args.phase != "prepare" and not args.prepared)
    ):
        parser.error(
            "positive workers, fixed phase limits, RAYON_NUM_THREADS=1, and --prepared for scoring required"
        )
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    if any(
        (out / n).exists()
        for n in ("preparation.json", "report.json", "score.jsonl", "failure.json")
    ):
        parser.error("RUN_DIR contains previous experiment artifacts")
    deadline = time.monotonic() + seconds
    try:
        (prepare if args.phase == "prepare" else score)(args, out, deadline)
        if time.monotonic() > deadline:
            raise TimeoutError("fixed deadline exceeded during verification/report")
    except Exception as error:
        write_json(
            out,
            "failure.json",
            dict(admitted=False, phase=args.phase, error=str(error)),
        )
        raise


if __name__ == "__main__":
    main()
