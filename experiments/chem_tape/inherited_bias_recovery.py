"""Operational recovery of 0918; never changes acquisition/scoring seed streams."""
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

import numpy as np

from experiments.chem_tape import inherited_bias as ib

SOURCE_COMMIT = "511711c35cfaada094184ea6c4fa616503b01ee4"
CUT = ("max", "inherited", 14)
REPLAYS = (("sum", "inherited", 0), ("max", "broken", 0))
SELECTIVE_SECONDS = 3600
FALLBACK_SECONDS = 5400
RECOVERY_SECONDS = SELECTIVE_SECONDS + FALLBACK_SECONDS
TIMING_SECONDS = 900


def key(row):
    return row["family"], row["arm"], row["replicate"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_rows(root):
    """Require the approved manifest and source code, not just plausibly shaped rows."""
    prior = json.loads((root / "manifest.json").read_text())
    expected = json.loads(json.dumps(ib.manifest()))
    if prior["git_commit"] != SOURCE_COMMIT or prior["git_dirty"]:
        raise RuntimeError("source must be the clean approved 0918 commit")
    if any(prior[k] != value for k, value in expected.items()):
        raise RuntimeError("source scientific manifest mismatch")
    for filename, sha in prior["source_sha256"].items():
        marker = "/experiments/" if "/experiments/" in filename else "/src/"
        relative = marker[1:] + filename.split(marker, 1)[1]
        content = subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{relative}"])
        if hashlib.sha256(content).hexdigest() != sha:
            raise RuntimeError("source code hash mismatch")
        # Only inherited_bias.py changes operationally in this recovery.
        if relative != "experiments/chem_tape/inherited_bias.py" and digest(relative) != sha:
            raise RuntimeError("scientific implementation differs from 0918")
    paths = sorted((root / "acquisition" / "main").glob("*/*/*.json"))
    rows = [json.loads(p.read_text()) for p in paths]
    expected_keys = {(f, a, i) for f in ib.FAMILIES for a in ib.ARMS for i in range(ib.ACQUISITIONS)}
    if len(rows) != 80 or {key(r) for r in rows} != expected_keys:
        raise RuntimeError("original roster missing or duplicate")
    if {key(r) for r in rows if not r["complete"]} != {CUT}:
        raise RuntimeError("original incomplete roster differs from approved recovery")
    for row in rows:
        f, a, i = key(row)
        name = f"main/{f}/{i}"
        program_seed = int(ib.seed("program/" + name).generate_state(1)[0])
        cfg = replace(ib.eb.config(f + "1", a, program_seed, ib.POP, ib.CAP,
                      [1 / 22] * 22, master=ib.MASTER), generations=ib.GENERATIONS)
        if (row["master"] != ib.MASTER or row["phase"] != "main" or
                row["program_seed"] != cfg.seed or row["config"] != asdict(cfg) or
                row["modifier_stream"] != "modifier/" + name + "/" + a):
            raise RuntimeError("original acquisition configuration mismatch")
    return rows, {key(r): p for r, p in zip(rows, paths)}


def episode_signature(episode):
    return {k: episode.get(k) for k in (
        "episode", "target", "training_seed", "training_indices", "solved", "first_gen",
        "evaluations_to_exact", "position", "solver", "generations", "censuses",
        "evaluations", "shuffles", "verifications", "shortcuts")}


def replay_checks(old, replayed):
    checks = []
    for new in replayed:
        original = old[key(new)]
        completed = len(original["trajectories"])
        if key(new) == CUT and completed != 30:
            raise RuntimeError("cut source must have exactly 30 completed episodes")
        ep_match = (len(new["episodes"]) >= completed and all(
            episode_signature(a) == episode_signature(b)
            for a, b in zip(original["episodes"][:completed], new["episodes"][:completed])))
        vector_match = (key(new) == CUT or all(
            np.array_equal(original[k], new[k]) for k in ("probs", "theta")))
        checks.append(dict(family=new["family"], arm=new["arm"], replicate=new["replicate"],
            completed_source_episodes=completed, episodes_match=ep_match,
            vectors_match=vector_match, complete=new["complete"],
            passed=new["complete"] and ep_match and vector_match))
    return checks


def recovery_estimate(rows):
    """Conservative extrapolation, explicitly not a measured complete replay."""
    cut = next(r for r in rows if key(r) == CUT)
    cut_estimate = cut["seconds"] * ib.EPISODES / len(cut["trajectories"])
    times = [cut_estimate if key(r) == CUT else r["seconds"] for r in rows]
    full = sum(times) / ib.WORKERS + (ib.WORKERS - 1) / ib.WORKERS * max(times)
    return dict(cut_extrapolated_seconds=cut_estimate, full_replay_expected_seconds=full,
                selective_expected_seconds=max(cut_estimate, *(r["seconds"] for r in rows
                                              if key(r) in REPLAYS)),
                basis="original worker times; cut duration extrapolated from 30/48 episodes; final-worker allowance")


def recover(out, source):
    start = time.monotonic()
    sentinel = out / "ACQUISITIONS_COMPLETE"
    sentinel.unlink(missing_ok=True)
    original, paths = source_rows(source)
    old = {key(r): r for r in original}
    ib.eb.write_json(out / "validation.json", ib.validate())
    jobs = [j for j in ib.acquisition_jobs(out / "selective", "main") if key(j) in (CUT, *REPLAYS)]
    for j in jobs:
        j["deadline"] = start + SELECTIVE_SECONDS
    replayed = ib.parallel(ib.acquire, jobs, 3)
    checks = replay_checks(old, replayed)
    fallback = not (len(checks) == 3 and all(c["passed"] for c in checks))
    estimate = recovery_estimate(original)
    provenance = dict(source_directory=str(source.resolve()), source_commit=SOURCE_COMMIT,
        source_manifest_sha256=digest(source / "manifest.json"), replay_checks=checks,
        cost_estimate=estimate,
        fallback=fallback, source_rows=[dict(family=r["family"], arm=r["arm"],
            replicate=r["replicate"], source_path=str(paths[key(r)].resolve()),
            sha256=digest(paths[key(r)]), reused=not fallback and key(r) != CUT) for r in original])
    # Save failed replay evidence before attempting fallback, including its complete budget.
    ib.eb.write_json(out / "recovery.json", provenance)
    if fallback:
        # Unspent selective allowance may fund fallback; the stage's 9000 s cap
        # never resets. A slow failed attempt can leave too little for full replay.
        deadline = start + RECOVERY_SECONDS
        if estimate["full_replay_expected_seconds"] > deadline - time.monotonic():
            raise RuntimeError("full replay exceeds remaining cumulative recovery budget; stop for replanning")
        jobs = ib.acquisition_jobs(out, "main", deadline=deadline)
        rows = ib.parallel(ib.acquire, jobs, ib.WORKERS)
    else:
        completed = next(r for r in replayed if key(r) == CUT)
        rows = [completed if key(r) == CUT else r for r in original]
        ib.check_acquisitions(rows)
        for r in rows:
            f, a, i = key(r)
            dest = out / "acquisition" / "main" / f / a / f"{i}.json"
            dest.parent.mkdir(parents=True, exist_ok=True)
            if key(r) == CUT:
                ib.eb.write_json(dest, r)
            else:
                shutil.copyfile(paths[key(r)], dest)
    ib.check_acquisitions(rows)
    provenance.update(seconds=time.monotonic() - start, complete=True,
        output_rows=[dict(family=r["family"], arm=r["arm"], replicate=r["replicate"],
            sha256=digest(out / "acquisition" / "main" / r["family"] / r["arm"] / f"{r['replicate']}.json"))
            for r in rows])
    ib.eb.write_json(out / "recovery.json", provenance)
    sentinel.write_text("ok\n")
    return provenance


def timing_jobs(out, rows):
    """Frozen 80 learned and 12 reference searches, strictly outside scoring indices."""
    by_key = {key(r): r for r in rows}
    spec = json.loads(ib.eb.SPEC_PATH.read_text())["vectors"]
    jobs = []
    for family in ib.FAMILIES:
        for arm in ib.ARMS:
            for rep in range(5):
                for th in ("1", "5"):
                    for index in (2000, 2001):
                        jobs.append(ib.frozen_job(family + th, f"{arm}/{rep}",
                                    by_key[(family, arm, rep)]["probs"], index, phase="recovery-timing"))
        for arm in ib.REFERENCES:
            vector = "hand_" + family if arm == "hand" else family if arm == "fit" else arm
            for th in ("1", "5"):
                jobs.append(ib.frozen_job(family + th, arm, spec[vector], 2002, phase="recovery-timing"))
    for j in jobs:
        j["out"] = str(out / "searches" / j["task"] / j["arm"] / f"{j['replicate']}.json")
    return jobs


def scoring_price(rows, workers):
    result = {}
    for family in ib.FAMILIES:
        work, cells = 0.0, []
        family_rows = [r for r in rows if r["task"].startswith(family)]
        for th in ("1", "5"):
            for arm in ib.ARMS + ib.REFERENCES:
                cell = [r for r in family_rows if r["task"] == family + th and r["arm"].split("/")[0] == arm]
                if len(cell) != (10 if arm in ib.ARMS else 1):
                    raise RuntimeError("timing roster missing or duplicate")
                mean = float(np.mean([r["seconds"] for r in cell]))
                work += mean * (640 // 2 if arm in ib.ARMS else 16)
                cells.append(dict(target=family + th, arm=arm, mean_seconds=mean,
                    n=len(cell), max_seconds=max(r["seconds"] for r in cell)))
        tail = max(r["seconds"] for r in family_rows)
        verifier_tails = [r for r in family_rows if r["verifier_seconds"] >= 60]
        learned = [r for r in family_rows if r["arm"].split("/")[0] in ib.ARMS]
        learned_tails = [r for r in learned if r["verifier_seconds"] >= 60]
        tail_work = sum(r["verifier_seconds"] * (32 if r["arm"].split("/")[0] in ib.ARMS else 16)
                        for r in verifier_tails)
        estimate = work / workers + (workers - 1) / workers * tail
        result[family] = dict(expected_seconds=estimate, worker_seconds=work, cells=cells,
            final_worker_allowance=(workers - 1) / workers * tail,
            verifier_tail_count=len(verifier_tails), n=len(family_rows),
            observed_tail_rate=len(verifier_tails) / len(family_rows),
            learned_tail_count=len(learned_tails), learned_n=len(learned),
            learned_tail_rate=len(learned_tails) / len(learned),
            verifier_tail_seconds=sum(r["verifier_seconds"] for r in verifier_tails),
            projected_verifier_tail_worker_seconds=tail_work,
            stage_timeout_seconds=2400 if family == "sum" else 5400,
            split_max=family == "max" and estimate > 4500)
    return result


def timing(out, source, workers):
    start = time.monotonic()
    rows, paths = source_rows(source)
    jobs = timing_jobs(out, rows)
    ib.eb.write_json(out / "timing_roster.json", jobs)
    for j in jobs:
        j["deadline"] = start + TIMING_SECONDS
    searches = ib.parallel(ib.score, jobs, workers)
    ib.eb.write_json(out / "timing.json", dict(wall_seconds=time.monotonic() - start,
        source_sha256={str(p.resolve()): digest(p) for p in paths.values()}, searches=searches))
    if not all(r["complete"] for r in searches):
        raise RuntimeError("incomplete timing searches; missingness, not censoring")
    price = scoring_price(searches, workers)
    ib.eb.write_json(out / "projection.json", price)
    return price
