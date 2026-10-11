"""2044 development probe and opt-in 2150 protected confirmation; frozen content."""

import argparse
import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import signed_chain_bank as bank_module
from experiments.chem_tape import (
    signed_gate_run as prior,
    signed_gate_bank as gates,
    order_run as base,
)
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_gp_search import Tree
from experiments.chem_tape.tree_library import verify_entries

TASK = "2026-10-11-2044"
DATA = Path(__file__).with_name("data") / "signed_chain_2044"
ARCHIVE_SHA = "2e6b84e2b1c74a39005eb17fa7b273bc2249bbbdec80ce62224d88b8059b81ca"
BANK_HASH = "e3873e170b71ffcb69bea99b0d2cf4afd7062a5b6ab28ef2a9e59608f6c6d175"
ARMS = ("R-tree", "R-all", "R-gate")
BOOTSTRAP_SEED = 202610112044
DRAWS = 8192
CONFIRM_TASK = "2026-10-11-2150"
CONFIRM_BOOTSTRAP_SEED = 202610112150
REVIEWED_SHA = "e9a14075090564caca352122c756cf3aabb6074289074a9fe3368935608c2eea"


def saved_libraries():
    """Replay the complete original acquisition; never extract from new targets."""
    raw = (DATA / "saved_1938.json.gz").read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA:
        raise ValueError("saved 1938 archive hash mismatch")
    archive = json.loads(gzip.decompress(raw))
    files = archive["files"]
    if any(
        hashlib.sha256(v.encode()).hexdigest() != archive["file_sha256"][k]
        for k, v in files.items()
    ):
        raise ValueError("saved file hash mismatch")
    bank, frozen, libs, schedule, p, audit = [
        json.loads(files[n + ".json"])
        for n in (
            "bank",
            "method_freeze",
            "libraries",
            "schedules",
            "preparation",
            "seed_audit",
        )
    ]
    rows = prior.validate_rows(
        [json.loads(line) for line in files["acquisition.jsonl"].splitlines()],
        prior.schedules(bank)["source"],
        bank,
    )
    if (
        digest(bank) != prior.BANK_HASH
        or not bank["admitted"]
        or not bank["screen"]["complete"]
        or not p["admitted"]
        or p["smoke"]
        or len(libs) != 24
        or schedule != prior.schedules(bank)
        or p["preparation_hash"]
        != digest({k: v for k, v in p.items() if k != "preparation_hash"})
        or any(
            p[k + "_hash"] != digest(v)
            for k, v in [
                ("source_rows", rows),
                ("libraries", libs),
                ("bank", bank),
                ("freeze", frozen),
                ("schedule", schedule),
                ("audit", audit),
            ]
        )
    ):
        raise ValueError("1938 acquisition provenance mismatch")
    gates.verify(bank["screen"]["cells"])
    if bank["split"] != gates.split(
        [c for c in bank["screen"]["cells"] if c["retained"]]
    ):
        raise ValueError("1938 source roster mismatch")
    current = method_hashes()
    for path, expected in frozen["methods"].items():
        if current.get(path) != expected:
            raise ValueError("1938 reviewed method changed: " + path)
    if prior.deterministic(libs) != prior.deterministic(
        prior.libraries_from(rows, bank, 24)
    ):
        raise ValueError("1938 source-only reconstruction mismatch")
    identities = [
        dict(
            build=b,
            library_hash=digest(lib["semantic"]),
            source_rows_hash=digest([r for r in rows if r["build"] == b]),
            source_cells=bank["split"]["source"],
            source_repeats=2,
            source_commit=json.loads(files["metadata.json"])["git_commit"],
        )
        for b, lib in enumerate(libs)
    ]
    return libs, identities, schedule, audit


def load_bank():
    gates.executable_check()
    bank = json.loads((DATA / "manifest.json").read_text())
    if (
        digest(bank) != BANK_HASH
        or not bank["admitted"]
        or not bank["screen"]["complete"]
    ):
        raise ValueError("chain frozen bank hash/admission mismatch")
    bank_module.verify(bank["screen"]["cells"])
    if bank["split"] != bank_module.split(
        [c for c in bank["screen"]["cells"] if c["retained"]]
    ):
        raise ValueError("chain frozen roster mismatch")
    return bank


