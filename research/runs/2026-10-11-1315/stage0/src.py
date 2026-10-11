import sys, time, json, pickle
sys.path.insert(0,'probe')
from rs import *
if __name__=="__main__":
    builds=int(sys.argv[1]); t=time.time()
    jobs=[]
    for b in range(builds):
        for i,c in enumerate(SRC):
            for r in range(2):
                base=70000+b*10000+i*100+r*10
                jobs.append((c,SRC[c],[base+k for k in range(8)],None))
    rows=[]
    with ProcessPoolExecutor(11) as ex:
        for j,row in zip(jobs,ex.map(execute,jobs)):
            row['build']=(j[2][0]-70000)//10000; row['repeat']=(j[2][0]//10)%10; rows.append(row)
    pickle.dump(rows,open('probe/src_rows.pkl','wb'))
    import numpy as np
    for b in range(builds):
        rr=[r for r in rows if r['build']==b]
        print("build",b,"solved",sum(r['solved'] for r in rr),"/",len(rr),"evals",sum(r['evaluations'] for r in rr),
              "first-attempt",sum(r['attempts'][0]['solved'] for r in rr),"worker-s",round(sum(r['worker_seconds'] for r in rr),1))
    ev=[r['evaluations'] for r in rows]; print("per-job evals median",np.median(ev),"mean",np.mean(ev),"max",max(ev))
    print("wall",round(time.time()-t,1))
