import itertools, time, sys, json
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape import tree_gp_search as T
X = np.asarray(inputs_for("D625"))
def lo(a,b): return np.where(X[:,a]>X[:,b], X[:,b], X[:,a])
def hi(a,b): return np.where(X[:,a]>X[:,b], X[:,a], X[:,b])
cells=[]
cells.append(("src lo01+X2", lo(0,1)+X[:,2]))
cells.append(("src hi23+X0", hi(2,3)+X[:,0]))
cells.append(("src lo13+X0", lo(1,3)+X[:,0]))
cells.append(("dst lo01+hi23", lo(0,1)+hi(2,3)))
cells.append(("dst lo01+hi12", lo(0,1)+hi(1,2)))
cells.append(("dst lo02+hi13", lo(0,2)+hi(1,3)))
inputs=[list(map(int,x)) for x in X]
LIB=[T.Tree((11,a,b,10,a,b)) for a,b in itertools.combinations(range(4),2)]+[T.Tree((11,b,a,10,a,b)) for a,b in itertools.combinations(range(4),2)]
def run(args):
    name,lab,seed,arm=args
    cell={"id":name,"labels":[int(v) for v in lab]}
    r=T.search((cell,seed,65536,256,inputs,0.5),donor_library=LIB if arm=="order" else None)
    return name,arm,seed,r["solved"],r["evaluations"],round(r["seconds"],1)
if __name__=="__main__":
    lab=lo(0,1); 
    for t_ in LIB[:1]+LIB[6:7]: print(t_.prefix, np.array_equal([T.interpret(t_,x) for x in inputs], lo(0,1) if t_ is LIB[0] else hi(0,1)))
    jobs=[(n,l,s,"tree") for n,l in cells for s in range(9000,9006)]+[(n,l,s,"order") for n,l in cells if n.startswith("dst") for s in range(9000,9006)]
    t=time.time()
    with ProcessPoolExecutor(10) as ex:
        for res in ex.map(run,jobs): print(*res, flush=True)
    print("wall",time.time()-t)