def schedules(bank, smoke=False, confirm=False):
    # Arm pairing is deliberate; eight disjoint consecutive attempt seeds/unit.
    cells = (
        bank["split"]["development"][:2]
        if smoke
        else bank["split"]["protected" if confirm else "development"]
    )
    builds, repeats, start = (
        ((2, 1, 20480000) if smoke else (24, 4, 20461000))
        if confirm
        else ((2, 1, 20460000) if smoke else (24, 2, 20450000))
    )
    stride = 4 if confirm else 2
    return [
        dict(
            cell=c,
            build=b,
            repeat=r,
            arm=a,
            seeds=[start + ((ci * 24 + b) * stride + r) * 8 + k for k in range(8)],
        )
        for ci, c in enumerate(cells)
        for b in range(builds)
        for r in range(repeats)
        for a in ARMS
    ]


def seed_audit(bank, old_schedule, old_audit, confirm=False):
    historic = set(range(20440000, 20443028))

    def collect(value, key=""):
        if isinstance(value, dict):
            for k, v in value.items():
                collect(v, k if "seed" in k else key)
        elif isinstance(value, list):
            for v in value:
                collect(v, key)
        elif isinstance(value, int) and "seed" in key:
            historic.add(value)

    collect(old_schedule)
    collect(old_audit)
    collect(
        json.loads(gzip.decompress((prior.DATA / "presearch.json.gz").read_bytes()))
    )
    historic |= (
        set(range(19380000, 19384718))
        | set(range(19480000, 19484718))
        | set(range(19390000, 19393028))
    )
    if confirm:
        for smoke in (False, True):
            for m in schedules(bank, smoke):
                historic.update(m["seeds"])
    published, used = {}, set()
    for smoke in (False, True):
        uses = {}
        for m in schedules(bank, smoke, confirm):
            for k, value in enumerate(m["seeds"]):
                uses.setdefault(value, []).append((m, k))
        for records in uses.values():
            if (
                len(records) != 3
                or {m["arm"] for m, _ in records} != set(ARMS)
                or len({(m["cell"], m["build"], m["repeat"], k) for m, k in records})
                != 1
            ):
                raise ValueError("unintended seed reuse")
        values = set(uses)
        if values & (historic | used):
            raise ValueError("historical/smoke seed collision")
        used.update(values)
        published[
            "smoke" if smoke else "confirmation" if confirm else "development"
        ] = sorted(values)
    return dict(
        admitted=True,
        historical_count=len(historic),
        historical_hash=digest(sorted(historic)),
        stage0_range=[20440000, 20443027],
        published_seed_sets=published,
    )


