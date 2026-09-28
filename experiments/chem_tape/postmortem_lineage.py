"""Map-bias / valley-crossing Step 0: where did each output run of a tagged solver come from?

Plans/valley-crossing.md, Step 0. The saved lineage (lineage.npz) follows only the fitter
parent at each crossover, so a run built silently in the less fit parent is never seen.
Here each tagged solver is re-run in-process up to its first exact generation (same
config and seed, so the trajectory is identical; checked against the original
history.csv), and every output (tag-0) run of the solver is traced back through *both*
parents, generation by generation, following the run itself rather than the main line.

At each step back the run's predecessor is the most similar run in the parent(s) of the
current individual, comparing what the runs compute (ops, plus tags on RECV cells only,
trailing NOPs stripped — other tags are inert and re-randomised; see _key); a run under another tag qualifies only if its body is >= 90% similar,
with a small penalty (see _score). On exact ties between the two crossover parents the
fitter (main) parent is chosen, so "from the less fit parent" counts only unambiguous cases.
Solvers whose re-run does not reproduce the original genome are excluded from the report. Events recorded: crossovers where the predecessor sat in the less fit parent
(merge), tag changes (retag; whether any RECV in that genome read the old tag), and the
generation where the trace ends (similarity < MIN_SIM: the run was written here, or
generation 0).

Labels per output run, from its tag-0 period (the contiguous stretch ending at the solve
where it had tag 0):
  retag_from_silent  became tag 0 by a header retag from a tag nothing read
  retag_from_helper  became tag 0 from a tag some RECV read (a helper promoted)
  retag_from_output  (leftmost helpers) got its tag from tag 0: a former output run
                     demoted to a helper
  built_as_output    written under tag 0 (trace ended inside the tag-0 period); for a
                     leftmost helper: written under its own tag
Leftmost-wins solvers (tag_combine "leftmost"): only the first run of each tag is read, so
the traced runs are the first tag-0 run and the runs it reaches by RECV.
  since_gen0         tag 0 since the random initial population
  copy_of_output_run the run's trace joins an earlier output run's trace (a copy);
                     `copy_mode` says whether both copies sat in one genome right after
                     the copy (made within one step, e.g. a crossover cut) or were
                     brought together later by crossover
plus, for retags, whether the body changed while silent, and how often the run's
predecessor came from the less fit parent (homologous crossover swaps same-tag bodies
between relatives all the time, so this count is churn, not a merge by itself).
Runs are traced jointly, so identical runs in one parent are not mistaken for a copy.

Usage: uv run python experiments/chem_tape/postmortem_lineage.py <day dir> <out dir> [--workers N]
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from dataclasses import replace
from difflib import SequenceMatcher
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import overnight_analysis as oa  # noqa: E402

from folding_evolution.chem_tape import tagged  # noqa: E402
from folding_evolution.chem_tape.evolve import run_evolution  # noqa: E402

MIN_SIM = 0.5
# (sweep dir, arm label from overnight_analysis.arm_name) — the solvers to trace.
TARGETS = [
    ("mapbias_xor_race", "tagged"),
    ("mapbias_xor_race", "tagged tagged_comb"),
    ("mapbias_knob_comb_and", "tagged tagged_comb"),
]
KIND = {0: "elite", 1: "crossover", 2: "copy"}


def _read_tags(g: np.ndarray) -> set[int]:
    return {tg for _, body in tagged.parse_runs(g) for op, tg in body if op == tagged.RECV}


RETAG_MIN_SIM = 0.9
RETAG_PENALTY = 0.05


def _key(body: tuple) -> tuple:
    """What a run computes: ops, with the tag kept only on RECV cells (other cells' tags do
    nothing and are re-randomised by padding and mutation), trailing NOPs stripped."""
    return tuple((op, tg if op == tagged.RECV else -1) for op, tg in tagged._strip_trailing_nops(body))


def _score(tag: int, body: tuple, ctag: int, cbody: tuple) -> float:
    """Body similarity (1.0 = identical). A candidate under another tag (a retag) needs
    similarity >= RETAG_MIN_SIM and pays RETAG_PENALTY, so a same-tag ancestor one or two
    mutations away still beats an unrelated identical body under another tag, while a real
    retag that coincided with a small body mutation is still found."""
    body, cbody = _key(body), _key(cbody)
    if not body and not cbody:
        sim = 1.0
    else:
        sim = 1.0 if cbody == body else SequenceMatcher(None, body, cbody, autojunk=False).ratio()
    if ctag == tag:
        return sim
    return sim - RETAG_PENALTY if sim >= RETAG_MIN_SIM else 0.0


def trace_runs(ks: list[int], idx: int, G: int, pops, fits, parents) -> list[list[dict]]:
    """Trace runs `ks` of individual idx at generation G back together. Returns one path
    per run: dicts {g, idx, k, tag, body, ...}, newest first. Step info (kind, from_other,
    retag_from, from_read) sits on the dict of the generation it leads *from*. A path ends
    with end = "written" (no predecessor with similarity >= MIN_SIM), "gen0", or
    "coalesced" (its predecessor is also an earlier run's predecessor: a copy)."""
    runs = tagged.parse_runs(pops[G][idx])
    paths = [[{"g": G, "idx": idx, "k": k, "tag": runs[k][0], "body": runs[k][1]}] for k in ks]
    active = list(range(len(ks)))
    for g in range(G, 0, -1):
        taken: dict[tuple, int] = {}                  # (idx, k) at g-1 -> trace that took it
        by_idx = collections.defaultdict(list)
        for t in active:
            by_idx[paths[t][-1]["idx"]].append(t)
        still = []
        for cur, ts in sorted(by_idx.items(), key=lambda kv: min(kv[1])):   # earlier runs first
            p1, p2, kind, _ = (int(x) for x in parents[g][cur])
            main = p2 if kind == 1 and fits[g - 1][p2] > fits[g - 1][p1] else p1
            cands = [(p1, k, t_, b) for k, (t_, b) in enumerate(tagged.parse_runs(pops[g - 1][p1]))]
            if kind == 1:
                cands += [(p2, k, t_, b) for k, (t_, b) in enumerate(tagged.parse_runs(pops[g - 1][p2]))]
            used: set[int] = set()
            for t in sorted(ts):                      # earlier output runs choose first
                node = paths[t][-1]
                scored = [(_score(node["tag"], node["body"], c[2], c[3]), c[0] != main, ci)
                          for ci, c in enumerate(cands)]
                if not scored:
                    node["end"] = "written"
                    continue
                top = max(s_ for s_, _, _ in scored)
                if top < MIN_SIM:
                    node["end"] = "written"
                    continue
                # Among equally good candidates prefer one no other trace in this
                # individual took (identical runs are not a coalescence), then the main parent.
                ties = sorted((ci in used, not_main, ci) for s_, not_main, ci in scored if s_ >= top - 1e-9)
                _, _, ci = ties[0]
                used.add(ci)
                pidx, pk, ptag, pbody = cands[ci]
                node["kind"] = KIND[kind]
                node["from_other"] = bool(kind == 1 and pidx != main)
                node["exact"] = _key(cands[ci][3]) == _key(node["body"])
                # Wiring event: the run gained a RECV of a tag some run in its own genome owns.
                new_recv = ({tg for op, tg in node["body"] if op == tagged.RECV}
                            - {tg for op, tg in cands[ci][3] if op == tagged.RECV})
                if new_recv & {t_ for t_, _ in tagged.parse_runs(pops[g][cur])}:
                    node["rewire"] = True
                if ptag != node["tag"]:
                    node["retag_from"] = ptag
                    node["from_read"] = ptag in _read_tags(pops[g - 1][pidx])
                nxt = {"g": g - 1, "idx": pidx, "k": pk, "tag": ptag, "body": pbody}
                key = (pidx, pk)
                if key in taken:
                    nxt["end"] = "coalesced"
                    nxt["with"] = taken[key]
                else:
                    taken[key] = t
                    still.append(t)
                paths[t].append(nxt)
        # Traces that coalesced with a trace that is still active keep only the marker.
        active = sorted(still)
        if not active:
            break
    for t in active:
        paths[t][-1]["end"] = "gen0"
    return paths


def classify(path: list[dict], paths: list[list[dict]]) -> dict:
    # Tag period: from the solve back while the run has its final tag (tag 0 for output
    # runs; a helper's own tag under leftmost-wins).
    j = 0
    while j + 1 < len(path) and path[j + 1]["tag"] == path[0]["tag"]:
        j += 1
    period = path[: j + 1]
    merges = [s["g"] for s in period if s.get("from_other")]
    out = {"tag0_since": path[j]["g"], "n_from_other_parent": len(merges),
           "n_rewires": sum(bool(s.get("rewire")) for s in period),
           "last_from_other_parent": merges[0] if merges else None, "trace_len": len(path) - 1}
    last = path[j]
    end = last.get("end")
    if end == "gen0":
        out["label"] = "since_gen0"
    elif end == "written":
        out["label"] = "built_as_output"
    elif end == "coalesced":
        out["label"] = "copy_of_output_run"
        other = paths[last["with"]]
        out["copy_of"] = last["with"]
        out["copy_gen"] = last["g"]
        # When did the copy and the original first sit in the same individual (going
        # forward), and by what step? Same individual right after the copy = made inside
        # one genome (crossover cut / duplication); later = brought together by crossover.
        mine = {s["g"]: s["idx"] for s in path}
        theirs = {s["g"]: s["idx"] for s in other}
        together = None
        for g in range(last["g"] + 1, path[0]["g"] + 1):
            if mine.get(g) is not None and mine.get(g) == theirs.get(g):
                together = g
                break
        out["together_gen"] = together
        step = next((s for s in path if s["g"] == together), {})
        out["copy_mode"] = ("within_one_step" if together == last["g"] + 1 else "joined_later") + \
            f":{step.get('kind', '?')}"
    else:
        # From tag 0: the run was an output run (or, under leftmost-wins, an inert later
        # tag-0 run) — not silent in the "unread tag" sense.
        out["label"] = ("retag_from_output" if last.get("retag_from") == tagged.OUTPUT_TAG
                        else "retag_from_helper" if last.get("from_read") else "retag_from_silent")
        # Before the retag: how long under a non-zero tag, and did the body change there?
        m = j + 1
        while m + 1 < len(path) and path[m + 1]["tag"] == path[j + 1]["tag"]:
            m += 1
        out["retag_from_tag"] = path[j + 1]["tag"]
        out["pre_retag_gens"] = path[j + 1]["g"] - path[m]["g"] + 1
        out["body_changed_before_retag"] = any(_key(path[i]["body"]) != _key(path[i + 1]["body"])
                                               for i in range(j + 1, m))
        out["retag_exact"] = bool(last.get("exact"))
        out["pre_retag_start"] = path[m].get("end") or "continued"
    return out


def analyze(item) -> dict:
    run_dir, c, first = item
    cfg = replace(oa.cfg_of(c), generations=int(first))
    rows = list(csv.DictReader(open(Path(run_dir) / "history.csv")))
    orig = np.frombuffer(bytes.fromhex(rows[int(first)]["best_genotype_hex"]), dtype=np.uint8)
    res = run_evolution(cfg)
    gens = res.generations
    pops, fits, parents = gens["pops"], gens["fits"], gens["parents"]
    G = len(pops) - 1
    idx = int(np.argmax(fits[G]))
    solver = pops[G][idx]
    out = {"run_dir": str(run_dir), "arm": oa.arm_name(c), "seed": c["seed"], "first_exact_gen": int(first),
           "reproduced": bool(G == int(first) and np.array_equal(solver, orig)),
           "exact": bool(oa.exact_many([solver], cfg, cfg.task)[0])}
    runs = tagged.parse_runs(solver)
    roles = {}
    if cfg.tag_combine == "leftmost":
        # Only the first run of each tag is ever read: trace the first tag-0 run and the
        # runs it reaches by RECV (breadth first); later same-tag runs are inert.
        first = {}
        for k, (tag, _) in enumerate(runs):
            first.setdefault(tag, k)
        out_idx, queue = [], [first.get(tagged.OUTPUT_TAG)]
        while queue:
            k = queue.pop(0)
            if k is None or k in out_idx:
                continue
            out_idx.append(k)
            roles[k] = "output" if k == first.get(tagged.OUTPUT_TAG) else f"helper(tag {runs[k][0]})"
            queue += [first.get(tg) for op, tg in runs[k][1] if op == tagged.RECV]
        out["output_live_recvs"] = len({tg for op, tg in runs[out_idx[0]][1]
                                        if op == tagged.RECV and tg in first}) if out_idx else 0
        out["inert_tag0_runs"] = sum(tag == tagged.OUTPUT_TAG for tag, _ in runs) - 1
    else:
        out_idx = [k for k, (tag, _) in enumerate(runs) if tag == tagged.OUTPUT_TAG]
    out["n_output_runs"] = len(out_idx)
    out["runs"] = []
    paths = trace_runs(out_idx, idx, G, pops, fits, parents)
    for order, k in enumerate(out_idx):
        r = {"order": order, "len": len(runs[k][1]), **classify(paths[order], paths)}
        if roles:
            r["role"] = roles[k]
        if cfg.alphabet == "tagged_comb" and order > 0:
            r["join"] = {tagged.C_MIN: "min", tagged.C_ADD: "add", tagged.C_GATE: "gate"}.get(
                tagged._marker(runs[k][1]), "max")
        out["runs"].append(r)
    return out


def load_items(day: Path) -> list:
    items = []
    for sweep, arm in TARGETS:
        loaded = oa.load(day / sweep)
        rows = json.loads((day / sweep / "analysis.json").read_text())
        assert len(loaded) == len(rows), f"{sweep}: analysis.json has {len(rows)} rows for {len(loaded)} runs"
        for (run_dir, c), r in zip(loaded, rows):
            assert r["seed"] == c["seed"] and r["arm"] == oa.arm_name(c), "analysis.json out of order"
            if r["arm"] == arm and r["final_exact"] and r["first_exact_gen"] is not None:
                items.append((run_dir, c, r["first_exact_gen"]))
    return items


def report(all_rows: list[dict]) -> list[str]:
    rows = [r for r in all_rows if r["reproduced"] and r["exact"]]
    bad = [f"{r['arm']} seed {r['seed']}" for r in all_rows if not (r["reproduced"] and r["exact"])]
    lines = ["# Lineage post-mortem (both parents traced)", "",
             f"Solvers: {len(all_rows)}; reproduced exactly and exact at the stop (counted below): "
             f"{len(rows)}." + (f" Excluded: {', '.join(bad)}." if bad else ""), ""]
    for key in dict.fromkeys((r["run_dir"].split("/")[-2], r["arm"]) for r in rows):
        rs = [r for r in rows if (r["run_dir"].split("/")[-2], r["arm"]) == key]
        if "output_live_recvs" in rs[0]:
            lines += leftmost_report(key, rs)
            continue
        lines += [f"## {key[0]} — {key[1]} ({len(rs)} solvers)", "",
                  "| output run | n | built as output | copy of output run (in one step / joined later) | "
                  "retag from silent | retag from helper | since gen 0 |", "|---|---|---|---|---|---|---|"]
        for order in range(max(r["n_output_runs"] for r in rs)):
            runs = [x for r in rs for x in r["runs"] if x["order"] == order]
            lab = collections.Counter(x["label"] for x in runs)
            one = sum(x.get("copy_mode", "").startswith("within") for x in runs)
            lines.append(f"| #{order + 1} | {len(runs)} | {lab['built_as_output']} | "
                         f"{lab['copy_of_output_run']} ({one} / {lab['copy_of_output_run'] - one}) | "
                         f"{lab['retag_from_silent']} | {lab['retag_from_helper']} | {lab['since_gen0']} |")
        modes = collections.Counter(x["copy_mode"] for r in rs for x in r["runs"] if "copy_mode" in x)
        if modes:
            lines += ["", f"Copy steps (mode:kind): {dict(modes)}"]
        rt = [x for r in rs for x in r["runs"] if x["label"].startswith("retag")]
        if rt:
            lines += ["", "Retags: " + "; ".join(
                f"seed {r['seed']} run #{x['order'] + 1}: tag {x['retag_from_tag']}→0, "
                f"{x['pre_retag_gens']} gens before, body changed: {x['body_changed_before_retag']}, "
                f"exact body at retag: {x['retag_exact']}"
                for r in rs for x in r["runs"] if x["label"].startswith("retag"))]
        rw = [x["n_rewires"] for r in rs for x in r["runs"]]
        lines += ["", f"Output runs with a RECV rewired to an existing run during their tag-0 period: "
                      f"{sum(n > 0 for n in rw)}/{len(rw)}"]
        joins = collections.Counter(x["join"] for r in rs for x in r["runs"] if "join" in x)
        if joins:
            lines += ["", f"Joins of later output runs: {dict(joins)}"]
        lines.append("")
    return lines


def leftmost_report(key, rs: list[dict]) -> list[str]:
    """Leftmost-wins: the output run (first tag-0 run) and the helpers it reads by RECV."""
    lines = [f"## {key[0]} — {key[1]} ({len(rs)} solvers; leftmost-wins, live runs only)", "",
             "Per solver: output run's live RECVs (0 = computes XOR itself), helpers, and how "
             "each live run arose under its final tag.", "",
             "| seed | first exact | live RECVs | output run | helpers | rewires in output run |",
             "|---|---|---|---|---|---|"]
    for r in sorted(rs, key=lambda r: r["first_exact_gen"]):
        o = r["runs"][0]
        hs = ", ".join(f"{x['role']}: {x['label']}" for x in r["runs"][1:]) or "-"
        lines.append(f"| {r['seed']} | {r['first_exact_gen']} | {r['output_live_recvs']} | {o['label']} "
                     f"(tag 0 since {o['tag0_since']}) | {hs} | {o['n_rewires']} |")
    lab = collections.Counter(x["label"] for r in rs for x in r["runs"])
    lines += ["", f"All live runs: {dict(lab)}. Self-contained output runs (no live RECV): "
                  f"{sum(r['output_live_recvs'] == 0 for r in rs)}/{len(rs)}. "
                  f"Inert extra tag-0 runs (median): {sorted(r['inert_tag0_runs'] for r in rs)[len(rs) // 2]}.", ""]
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("day")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0, help="first N solvers only (smoke test)")
    ap.add_argument("--target", action="append", default=[],
                    help="SWEEP_DIR=ARM (arm label as overnight_analysis.arm_name gives it); repeatable. "
                         "Default: the §16 tagged XOR / AND solvers.")
    a = ap.parse_args()
    if a.target:
        TARGETS[:] = [tuple(t.split("=", 1)) for t in a.target]
    items = load_items(Path(a.day))
    if a.limit:
        items = items[: a.limit]
    print(f"{len(items)} solvers", flush=True)
    with Pool(a.workers) as pool:
        rows = []
        for r in pool.imap_unordered(analyze, items):
            rows.append(r)
            print(f"  {r['arm']} seed {r['seed']}: reproduced={r['reproduced']} "
                  f"{[x['label'] for x in r['runs']]}", flush=True)
    rows.sort(key=lambda r: (r["run_dir"]))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "postmortem.json").write_text(json.dumps(rows, indent=1))
    lines = report(rows)
    (out / "postmortem.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
