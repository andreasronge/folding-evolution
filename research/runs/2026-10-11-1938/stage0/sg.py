import itertools, time, sys, json, collections, pickle
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape import tree_gp_search as T
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape import order_library as OL
X = np.asarray(inputs_for("D625")); inputs=[list(map(int,x)) for x in X]
def p(a,b): return np.where(X[:,a]>0, X[:,b], 0)
def n(a,b): return np.where(X[:,a]>0, 0, X[:,b])
F={'p':p,'n':n}
OP=[(a,b) for a in range(4) for b in range(4) if a!=b]
SRC={f"{f}{a}{b}+2X{c}":F[f](a,b)+2*X[:,c] for f in F for a,b in OP for c in range(4) if c not in (a,b)}
DST={f"p{a}{b}+n{c}{d}":p(a,b)+n(c,d) for a,b in OP for c,d in OP if len({a,b,c,d})==4}
def ptree(a,b): return T.Tree((11,5,b,a))
def ntree(a,b): return T.Tree((11,b,5,a))
GATE=[ptree(a,b) for a,b in OP]+[ntree(a,b) for a,b in OP]
GV=[p(a,b) for a,b in OP]+[n(a,b) for a,b in OP]
HV={}
for (a,b) in OP: HV[f"p{a}{b}"]=p(a,b).astype('<i8').tobytes(); HV[f"n{a}{b}"]=n(a,b).astype('<i8').tobytes()
def execute(args):
    name,lab,seeds,lib=args
    donors=None if lib is None else [T.Tree(tuple(q)) for q in lib]
    t=time.monotonic(); att=[]
    for sd in seeds:
        r=T.search((dict(id=name,labels=[int(v) for v in lab]),sd,65536,256,inputs,0.5),donor_library=donors)
        att.append(dict(seed=sd,solved=r['solved'],evaluations=r['evaluations'],solver_tree=r['solver_tree']))
        if r['solved']: break
    return dict(cell=name,arm='R-tree',solved=att[-1]['solved'],evaluations=sum(a['evaluations'] for a in att),
                worker_seconds=time.monotonic()-t,attempts=att)
def check():
    vm=outputs([t.program for t in GATE],inputs,ALPHABET)
    for t,v,w in zip(GATE,GV,vm):
        assert np.array_equal([T.interpret(t,x) for x in inputs],v), t.prefix
        assert np.array_equal(w,v), ("vm",t.prefix)
    print("gate trees verified interp+VM; nodes",len(GATE[0].prefix),"tokens",len(GATE[0].program),flush=True)
    print("sources",len(SRC),len({v.tobytes() for v in SRC.values()}),"dests",len(DST),flush=True)
def sources(builds):
    jobs=[]
    for b in range(builds):
        for i,c in enumerate(SRC):
            for r in range(2):
                base=19380000+b*100000+i*100+r*10
                jobs.append((c,SRC[c],[base+k for k in range(8)],None))
    rows=[]; t=time.time()
    with ProcessPoolExecutor(11) as ex:
        for j,row in zip(jobs,ex.map(execute,jobs)):
            row['build']=(j[2][0]-19380000)//100000; row['repeat']=(j[2][0]//10)%10; rows.append(row)
    pickle.dump(rows,open('probe/src_rows.pkl','wb'))
    for b in range(builds):
        rr=[r for r in rows if r['build']==b]
        print("build",b,"solved",sum(r['solved'] for r in rr),"/",len(rr),"evals",sum(r['evaluations'] for r in rr),
              "first",sum(r['attempts'][0]['solved'] for r in rr),"worker-s",round(sum(r['worker_seconds'] for r in rr),1),flush=True)
    ev=[r['evaluations'] for r in rows]; print("per-job evals median",np.median(ev),"mean",np.mean(ev),"max",max(ev),"wall",round(time.time()-t,1),flush=True)
if __name__=="__main__":
    check()
    if sys.argv[1]=="src": sources(int(sys.argv[2]))