def freeze(bank, libs, identities, confirm=False):
    supplied = [
        list(gates.helper(k, a, b).prefix)
        for k in ("p", "n")
        for a, b in itertools.permutations(range(4), 2)
    ]
    for lib in libs:
        verify_entries(lib["semantic"], bank["inputs"])
    verify_entries(
        [
            dict(prefix=p, nodes=len(p), compiled_length=len(Tree(tuple(p)).program))
            for p in supplied
        ],
        bank["inputs"],
    )
    frozen = dict(
        task=TASK,
        bank_hash=BANK_HASH,
        methods=method_hashes(),
        executable=gates.executable_check(),
        grammar=base.GRAMMAR,
        cutoff=65536,
        attempts=8,
        population=256,
        crossover=0.5,
        library_probability=0.5,
        builds=24,
        repeats=2,
        arms=list(ARMS),
        gates=supplied,
        archive_sha256=ARCHIVE_SHA,
        acquisition_identities=identities,
        donors="uniform unchanged expanded entries; half library mutation draws, original fallback",
        protected_count=len(bank["split"]["protected"]),
        protected_searches=0,
        frozen_before_search=True,
        inference="descriptive only; no efficacy verdict",
        bootstrap=dict(
            seed=BOOTSTRAP_SEED,
            draws=DRAWS,
            unit="paired whole builds and cells, repeats retained",
        ),
        forecast=dict(
            repeats=[1, 2, 4],
            effects=[0.60, 0.75, 0.80, 0.85, 1.00],
            sensitivity_variance_multiplier=2,
            runtime_tail_multiplier=2,
        ),
    )
    if confirm:
        raw = (DATA / "method_2044.json.gz").read_bytes()
        if hashlib.sha256(raw).hexdigest() != REVIEWED_SHA:
            raise ValueError("2044 reviewed freeze hash mismatch")
        reviewed = json.loads(gzip.decompress(raw))
        # The driver gains an opt-in phase; every other reviewed module and
        # production source/binary must be unchanged from 8a621df.
        for path, expected in reviewed["methods"].items():
            if (
                path != "experiments/chem_tape/signed_chain_run.py"
                and frozen["methods"].get(path) != expected
            ):
                raise ValueError("2044 reviewed method changed: " + path)
        for key in (
            "task",
            "bank_hash",
            "grammar",
            "cutoff",
            "attempts",
            "population",
            "crossover",
            "library_probability",
            "builds",
            "repeats",
            "arms",
            "gates",
            "archive_sha256",
            "acquisition_identities",
            "donors",
        ):
            if digest(frozen[key]) != digest(reviewed[key]):
                raise ValueError("2044 reviewed parameter drift: " + key)
        if len(bank["split"]["protected"]) != 18:
            raise ValueError("confirmation requires all eighteen frozen cells")
        frozen.update(
            task=CONFIRM_TASK,
            repeats=4,
            reviewed_freeze_sha256=REVIEWED_SHA,
            bootstrap=dict(
                seed=CONFIRM_BOOTSTRAP_SEED,
                draws=DRAWS,
                unit="paired whole builds and cells, four repeats retained",
            ),
            inference=dict(
                primary="R-all/R-tree pooled capped mean evaluations",
                saving="upper95 < 1.00",
                harm="lower95 > 1.00",
                otherwise="unresolved",
                secondary_bar=0.80,
            ),
            validity=dict(
                R_tree_first_attempt_max=0.85,
                R_tree_cap_max=0.25,
                R_gate_solve_min=0.95,
                failing_flags="report capped costs; qualify interpretation",
            ),
            economics_horizons=[10, 100],
            scope="Protected-cell reuse within the development chain bank",
            authorized_protected_searches=5184,
        )
        frozen.pop("forecast")
    return frozen


def admission_identity(bank):
    """Compare identical admission evidence across relocated git worktrees."""
    marker = "/experiments/chem_tape/data/"

    def relative(path):
        if path.count(marker) != 1:
            raise ValueError("invalid historical bank reference")
        return "experiments/chem_tape/data/" + path.split(marker, 1)[1]

    hashes = {relative(k): v for k, v in bank["old_bank_hashes"].items()}
    if len(hashes) != len(bank["old_bank_hashes"]):
        raise ValueError("ambiguous historical bank references")
    return dict(
        split=bank["split"],
        cells=[
            c | dict(old_bank=relative(c["old_bank"])) for c in bank["screen"]["cells"]
        ],
        old_bank_hashes=hashes,
        pairwise=bank["pairwise"],
    )


def prepare(args, out, deadline):
    start = time.monotonic()
    bank = load_bank()
    # Reproduce all performance-blind admission checks; timing is not hashed.
    rebuilt = bank_module.build(deadline)
    if not rebuilt["admitted"] or admission_identity(rebuilt) != admission_identity(
        bank
    ):
        raise ValueError("chain admission replay mismatch")
    libs, identities, old_schedule, old_audit = saved_libraries()
    frozen = freeze(bank, libs, identities, args.confirm)
    audit = seed_audit(bank, old_schedule, old_audit, args.confirm)
    full, smoke = (
        schedules(bank, confirm=args.confirm),
        schedules(bank, True, args.confirm),
    )
    payloads = [
        ("bank", bank),
        ("method_freeze", frozen),
        ("libraries", libs),
        ("schedules", full),
        ("smoke_schedule", smoke),
        ("seed_audit", audit),
    ]
    p = dict(
        admitted=True,
        protected_searches=0,
        admission_replay_identity_hash=digest(admission_identity(rebuilt)),
        seconds=time.monotonic() - start,
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"])
        .decode()
        .strip(),
    )
    for name, data in payloads:
        write_json(out, name + ".json", data)
        p[name + "_hash"] = digest(data)
    p["preparation_hash"] = digest(p)
    write_json(out, "preparation.json", p)
    print("prepared", p, flush=True)


