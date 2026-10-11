import itertools, time, collections
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from probe_order import X, lo, hi, inputs, LIB, T
from experiments.chem_tape.tree_library import extract
H={'lo':lo,'hi':hi}
srcs={}
for f in ('lo','hi'):
    for a,b in itertools.combinations(range(4),2):
        for c in range(4):
            if c not in (a,b): srcs[f"{f}{a}{b}+X{c}"]=H[f](a,b)+X[:,c]
def run(args):
    name,lab,seed,lib=args
    r=T.search(({"id":name,"labels":[int(v) for v in lab]},seed,65536,256,inputs,0.5),donor_library=lib)
    return dict(cell=name,arm="R-tree",solved=r["solved"],evaluations=r["evaluations"],attempts=[dict(solver_tree=r["solver_tree"])])
helpers={tuple(t.prefix) for t in LIB}
def describe(entries):
    from experiments.chem_tape.tree_library import canonical
    hc={canonical(t) for t in LIB}
    return sum(tuple(e["canonical"]) in hc for e in entries), [e["nodes"] for e in entries]
if __name__=="__main__":
    t=time.time()
    builds={}
    with ProcessPoolExecutor(10) as ex:
        # build A: four cells, two helpers each in two cells; build B,C: all 24 cells x 1 job, different seeds
        A=["lo01+X2","lo01+X3","hi23+X0","hi23+X1"]
        rows=list(ex.map(run,[(c,srcs[c],7000+s,None) for c in A for s in range(8)]))
        builds["A4x8"]=(rows,A)
        for k,base in (("B24x1",7100),("C24x1",7200)):
            rows=list(ex.map(run,[(c,srcs[c],base+i,None) for i,c in enumerate(srcs)]))
            builds[k]=(rows,list(srcs))
        Ar=["lo02+X1","hi13+X0","lo23+X0","hi01+X2"]  # 4 cells, no helper repeats
        rows=list(ex.map(run,[(c,srcs[c],7300+s,None) for c in Ar for s in range(8)]))
        builds["D4x8norep"]=(rows,Ar)
        dst={"lo01+hi23":lo(0,1)+hi(2,3),"lo01+hi12":lo(0,1)+hi(1,2),"lo02+hi13":lo(0,2)+hi(1,3)}
        for k,(rows,cells) in builds.items():
            ev=sum(r["evaluations"] for r in rows); sv=sum(r["solved"] for r in rows)
            entries,_=extract(rows,set(cells))
            nh,nodes=describe(entries)
            print(k,"src solved",sv,"/",len(rows),"evals",ev,"entries",len(entries),"helper-entries",nh,"nodes",nodes)
            for e in entries[:16]: print("   ",e["prefix"],e["source_cells"].__len__())
            lib=[T.Tree(tuple(e["prefix"])) for e in entries]
            res=list(ex.map(run,[(n,l,s,lib) for n,l in dst.items() for s in range(9000,9006)]))
            print("   learned on dst:",[(r["cell"],r["solved"],r["evaluations"]) for r in res])
            print("   mean evals",np.mean([r["evaluations"] for r in res]),"solved",sum(r["solved"] for r in res))
    print("wall",time.time()-t)
