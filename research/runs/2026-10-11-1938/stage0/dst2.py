import sys,pickle,collections,json; sys.path.insert(0,'probe')
from sg import *
if __name__=='__main__':
    cells=sys.argv[1].split(','); reps=int(sys.argv[2])
    L=json.load(open('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1228-score/libraries.json'))
    libs={f'R-order{b}':[e['prefix'] for e in L[b]['semantic_all']] for b in (0,1)}
    print("order lib sizes",[len(v) for v in libs.values()])
    jobs=[]
    for ci,c in enumerate(cells):
        for r in range(reps):
            base=19390000+ci*1000+r*10
            for arm,lib in libs.items(): jobs.append((arm,(c,DST[c],[base+k for k in range(8)],lib)))
    res=collections.defaultdict(list)
    with ProcessPoolExecutor(11) as ex:
        for (arm,j),row in zip(jobs,ex.map(execute,[j for _,j in jobs])): res[arm].append(row)
    for arm,rr in res.items():
        print(arm,"solved",sum(r['solved'] for r in rr),"/",len(rr),"first",sum(r['attempts'][0]['solved'] for r in rr),
          "mean evals",int(np.mean([r['evaluations'] for r in rr])),"median",int(np.median([r['evaluations'] for r in rr])))