def load_prepared(path, confirm=False):
    if (path / "failure.json").exists():
        raise ValueError("preparation has recorded failure")

    def read(n):
        return json.loads((path / (n + ".json")).read_text())

    bank, frozen, libs, full, smoke, audit, p = [
        read(n)
        for n in (
            "bank",
            "method_freeze",
            "libraries",
            "schedules",
            "smoke_schedule",
            "seed_audit",
            "preparation",
        )
    ]
    original, identities, old_schedule, old_audit = saved_libraries()
    if (
        not p["admitted"]
        or digest(bank) != digest(load_bank())
        or libs != original
        or digest(frozen) != digest(freeze(bank, libs, identities, confirm))
        or full != schedules(bank, confirm=confirm)
        or smoke != schedules(bank, True, confirm)
        or audit != seed_audit(bank, old_schedule, old_audit, confirm)
        or p["preparation_hash"]
        != digest({k: v for k, v in p.items() if k != "preparation_hash"})
        or any(
            p[k + "_hash"] != digest(v)
            for k, v in [
                ("bank", bank),
                ("method_freeze", frozen),
                ("libraries", libs),
                ("schedules", full),
                ("smoke_schedule", smoke),
                ("seed_audit", audit),
            ]
        )
    ):
        raise ValueError("chain preparation provenance mismatch")
    return bank, frozen, libs, p


