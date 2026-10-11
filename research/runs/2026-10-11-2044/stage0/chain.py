import sys,pickle,collections; sys.path.insert(0,'probe')
from sg import *
def ch(a,b,c,d): return p(a,b)+n(b,c)+p(c,d)
CELLS=sys.argv[1].split(','); reps=int(sys.argv[2])
DC={c:ch(int(c[1]),int(c[2]),int(c[6]),int(c[10])) for c in CELLS}
for c in CELLS: assert c[2]==c[5] and c[6]==c[9]
if __name__=='__main__':
    libs={'R-tree':None,'R-gate':[list(t.prefix) for t in GATE]}
    for b in (0,1): libs[f'R-all{b}']=[e['prefix'] for e in pickle.load(open(f'probe/lib{b}.pkl','rb'))['semantic']]
    jobs=[]
    for ci,c in enumerate(CELLS):
        for r in range(reps):
            base=20440000+ci*1000+r*10
            for arm,lib in libs.items(): jobs.append((arm,(c,DC[c],[base+k for k in range(8)],lib)))
    t=time.time(); res=collections.defaultdict(list)
    with ProcessPoolExecutor(11) as ex:
        for (arm,j),row in zip(jobs,ex.map(execute,[j for _,j in jobs])):
            res[arm].append(row)
    for arm,rr in res.items():
        print(arm,"solved",sum(r['solved'] for r in rr),"/",len(rr),"first",sum(r['attempts'][0]['solved'] for r in rr),
          "attempts",[len(r['attempts']) for r in rr],
          "mean evals",int(np.mean([r['evaluations'] for r in rr])),"median",int(np.median([r['evaluations'] for r in rr])),
          "worker-s mean",round(np.mean([r['worker_seconds'] for r in rr]),1),"max",round(max(r['worker_seconds'] for r in rr),1))
        print("   per-cell",[ (c,int(np.mean([r['evaluations'] for r in rr if r['cell']==c]))) for c in CELLS])
    print("wall",round(time.time()-t,1))
    pickle.dump(dict(res),open('probe/chain_rows.pkl','wb'))
