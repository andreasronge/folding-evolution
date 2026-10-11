"""Reviewer: construction audit summary, operator use and solver-content checks."""
import json, re
from collections import Counter
import numpy as np
from experiments.chem_tape.tree_gp_search import Tree

S = "/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0524-score"
P = "/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0524-prepare"
ARMS = ("R-tree", "R-lib", "R-perm")
rows = [json.loads(l) for l in open(f"{S}/search.jsonl")]
print("attempt keys:", sorted(rows[0]["attempts"][0].keys()))
for k, v in rows[0]["attempts"][0].items():
    if isinstance(v, dict) and k not in ("budget_seconds",): print("  ", k, json.dumps(v)[:300])

def split(cell):
    m = re.match(r"GS:\(X(\d)\+X(\d)\)>\(X(\d)\+X(\d)\)\?\(X(\d)\+X(\d)\):X(\d)", cell)
    a, b, c, d, e, f, g = map(int, m.groups())
    s = tuple(sorted([tuple(sorted((a, b))), tuple(sorted((c, d)))]))
    return {((0,1),(2,3)): "A", ((0,2),(1,3)): "B", ((0,3),(1,2)): "C"}[s], s
SPLIT = {r["cell"]: split(r["cell"]) for r in rows}

# --- construction audit ---
audit = json.load(open(f"{P}/construction_audit.json"))
libs = json.load(open(f"{P}/libraries.json"))
print("\n== construction audit: 24 builds x 3 realizations =", len(audit["per_construction"]))
orig = Counter(); perm = [Counter() for _ in range(3)]
origp = Counter(); permp = [Counter() for _ in range(3)]
changed = []; cb = []; ub = []; uo = []; ent = 0
for a in audit["per_construction"]:
    k = a["realization"]
    for s, v in a["original_motifs"]["split_pair_counts"].items(): orig[s] += v
    for s, v in a["motifs"]["split_pair_counts"].items(): perm[k][s] += v
    for s, v in a["original_motifs"]["ordered_predicate_counts"].items(): origp[s] += v
    for s, v in a["motifs"]["ordered_predicate_counts"].items(): permp[k][s] += v
    changed.append(a["changed"] / a["entry_count"]); cb.append(a["changed_behaviours"] / a["entry_count"]); ub.append(a["unique_behaviours"]); ent += a["entry_count"]
print("entries per realization", ent // 3, " mean entries per library", ent / 72)
print("distinct-input pair sums by split, summed over 24 libraries: intact", dict(orig))
for k in range(3): print("   realization", k, dict(perm[k]))
print("ordered GT(ADD,ADD) predicates by orientation, intact:", {k: v for k, v in origp.items() if v})
for k in range(3): print("   realization", k, {s: v for s, v in permp[k].items() if v})
print("changed entries share: mean %.2f min %.2f max %.2f" % (np.mean(changed), min(changed), max(changed)))
print("changed behaviours share: mean %.2f min %.2f" % (np.mean(cb), min(cb)))
# unique behaviours intact vs permuted
orig_unique = {}
from experiments.chem_tape.composition_search import outputs
bank = json.load(open(f"{P}/bank.json"))
from experiments.chem_tape.independent_input_bank import ALPHABET
for lib in libs:
    o = outputs([Tree(tuple(e["prefix"])).program for e in lib["entries"]], bank["inputs"], ALPHABET)
    orig_unique[lib["build"]] = len({r.tobytes() for r in o})
print("unique behaviours: intact total", sum(orig_unique.values()), " per realization", [sum(a["unique_behaviours"] for a in audit["per_construction"] if a["realization"] == k) for k in range(3)])
print("library sizes:", sorted(len(l["entries"]) for l in libs))
big = [sum(e["nodes"] >= 5 for e in l["entries"]) for l in libs]
print("entries with >=5 nodes per library:", big, "total", sum(big))
# per-library predicate: which builds have A predicate intact
hasA = [l["build"] for l in libs if any(v for k, v in audit["per_construction"][3*l["build"]]["original_motifs"]["ordered_predicate_counts"].items())]
print("builds with an intact GT(ADD,ADD) predicate:", len(hasA), "; without:", [b for b in range(24) if b not in hasA])

# --- operator use per arm on B/C ---
print("\n== operator/library use on B/C (summed over attempts)")
for a in ARMS:
    tot = Counter(); n = 0
    for r in rows:
        if r["arm"] == a and SPLIT[r["cell"]][0] in "BC":
            n += 1
            for at in r["attempts"]:
                for k, v in at.items():
                    if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in ("seed", "cap", "pop_size", "crossover", "evaluations", "seconds", "generations"): tot[k] += v
                for kk in ("operators", "library", "counters", "stats"):
                    if isinstance(at.get(kk), dict):
                        for k, v in at[kk].items():
                            if isinstance(v, (int, float)): tot[kk + "." + k] += v
    print(" ", a, n, dict(tot))

# --- solver content ---
def subtrees(prefix):
    t = Tree(tuple(prefix))
    return [tuple(t.prefix[i:t.ends[i]]) for i in range(len(t.prefix))]
def gt_add_add(sub):
    # GT(ADD(Xa,Xb),ADD(Xc,Xd)) with distinct inputs, returns the split
    if len(sub) == 7 and sub[0] == 10 and sub[1] == 9 and sub[4] == 9 and all(x < 4 for x in (sub[2], sub[3], sub[5], sub[6])) and sub[2] != sub[3] and sub[5] != sub[6]:
        return tuple(sorted([tuple(sorted(sub[2:4])), tuple(sorted(sub[5:7]))]))
    return None
lib_entries = {l["build"]: {tuple(e["prefix"]) for e in l["entries"] if e["nodes"] >= 5} for l in libs}
perm_entries = {(l["build"], c["realization"]): {tuple(e["prefix"]) for e in c["entries"] if e["nodes"] >= 5} for l in libs for c in l["constructions"]}
print("\n== solver content (solved jobs; denominators = solved jobs in group)")
print("group arm | n | has GT(ADD,ADD) of the cell's split | has any GT(ADD,ADD) | contains a >=5-node entry of its own donor set verbatim | contains an INTACT >=5-node entry verbatim | mean solver nodes")
for grp, pred in [("A", lambda s: s == "A"), ("B/C", lambda s: s in "BC")]:
    for a in ARMS:
        n = own = intact = anyp = right = 0; nodes = []
        for r in rows:
            if r["arm"] != a or not pred(SPLIT[r["cell"]][0]) or not r["solved"]: continue
            n += 1
            st = r["attempts"][-1]["solver_tree"]; subs = subtrees(st); nodes.append(len(st))
            ps = [gt_add_add(s) for s in subs]; ps = [p for p in ps if p]
            anyp += bool(ps); right += SPLIT[r["cell"]][1] in ps
            own_set = lib_entries[r["build"]] if a == "R-lib" else perm_entries[r["build"], r["realization"]] if a == "R-perm" else set()
            own += bool(own_set & set(subs)); intact += bool(lib_entries[r["build"]] & set(subs))
        print(f"{grp} {a} | {n} | {right} ({right/n:.2f}) | {anyp} ({anyp/n:.2f}) | {own} ({own/n:.2f}) | {intact} ({intact/n:.2f}) | {np.mean(nodes):.1f}")