def envelopes(metas, bank, libs, frozen, smoke=False, confirm=False):
    expected = {json.dumps(m, sort_keys=True) for m in schedules(bank, smoke, confirm)}
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    jobs = []
    for m in metas:
        if json.dumps(m, sort_keys=True) not in expected or (
            (smoke or not confirm) and m["cell"] in bank["split"]["protected"]
        ):
            raise ValueError("unapproved/protected search requested")
        donors = (
            None
            if m["arm"] == "R-tree"
            else frozen["gates"]
            if m["arm"] == "R-gate"
            else [e["prefix"] for e in libs[m["build"]]["semantic"]]
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


def stats(rows):
    def distribution(values):
        return dict(
            mean=float(np.mean(values)),
            median=float(np.median(values)),
            p95=float(np.quantile(values, 0.95)),
            max=float(np.max(values)),
        )

    counts = {str(n): sum(len(r["attempts"]) == n for r in rows) for n in range(1, 9)}
    operator = {}
    for r in rows:
        for attempt in r["attempts"]:
            for k, v in attempt.get("operator", {}).items():
                operator[k] = operator.get(k, 0) + v
    return dict(
        jobs=len(rows),
        solves=sum(r["solved"] for r in rows),
        capped_jobs=sum(not r["solved"] for r in rows),
        first_attempt_rate=float(np.mean([r["attempts"][0]["solved"] for r in rows])),
        attempts_distribution=counts,
        evaluations=distribution([r["evaluations"] for r in rows]),
        worker_seconds=distribution([r["worker_seconds"] for r in rows]),
        operator=operator,
    )


def variance_components(z):
    """Balanced crossed random effects MOM for the paired mean-ratio influence."""
    b, c, r = z.shape
    if min(b, c, r) < 2:
        raise ValueError("forecast requires complete 24x6x2 development tensor")
    means = z.mean(2)
    grand = means.mean()
    bm, cm = means.mean(1), means.mean(0)
    interaction = means - bm[:, None] - cm[None, :] + grand
    mse = float(((z - means[:, :, None]) ** 2).sum() / (b * c * (r - 1)))
    msbc = float(r * (interaction**2).sum() / ((b - 1) * (c - 1)))
    msb = float(c * r * np.var(bm, ddof=1))
    msc = float(b * r * np.var(cm, ddof=1))
    return dict(
        build=max(0, (msb - msbc) / (c * r)),
        cell=max(0, (msc - msbc) / (b * r)),
        build_cell=max(0, (msbc - mse) / r),
        search=mse,
        mean_squares=dict(build=msb, cell=msc, build_cell=msbc, search=mse),
    )


def forecast(arrays, bank, throughput, frozen):
    all_cost, tree_cost = (
        arrays["evaluations"]["R-all"],
        arrays["evaluations"]["R-tree"],
    )
    z = all_cost / all_cost.mean() - tree_cost / tree_cost.mean()
    components = variance_components(z)
    count, builds = len(bank["split"]["protected"]), 24
    effective = throughput["effective_concurrency"]
    mean_seconds = sum(a.mean() for a in arrays["worker_seconds"].values()) / 3
    rng = np.random.default_rng(BOOTSTRAP_SEED + 1)
    normals = rng.normal(size=(DRAWS, 4))
    prices = []
    for repeats in frozen["forecast"]["repeats"]:
        terms = np.asarray(
            [
                components["build"] / builds,
                components["cell"] / count,
                components["build_cell"] / (builds * count),
                components["search"] / (builds * count * repeats),
            ]
        )
        jobs = builds * count * repeats * 3
        central_seconds = jobs * mean_seconds / effective
        # 15-min verification reserve + rounded score time including 2x tails,
        # replay/reporting (120s) and 25% scheduling margin. This is a price,
        # not a runnable/authorized confirmation queue.
        scoring_timeout = int(60 * np.ceil((2 * central_seconds * 1.25 + 120) / 60))
        scenarios = []
        for multiplier in (1, frozen["forecast"]["sensitivity_variance_multiplier"]):
            errors = normals @ np.sqrt(terms * multiplier)
            lo, hi = np.quantile(np.exp(errors), [0.025, 0.975])
            intervals = []
            for effect in frozen["forecast"]["effects"]:
                low, high = float(effect * lo), float(effect * hi)
                decision = (
                    "saving"
                    if high < 0.80
                    else "saving_excluded"
                    if low >= 0.80
                    else "unresolved"
                )
                intervals.append(
                    dict(
                        hypothetical_effect=effect,
                        expected_interval95=[low, high],
                        hypothetical_decision=decision,
                    )
                )
            scenarios.append(
                dict(
                    variance_multiplier=multiplier,
                    expected_upper_lower=float(hi / lo),
                    precision_at_most_1_6=bool(hi / lo <= 1.6),
                    effect_scenarios=intervals,
                )
            )
        prices.append(
            dict(
                repeats=repeats,
                cells=count,
                builds=builds,
                jobs=jobs,
                central_wall_seconds=float(central_seconds),
                tail_2x_seconds=float(2 * central_seconds),
                prepare_timeout_seconds=900,
                scoring_timeout_seconds=scoring_timeout,
                summed_timeout_seconds=900 + scoring_timeout,
                affordable=900 + scoring_timeout <= 14400,
                scenarios=scenarios,
            )
        )
    return dict(
        protected_cells=count,
        components=components,
        prices=prices,
        model="Paired delta-method influence of pooled capped arithmetic means; normal random build/cell/interaction/search effects simulate log-ratio sampling error. MOM negative components truncated to zero.",
        assumptions="Conditional on admitted protected cells exchangeable with six development cells, constant effect/relative variation, measured throughput; not observed protected precision. All four variances doubled in sensitivity; small development roster may underestimate heterogeneity.",
        decisiveness="Width <=1.6 does not decide an effect near .80. Hypothetical effect .80 is unresolved. No automatic confirmation authorization.",
    )


def classify_confirmation(interval, threshold=1.0):
    low, high = interval
    return "saving" if high < threshold else "harm" if low > threshold else "unresolved"


def validity_checks(arms):
    tree, gate = arms["R-tree"], arms["R-gate"]
    hard = tree["first_attempt_rate"] <= 0.85
    cap_rate = tree["capped_jobs"] / tree["jobs"]
    solve_rate = gate["solves"] / gate["jobs"]
    return dict(
        R_tree_first_attempt_rate=tree["first_attempt_rate"],
        hard_tier_supported=hard,
        R_tree_cap_rate=cap_rate,
        cap_dominated=cap_rate > 0.25,
        R_gate_solve_rate=solve_rate,
        supplied_repertoire_reliable=solve_rate >= 0.95,
        intended_interpretation_supported=hard
        and cap_rate <= 0.25
        and solve_rate >= 0.95,
        interpretation="Report capped costs regardless; withhold hard-tier interpretation if first-attempt >85%, label cap-dominated if caps >25%, withhold reliable-supplied-reference interpretation if R-gate solves <95%. Return to strategy; no top-up.",
    )


def summarize(rows, libs, bank, frozen, elapsed, workers, smoke=False, confirm=False):
    rows = prior.validate_rows(rows, schedules(bank, smoke, confirm), bank)
    cells = (
        bank["split"]["development"][:2]
        if smoke
        else bank["split"]["protected" if confirm else "development"]
    )
    builds, repeats = (2, 1) if smoke else (24, 4 if confirm else 2)
    by = {(r["build"], r["cell"], r["repeat"], r["arm"]): r for r in rows}
    arrays = {
        metric: {
            a: np.asarray(
                [
                    [[by[b, c, r, a][metric] for r in range(repeats)] for c in cells]
                    for b in range(builds)
                ],
                dtype=float,
            )
            for a in ARMS
        }
        for metric in ("evaluations", "worker_seconds", "solved")
    }
    rng = np.random.default_rng(CONFIRM_BOOTSTRAP_SEED if confirm else BOOTSTRAP_SEED)
    bi, ci = (
        rng.integers(builds, size=(DRAWS, builds)),
        rng.integers(len(cells), size=(DRAWS, len(cells))),
    )
    boot = {
        m: {a: prior.bootstrap_mean(v, bi, ci) for a, v in aa.items()}
        for m, aa in arrays.items()
    }
    contrasts = {
        a + "/R-tree": {
            m: prior.estimate(
                arrays[m][a].mean() / arrays[m]["R-tree"].mean(),
                boot[m][a] / boot[m]["R-tree"],
            )
            for m in ("evaluations", "worker_seconds")
        }
        for a in ("R-all", "R-gate")
    }
    if confirm:
        for numerator, denominator in (("R-gate", "R-all"), ("R-all", "R-gate")):
            contrasts[numerator + "/" + denominator] = {
                m: prior.estimate(
                    arrays[m][numerator].mean() / arrays[m][denominator].mean(),
                    boot[m][numerator] / boot[m][denominator],
                )
                for m in ("evaluations", "worker_seconds")
            }
    coverage = []
    for b, lib in enumerate(libs):
        included = {
            h for h, d in lib["helper_diagnostics"].items() if d["semantic"]["included"]
        }
        for cell in bank["screen"]["cells"]:
            if cell["retained"]:
                present = sorted(included & set(cell["helpers"]))
                coverage.append(
                    dict(
                        build=b,
                        cell=cell["id"],
                        needed=cell["helpers"],
                        present=present,
                        needed_helpers_present=len(present),
                    )
                )
    coverage_by = {
        (c["build"], c["cell"]): c["needed_helpers_present"] for c in coverage
    }
    strata = []
    for n in range(4):
        rr = [
            r
            for r in rows
            if r["arm"] == "R-all" and coverage_by[r["build"], r["cell"]] == n
        ]
        strata.append(dict(needed_helpers_present=n, stats=stats(rr) if rr else None))
    throughput = dict(
        wall_seconds=elapsed,
        workers=workers,
        worker_seconds=sum(r["worker_seconds"] for r in rows),
        effective_concurrency=sum(r["worker_seconds"] for r in rows) / elapsed,
        jobs_per_second=len(rows) / elapsed,
        max_worker_seconds=max(r["worker_seconds"] for r in rows),
    )
    economics = {}
    for metric, field in [
        ("evaluations", "acquisition_evaluations"),
        ("worker_seconds", "acquisition_worker_seconds"),
    ]:
        acquisition = np.asarray(
            [
                lib[field]
                + (
                    sum(lib[k] for k in prior.TIMINGS)
                    if metric == "worker_seconds"
                    else 0
                )
                for lib in libs[:builds]
            ]
        )
        acq_boot = acquisition[bi].mean(1)
        all_mean, tree_mean = (
            arrays[metric]["R-all"].mean(),
            arrays[metric]["R-tree"].mean(),
        )
        saving = float(tree_mean - all_mean)
        economics[metric] = dict(
            historical_acquisition=prior.estimate(acquisition.mean(), acq_boot),
            saving_per_search=prior.estimate(
                saving, boot[metric]["R-tree"] - boot[metric]["R-all"]
            ),
            repayment_searches=None
            if saving <= 0
            else float(acquisition.mean() / saving),
            cost_curves=[
                dict(
                    searches=n,
                    R_tree=float(n * tree_mean),
                    R_all_owned=float(n * all_mean),
                    R_all_newly_deployed=float(acquisition.mean() + n * all_mean),
                    newly_deployed_difference=prior.estimate(
                        acquisition.mean() - n * saving,
                        acq_boot + n * (boot[metric]["R-all"] - boot[metric]["R-tree"]),
                    ),
                )
                for n in (0, 1, 10, 100, 1000)
            ],
        )
        if confirm:
            saving_boot = boot[metric]["R-tree"] - boot[metric]["R-all"]
            lo, hi = np.quantile(saving_boot / acq_boot, [0.025, 0.975])
            unbounded = (
                lo <= 0 or economics[metric]["saving_per_search"]["interval95"][0] <= 0
            )
            economics[metric].update(
                symbols="A = acquisition; C = capped per-search cost; Delta = C_tree - C_all; total = A + N*C_all; repayment = A/Delta for positive Delta",
                repayment_interval95=[
                    None if hi <= 0 else float(1 / hi),
                    None if unbounded else float(1 / lo),
                ],
                repayment_unbounded=bool(unbounded),
                nonpositive_saving_bootstrap_fraction=float(np.mean(saving_boot <= 0)),
                interval_method="Paired build/cell bootstrap of saving/acquisition, inverted; null bounds encode infinity/no finite repayment. Upper is unbounded if saving interval includes zero.",
            )
            for curve in economics[metric]["cost_curves"]:
                curve["acquisition_plus_search_label"] = (
                    "lower_total_cost"
                    if curve["newly_deployed_difference"]["interval95"][1] < 0
                    else "higher_total_cost"
                    if curve["newly_deployed_difference"]["interval95"][0] > 0
                    else "unresolved"
                )
    result = dict(
        complete=True,
        smoke=smoke,
        protected_searches=0,
        decision="descriptive_no_efficacy_verdict",
        arms={a: stats([r for r in rows if r["arm"] == a]) for a in ARMS},
        contrasts=contrasts,
        per_cell=[
            dict(
                arm=a,
                cell=c,
                stats=stats([r for r in rows if r["arm"] == a and r["cell"] == c]),
            )
            for a in ARMS
            for c in cells
        ],
        per_build=[
            dict(
                arm=a,
                build=b,
                stats=stats([r for r in rows if r["arm"] == a and r["build"] == b]),
            )
            for a in ARMS
            for b in range(builds)
        ],
        coverage=coverage,
        R_all_coverage_strata=strata,
        throughput=throughput,
        economics=economics,
        economics_scope="Historical acquisition/extraction/validation worker seconds from 1938; current deployment worker seconds. Hardware/load differences limit comparability. Shared admission/replay overhead separate; supplied family prior has no evolutionary acquisition.",
        scope="One combined linked-role/depth shape change; no protected effect, helper causality, inherited learning or unrestricted time-to-solution claim.",
    )
    if confirm:
        result.update(
            protected_searches=0 if smoke else len(rows),
            task=CONFIRM_TASK,
            primary="R-all/R-tree pooled capped arithmetic mean evaluations",
            scope="Protected-cell reuse within the development chain bank; combined depth/input-sharing change, no fresh-bank transfer, helper causality, inherited learning or uncapped time-to-solution claim.",
        )
        if not smoke:
            primary = contrasts["R-all/R-tree"]["evaluations"]
            bar = classify_confirmation(primary["interval95"], 0.80)
            result.update(
                validity_checks=validity_checks(result["arms"]),
                decision=classify_confirmation(primary["interval95"]),
                secondary_20_percent_label={
                    "saving": ">20% saving",
                    "harm": "20% saving excluded",
                    "unresolved": "unresolved",
                }[bar],
                next_action="Return to strategy; unresolved closes this confirmation without automatic top-up. Acquisition repayment requires the measured horizon comparisons, separate from deployment saving.",
            )
    elif not smoke:
        result["confirmation_forecast"] = forecast(arrays, bank, throughput, frozen)
        hard = result["arms"]["R-tree"]["first_attempt_rate"] <= 0.85
        ceiling = (
            result["arms"]["R-gate"]["solves"] / 288 >= 0.95
            and result["arms"]["R-tree"]["capped_jobs"] / 288 <= 0.25
        )
        priced = any(
            p["affordable"] and p["scenarios"][0]["precision_at_most_1_6"]
            for p in result["confirmation_forecast"]["prices"]
        )
        result["strategy_recommendation"] = dict(
            hard=hard,
            not_ceilinged=ceiling,
            precise_and_affordable=priced,
            consider_separately_approved_confirmation=bool(hard and ceiling and priced),
            authorization="Return to strategy only; precision forecast is not evidence of a saving or permission to run.",
        )
    return result


def plots(out, rows, libs):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 4, figsize=(17, 4))
    xs = [256, 4096, 16384, 65536, 131072, 262144, 524288]
    for arm in ARMS:
        rr = [r for r in rows if r["arm"] == arm]
        axes[0].plot(
            xs,
            [np.mean([r["solved"] and r["evaluations"] <= x for r in rr]) for x in xs],
            label=arm,
        )
        for panel, field in [(1, "curve"), (2, "phenotype_diversity_curve")]:
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
                label=arm,
            )
    for ax, title in zip(
        axes[:3],
        [
            "Exact D625 solves",
            "Training best; restart resets",
            "Training output diversity",
        ],
    ):
        ax.set(xscale="log", xlabel="Evaluations", title=title)
        ax.legend(fontsize=7)
    axes[3].plot([len(lib["semantic"]) for lib in libs])
    axes[3].set(xlabel="Saved build", ylabel="R-all entries")
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=140)
    plt.close(fig)


