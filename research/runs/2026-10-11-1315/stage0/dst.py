import sys, time, json, pickle
sys.path.insert(0,'probe')
from rs import *
from experiments.chem_tape import order_library
if __name__=="__main__":
    rows=pickle.load(open('probe/src_rows.pkl','rb'))
    builds=sorted({r['build'] for r in rows})
    libs={}
    for b in builds:
        rr=[r for r in rows if r['build']==b]
        lib=order_library.build(rr,set(SRC),inputs,cap=None)['semantic']
        names=[]
        for e in lib:
            v=np.array([T.interpret(T.Tree(tuple(e['prefix'])),x) for x in inputs]).astype('<i8').tobytes()
            names.append(HV.get(v))
        hl=[n for n in names if n]
        print(f"build {b}: R-all entries {len(lib)}, rect helpers {len(hl)} {sorted(hl)}; sizes {collections.Counter(e['nodes'] for e in lib)}")
        libs[f"R-all{b}"]=[e['prefix'] for e in lib]
        # census of own helper in solvers
        own=0; anyh=0; sizes=collections.Counter()
        for r in rr:
            if not r['solved']: continue
            t=T.Tree(tuple(r['attempts'][-1]['solver_tree'])); f=set()
            for p in range(len(t.prefix)):
                sub=T.Tree(t.prefix[p:t.ends[p]]); v=np.array([T.interpret(sub,x) for x in inputs]).astype('<i8').tobytes()
                if v in HV: f.add(HV[v]); sizes[len(sub.prefix)]+=1
            anyh+=bool(f); own+= r['cell'].split('+')[0] in f
        print("   census: solvers with any helper",anyh,"own helper",own,"helper subtree sizes",sorted(sizes.items()))
    old=json.load(open('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1228-prepare/libraries.json'))
    libs["R-order-all0"]=[e['prefix'] for e in old[0]['semantic_all']]
    libs["R-rect"]=[list(t.prefix) for t in RECT]
    libs["R-tree"]=None
    dsts=sys.argv[1].split(',')
    nrep=int(sys.argv[2]); t=time.time()
    jobs=[(d,DST[d],[90000+i*100+r*10+k for k in range(8)],lib) for i,d in enumerate(dsts) for r in range(nrep) for arm,lib in libs.items()]
    arms=[arm for i,d in enumerate(dsts) for r in range(nrep) for arm in libs]
    out=collections.defaultdict(list)
    with ProcessPoolExecutor(11) as ex:
        for arm,j,row in zip(arms,jobs,ex.map(execute,jobs)):
            out[arm].append((j[0],row['solved'],row['evaluations'],len(row['attempts']),round(row['worker_seconds'],1)))
    for arm,v in out.items():
        ev=[x[2] for x in v]
        print(arm,"solved",sum(x[1] for x in v),"/",len(v),"mean",int(np.mean(ev)),"geo",int(np.exp(np.mean(np.log(ev)))),"first",sum(x[3]==1 and x[1] for x in v),"ws",round(sum(x[4] for x in v),1))
        print("   ",[(x[0][:13],x[2]) for x in v])
    print("wall",round(time.time()-t,1))
