"""Steward probe (read-only, 2026-10-09-0826): which tokens in the 1246 G4 exact-solver tapes
are knockout-active (NOP substitution changes output on a 96-input sample), and how many short
active fragments recur across >= 2 source cells of the same corpus. Uses research/main's Python
executor extracted to /tmp/rmain (git archive research/main src experiments/chem_tape)."""
import sys, json, collections, time
sys.path[:0] = ["/tmp/rmain", "/tmp/rmain/src"]
import numpy as np
from folding_evolution.chem_tape.executor import execute_program
from experiments.chem_tape.composition_bank import TA

OUT = "experiments/output/2026-10-08/2026-10-08-1246-comparison-gate-training"
bank = json.load(open(f"{OUT}/bank.json"))
lab = {c["id"]: np.array(c["labels"]) for c in bank["cells"]}
rng = np.random.default_rng(0)
idx = rng.choice(len(bank["inputs"]), 96, replace=False)
xs = [bank["inputs"][i] for i in idx]
run = lambda t: np.array([execute_program(list(t), TA, list(x), "intlist", "v2_rmin_first") for x in xs])

t0 = time.time()
rows = [json.loads(l) for l in open(f"{OUT}/search.jsonl")]
tapes = collections.defaultdict(list)
for r in rows:
    if r.get("phase") == "collection" and r["solved"]:
        tapes[r["corpus"]].append((r["cell"], r["solver"]))
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10**9
n_active, contiguous_runs, bad = [], [], 0
summary = {}
for corpus, items in sorted(tapes.items()):
    per_cell = collections.defaultdict(set)
    per_cell_contig = collections.defaultdict(set)
    for cell, tape in items[:limit]:
        base = run(tape)
        bad += not np.array_equal(base, lab[cell][idx])
        act = []
        for j in range(32):
            t = list(tape); t[j] = 0
            act.append(not np.array_equal(run(t), base))
        n_active.append(sum(act))
        seq = tuple(tape[j] for j in range(32) if act[j])  # active tokens in order (gaps removed)
        for L in range(3, 7):
            for s in range(len(seq) - L + 1):
                per_cell[cell].add(seq[s:s + L])
        # contiguous tape windows whose every token is active
        for L in range(3, 7):
            for s in range(32 - L + 1):
                if all(act[s:s + L]):
                    per_cell_contig[cell].add(tuple(tape[s:s + L]))
    def recurring(d):
        c = collections.Counter()
        for fs in d.values():
            c.update(fs)
        return {f: k for f, k in c.items() if k >= 2}
    g, cg = recurring(per_cell), recurring(per_cell_contig)
    summary[corpus] = dict(gapped=len(g), contiguous=len(cg),
                           contiguous_by_len=dict(collections.Counter(len(f) for f in cg)),
                           top=[(list(f), k) for f, k in sorted(cg.items(), key=lambda kv: (-kv[1], -len(kv[0])))[:5]])
print("label mismatches", bad, "solvers", len(n_active))
print("knockout-active tokens per solver: median", np.median(n_active), "IQR", np.percentile(n_active, [25, 75]))
for k, v in summary.items():
    print(k, v)
print("seconds", round(time.time() - t0, 1))
