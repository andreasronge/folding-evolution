import itertools, time, sys, json, collections
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape import tree_gp_search as T
X = np.asarray(inputs_for("D625")); inputs=[list(map(int,x)) for x in X]
def s(a,b): return X[:,a]+X[:,b]
def pos(a,b): v=s(a,b); return np.where(v>0,v,0)
def neg(a,b): v=s(a,b); return np.where(v>0,0,v)
F={'pos':pos,'neg':neg}
PAIRS=list(itertools.combinations(range(4),2))
SRC={f"{f}{a}{b}+X{c}":F[f](a,b)+X[:,c] for f in F for a,b in PAIRS for c in range(4) if c not in (a,b)}
DST={f"pos{a}{b}+neg{c}{d}":pos(a,b)+neg(c,d) for a,b in PAIRS for c,d in PAIRS if (a,b)!=(c,d)}
def ptree(a,b): return T.Tree((11,5,9,a,b,9,a,b))
def ntree(a,b): return T.Tree((11,9,a,b,5,9,a,b))
RECT=[ptree(a,b) for a,b in PAIRS]+[ntree(a,b) for a,b in PAIRS]
HV={}
for a,b in PAIRS: HV[pos(a,b).astype('<i8').tobytes()]=f"pos{a}{b}"; HV[neg(a,b).astype('<i8').tobytes()]=f"neg{a}{b}"
def execute(args):
    name,lab,seeds,lib=args
    donors=None if lib is None else [T.Tree(tuple(p)) for p in lib]
    t=time.monotonic(); att=[]
    for sd in seeds:
        r=T.search((dict(id=name,labels=[int(v) for v in lab]),sd,65536,256,inputs,0.5),donor_library=donors)
        att.append(dict(seed=sd,solved=r['solved'],evaluations=r['evaluations'],solver_tree=r['solver_tree']))
        if r['solved']: break
    return dict(cell=name,arm='R-tree',build=0,repeat=0,solved=att[-1]['solved'],evaluations=sum(a['evaluations'] for a in att),
                worker_seconds=time.monotonic()-t,attempts=att)
if __name__=="__main__":
    for t_,v in zip(RECT,[pos(a,b) for a,b in PAIRS]+[neg(a,b) for a,b in PAIRS]):
        assert np.array_equal([T.interpret(t_,x) for x in inputs], v), t_.prefix
    print("helper trees verified; tokens",[len(t.program) for t in RECT[:1]], flush=True)
