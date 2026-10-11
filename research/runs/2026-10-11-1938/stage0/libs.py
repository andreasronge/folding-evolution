import sys,pickle,collections; sys.path.insert(0,'probe')
from sg import *
for b in (0,1):
    out=pickle.load(open(f'probe/lib{b}.pkl','rb'))
    sem=out['semantic']; d=out['helper_diagnostics']
    inc=[h for h,v in d.items() if v['semantic']['included']]
    rec=[h for h,v in d.items() if v['semantic']['recurrent']]
    print("build",b,"entries",len(sem),"nodes",collections.Counter(e['nodes'] for e in sem) if False else sorted(e['nodes'] for e in sem))
    print("  helpers included",len(inc),sorted(inc),"recurrent",len(rec))
    # coverage: dest cells whose both / one needed helper in library
    both=sum(1 for k in DST if k[:3] in inc and k[4:] in inc); one=sum(1 for k in DST if (k[:3] in inc) or (k[4:] in inc))
    print("  dest coverage both",both,"/24 at least one",one,"/24")
    import collections as C
    vecs=[np.array([T.interpret(T.Tree(tuple(e['prefix'])),x) for x in inputs]) for e in sem]
    ins=[sorted({o for o in e['prefix'] if o<4}) for e in sem]
    print("  entry input-sets",C.Counter(len(i) for i in ins))
    print("  acq evals",out['acquisition_evaluations'],"worker-s",round(out['acquisition_worker_seconds'],1))
