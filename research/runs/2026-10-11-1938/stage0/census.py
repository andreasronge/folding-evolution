import sys,pickle,collections; sys.path.insert(0,'probe')
from sg import *
rows=pickle.load(open('probe/src_rows.pkl','rb'))
c=collections.Counter(); nodes=[]; ownsz=[]
for r in rows:
    t=T.Tree(tuple(r['attempts'][-1]['solver_tree'])); nodes.append(len(t.prefix))
    name=r['cell']; f=name[0]; a,b=int(name[1]),int(name[2]); cc=int(name[-1])
    vals={}
    for q in range(1,len(t.prefix)):
        sub=T.Tree(t.prefix[q:t.ends[q]])
        vals.setdefault(np.array([T.interpret(sub,x) for x in inputs]).astype('<i8').tobytes(),[]).append(len(sub.prefix))
    own=F[f](a,b).astype('<i8').tobytes()
    c['root IF_GT']+=t.prefix[0]==11; c['root ADD']+=t.prefix[0]==9
    c['has own helper']+=own in vals; c['own emittable 3-9']+= own in vals and any(3<=s<=9 for s in vals[own])
    c['has 2Xc']+=(2*X[:,cc]).astype('<i8').tobytes() in vals
    c['has Xb+2Xc']+=(X[:,b]+2*X[:,cc]).astype('<i8').tobytes() in vals
    c['any gate helper']+=any(v in vals for v in HV.values())
    if own in vals: ownsz.append(min(vals[own]))
print(len(rows),dict(c),"solver nodes median",np.median(nodes),"own-helper min sizes",collections.Counter(ownsz))
src=set(SRC)
for b in sorted({r['build'] for r in rows}):
    rr=[r for r in rows if r['build']==b]
    out=OL.build(rr,src,inputs,cap=None,diagnostic_vectors=HV)
    lib=out['semantic'] if 'semantic' in out else out
    ents=out.get('entries') if isinstance(out,dict) and 'entries' in out else None
    print("build",b,"keys",list(out.keys())[:10])
    pickle.dump(out,open(f'probe/lib{b}.pkl','wb'))
