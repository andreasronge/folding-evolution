import sys,pickle; sys.path.insert(0,'probe')
from rs import *
rows=pickle.load(open('probe/src_rows.pkl','rb'))
c=collections.Counter(); nodes=[]
for r in rows:
    t=T.Tree(tuple(r['attempts'][-1]['solver_tree'])); nodes.append(len(t.prefix))
    name=r['cell']; f,ab,cc=name[:3],name[3:5],int(name[-1]); a,b=int(ab[0]),int(ab[1])
    s3=(X[:,a]+X[:,b]+X[:,cc]).astype('<i8').tobytes(); s2=s(a,b).astype('<i8').tobytes()
    vals=set()
    for p in range(len(t.prefix)):
        vals.add(np.array([T.interpret(T.Tree(t.prefix[p:t.ends[p]]),x) for x in inputs]).astype('<i8').tobytes())
    own=F[f](a,b).astype('<i8').tobytes()
    c['root IF_GT']+=t.prefix[0]==11; c['has a+b+c']+=s3 in vals; c['has a+b']+=s2 in vals; c['has own helper']+=own in vals
print(len(rows),dict(c),"solver nodes median",np.median(nodes))
