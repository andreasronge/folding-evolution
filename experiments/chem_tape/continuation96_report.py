"""1137 fixed gate, historical scientific fingerprints, and paired inference."""

import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from experiments.chem_tape.crossed_learning_report import interval
from experiments.chem_tape.crossed_learning_run import TRAINING
from experiments.chem_tape.map_learning import log_cost
from experiments.chem_tape.rank_one_report import balanced

REFERENCE = Path(__file__).with_name("data") / "continuation_0821.json.gz"
REFERENCE_SHA = "2c8411952488c35c6b82f633896cabfab58e216c8157287f34cb8c63edf0557f"
ROSTER = [f"{f}{k}" for k in range(1, 9) for f in ("BE", "PA")]
F1_SEEDS = list(range(1_824_000_000, 1_824_000_050))


def load_reference():
    raw = REFERENCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA:
        raise ValueError("0821 reference SHA mismatch")
    ref = json.loads(gzip.decompress(raw))
    c = ref["config"]
    if (
        c["task"] != "2026-10-07-0821"
        or c["smoke_only"]
        or c["probe_only"]
        or c["fresh_seeds"] != F1_SEEDS
        or c["scoring_effort"] != 24
        or c["searches_per_trajectory"] != 4040
        or c["training"] != TRAINING
    ):
        raise ValueError("invalid historical configuration")
    expected = {
        (tid, a, cell, seed)
        for tid in ROSTER
        for a in ("S", "T24")
        for cell in TRAINING[tid[:2]]
        for seed in F1_SEEDS
    }
    keys = [(r["start"], r["arm"], r["cell"], r["seed"]) for r in ref["records"]]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("invalid historical row roster")
    return ref


def fingerprint(row, fields):
    # Field inclusion is pinned to the prior schema; timing and arm labels excluded.
    payload = {k: row[k] for k in fields}
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def baseline_check(rows, reference, starts, seeds):
    expected = {
        (tid + ":S", c, s) for tid in starts for c in TRAINING[tid[:2]] for s in seeds
    }
    prior = {
        (r["start"] + ":S", r["cell"], r["seed"]): r
        for r in reference["records"]
        if r["arm"] == "S"
    }
    seen, mismatches = set(), []
    for r in rows:
        if not r["arm"].endswith(":S"):
            continue
        key = r["arm"], r["cell"], r["seed"]
        if key in seen or key not in expected or key not in prior:
            mismatches.append(list(key))
        elif (
            fingerprint(r, reference["scientific_fields"])
            != prior[key]["scientific_sha256"]
        ):
            mismatches.append(list(key))
        seen.add(key)
    return dict(
        passed=seen == expected and not mismatches,
        expected_rows=len(expected),
        observed_rows=len(seen),
        mismatches=mismatches,
        fields=reference["scientific_fields"],
        timing_excluded=True,
    )


def validate_rows(rows, maps, seeds, cap, phase):
    expected = {
        (name, c, s)
        for name in maps
        for c in (sum(TRAINING.values(), []) if name == "G4" else TRAINING[name[:2]])
        for s in seeds
    }
    seen, cases, errors = set(), {}, []
    for r in rows:
        key = r["arm"], r["cell"], r["seed"]
        if key in seen or key not in expected:
            errors.append("duplicate/unexpected row")
        seen.add(key)
        if (
            r["cap"] != cap
            or r["pop_size"] != 256
            or r["phase"] != phase
            or r["table_hash"] != maps.get(r["arm"], {}).get("table_hash")
        ):
            errors.append("cap/population/phase/map mismatch")
        if r["seed"] in cases and cases[r["seed"]] != r["training_indices"]:
            errors.append("unpaired shared-seed training cases")
        cases[r["seed"]] = r["training_indices"]
    if seen != expected:
        errors.append("missing/unexpected rows")
    return dict(
        passed=not errors,
        errors=sorted(set(errors)),
        expected_rows=len(expected),
        observed_rows=len(rows),
    )


def contrasts(rows, starts, seeds, cap, comparisons):
    lookup = {(r["arm"], r["cell"], r["seed"]): r for r in rows}
    estimates, effects = {}, {}
    for label, (num, den) in comparisons.items():
        values = {f: [] for f in TRAINING}
        effects[label] = {}
        for tid in starts:
            value = float(
                np.mean(
                    [
                        log_cost(lookup[tid + ":" + num, c, s], cap)
                        - log_cost(lookup[tid + ":" + den, c, s], cap)
                        for c in TRAINING[tid[:2]]
                        for s in seeds
                    ]
                )
            )
            values[tid[:2]].append(value)
            effects[label][tid] = value
        estimates[label] = dict(
            pooled=balanced(values),
            families={f: interval(v) if v else None for f, v in values.items()},
        )
    return estimates, effects


def gate(estimate, valid=True):
    return bool(valid and estimate["ratio"] is not None and estimate["ratio"] >= 1.10)


def outcome(f1, f2, primary, context, residual, valid, token_counts, context_counts):
    def result(row, meaning, **kw):
        return dict(row=row, meaning=meaning, next="strategy", **kw)

    if not valid or min(token_counts.values()) < 6:
        return result(
            "U",
            "Infrastructure failure or fewer than six complete T starts per family.",
        )
    if not gate(f1):
        if f1["interval_95"][1] < 1.10:
            return result(
                "1",
                "This fixed procedure's mean token gain is bounded below 1.10x on these saved starts; plateau versus depth remains unresolved.",
            )
        return result(
            "2",
            "Token progress unresolved; report the interval without automatic follow-up.",
        )
    if min(context_counts.values()) < 6:
        return result(
            "3",
            "Token gate passed; context comparison unresolved because fewer than six C starts per family fit.",
        )
    lo, hi = primary["interval_95"]
    if lo > 1:
        return result(
            "4",
            "C outperforms T on training cells in this procedure.",
            beneficial_adaptation_above_S=context["interval_95"][0] > 1,
            residual_removal_resolved=residual["interval_95"][0] > 1,
            qualification="Residual removal also changes token marginals; transfer untested.",
        )
    if f2["interval_95"][0] <= 1:
        return result(
            "5",
            "Token progress lacks fresh-search confirmation; C/T still constrains relative context performance.",
        )
    if hi < 1.15:
        return result(
            "6",
            "Mean context increment bounded below 1.15x with confirmed token gain in this procedure; joint learning from G4 untested.",
        )
    return result("7", "Unresolved context increment with a confirmed token control.")


def selected_diagnostic(previous, current_scores):
    """Only actual source parents retained with their accepted children qualify."""
    chosen = previous["selected_indices"]
    changes, curse = [], []
    missing, accepted = 0, 0
    for slot, idx in enumerate(chosen):
        if idx < 2:
            continue
        accepted += 1
        parent = previous["mutations"][idx - 2]["parent"]
        child_id = previous["candidates"][idx]["id"]
        parent_id = previous["candidates"][parent]["id"]
        curse.append(
            dict(
                child_id=child_id,
                acceptance_minus_rescore=previous["scores"][idx] - current_scores[slot],
            )
        )
        if parent not in chosen:
            missing += 1
            continue
        parent_slot = chosen.index(parent)
        changes.append(
            dict(
                child_id=child_id,
                source_parent_id=parent_id,
                child_minus_parent=current_scores[slot] - current_scores[parent_slot],
            )
        )
    return dict(
        accepted_children=accepted,
        missing_source_parent=missing,
        covered_pairs=len(changes),
        selected_changes=changes,
        winners_curse=curse,
        scope="selected subset: child and its actual source parent both survived",
    )
