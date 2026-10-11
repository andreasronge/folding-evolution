import itertools, collections
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from probe_order import X, lo, hi, inputs, T
from probe2 import srcs, run
H={}
for a,b in itertools.combinations(range(4),2):
    H[lo(a,b).tobytes()]=f"lo{a}{b}"; H[hi(a,b).tobytes()]=f"hi{a}{b}"
def census(row):
    t=T.Tree(tuple(row["attempts"][-1]["solver_tree"]))
    found=set(); nodes=[]
    for p in range(len(t.prefix)):
        sub=T.Tree(t.prefix[p:t.ends[p]])
        v=np.array([T.interpret(sub,x) for x in inputs])
        if v.tobytes() in H: found.add(H[v.tobytes()]); nodes.append(len(sub.prefix))
    return found, nodes, len(t.prefix)
if __name__=="__main__":
    with ProcessPoolExecutor(10) as ex:
        rows=list(ex.map(run,[(c,srcs[c],7500+s*100+i,None) for i,c in enumerate(srcs) for s in range(3)]))
    sol=[r for r in rows if r["solved"]]
    hits=0; match=0; sizes=collections.Counter(); tot=[]
    for r in sol:
        f,n,L=census(r); tot.append(L)
        own=r["cell"][:4]
        hits+= bool(f); match+= own in f; sizes.update(n)
    print("solved",len(sol),"/",len(rows),"solver nodes median",np.median(tot))
    print("solvers containing any lo/hi-equivalent subtree",hits,"own helper",match,"subtree sizes",sorted(sizes.items()))
