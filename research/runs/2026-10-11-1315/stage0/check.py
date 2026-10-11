import sys; sys.path.insert(0,'probe')
from rs import *
def lo(a,b): return np.where(X[:,a]>X[:,b], X[:,b], X[:,a])
if __name__=="__main__":
    print("X range",X.min(),X.max(), "pos01+X2 range", SRC['pos01+X2'].min(), SRC['pos01+X2'].max())
    t=T.Tree((9,11,5,9,0,1,9,0,1,2)); print("hand source tree tokens",len(t.program), np.array_equal([T.interpret(t,x) for x in inputs],SRC['pos01+X2']))
    jobs=[("lo01+X2",lo(0,1)+X[:,2],[5000+i],None) for i in range(4)]
    jobs+=[("pos01+X2",SRC['pos01+X2'],[5100+i],[list(t.prefix) for t in RECT]) for i in range(4)]
    jobs+=[("neg23+X0",SRC['neg23+X0'],[5200+i],[list(t.prefix) for t in RECT]) for i in range(4)]
    with ProcessPoolExecutor(11) as ex:
        for j,r in zip(jobs,ex.map(execute,jobs)):
            print(j[0], "lib" if j[3] else "tree", r['solved'], r['evaluations'], round(r['worker_seconds'],1))