def score(args, out, deadline):
    start = time.monotonic()
    confirm = args.phase == "confirm"
    bank, frozen, libs, p = load_prepared(Path(args.prepared), confirm)
    replay = time.monotonic() - start
    metas = schedules(bank, args.smoke, confirm)
    for name, value in [
        ("bank", bank),
        ("method_freeze", frozen),
        ("schedules", metas),
    ]:
        write_json(out, name + ".json", value)
    rows, elapsed = base.run_batch(
        out,
        "score.jsonl",
        envelopes(metas, bank, libs, frozen, args.smoke, confirm),
        args.workers,
        deadline,
    )
    report = summarize(
        rows, libs, bank, frozen, elapsed, args.workers, args.smoke, confirm
    )
    if confirm and not args.smoke:
        write_json(out, "validity_checks.json", report["validity_checks"])
    plots(out, rows, libs)
    report.update(
        preparation_hash=p["preparation_hash"],
        score_rows_hash=digest(prior.validate_rows(rows, metas, bank)),
        replay_validation_seconds=replay,
        seconds=time.monotonic() - start,
    )
    write_json(out, "report.json", report)
    print("scored", len(rows), "wall", elapsed, "arms", report["arms"], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "development", "confirm"))
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="prepare the authorized 2150 confirmation freeze",
    )
    parser.add_argument("--prepared")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seconds", type=int)
    args = parser.parse_args()
    limit = (
        870 if args.phase == "prepare" else 11490 if args.phase == "confirm" else 2370
    )
    seconds = args.seconds or limit
    if (
        args.workers < 1
        or seconds <= 0
        or seconds > limit
        or (args.phase != "prepare" and not args.prepared)
        or os.environ.get("RAYON_NUM_THREADS") != "1"
        or (args.phase == "prepare" and args.smoke)
        or (args.phase != "prepare" and args.confirm)
    ):
        parser.error(
            "positive workers, fixed phase limits, RAYON_NUM_THREADS=1 and --prepared for score required; preparation always freezes full grids"
        )
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    if any(
        (out / n).exists()
        for n in ("failure.json", "preparation.json", "report.json", "score.jsonl")
    ):
        parser.error("RUN_DIR contains previous experiment artifacts")
    deadline = time.monotonic() + seconds
    try:
        (prepare if args.phase == "prepare" else score)(args, out, deadline)
        if time.monotonic() > deadline:
            raise TimeoutError(
                "fixed phase deadline exceeded during verification/report"
            )
    except Exception as error:
        write_json(
            out,
            "failure.json",
            dict(admitted=False, phase=args.phase, smoke=args.smoke, error=str(error)),
        )
        raise


if __name__ == "__main__":
    main()
