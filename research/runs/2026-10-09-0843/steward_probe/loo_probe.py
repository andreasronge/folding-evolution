"""Steward probe (read-only, 2026-10-09-0843): leave-one-cell-out library sizes for the fragment
proposal. Same knockout rule as runs/2026-10-09-0826/steward_probe/fragment_probe.py; for each
corpus and held-out cell c, count contiguous all-active 3-6 windows recurring in >= 2 of the
other 3 cells, and how many of the top 32 (rank: source cells, count, length, tokens) solve any
of the corpus's 4 cells when NOP-padded."""
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
sizes, padded_solvers = [], 0
for corpus, items in sorted(tapes.items()):
    cells = sorted({c for c, _ in items})
    per_cell = collections.defaultdict(collections.Counter)
    for cell, tape in items:
        base = run(tape)
        act = [not np.array_equal(run(tape[:j] + [0] + tape[j + 1:]), base) for j in range(32)]
        for L in range(3, 7):
            for s in range(33 - L):
                if all(act[s:s + L]):
                    per_cell[cell][tuple(tape[s:s + L])] += 1
    out = []
    for held in cells:
        src = [c for c in cells if c != held]
        n_cells, cnt = collections.Counter(), collections.Counter()
        for c in src:
            for f, k in per_cell[c].items():
                n_cells[f] += 1; cnt[f] += k
        rec = [f for f in n_cells if n_cells[f] >= 2]
        top = sorted(rec, key=lambda f: (-n_cells[f], -cnt[f], -len(f), f))[:32]
        solv = sum(any(np.array_equal(run(list(f) + [0] * (32 - len(f))), lab[c][idx]) for c in cells) for f in top)
        padded_solvers += solv
        sizes.append(len(rec)); out.append((len(rec), solv, collections.Counter(len(f) for f in top)))
    print(corpus, [(n, s) for n, s, _ in out], dict(out[0][2]))
print("LOO recurring windows: min", min(sizes), "median", np.median(sizes), "; top-32 that solve a cell padded:", padded_solvers)
print("seconds", round(time.time() - t0, 1))
