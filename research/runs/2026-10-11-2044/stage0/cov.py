import sys,json; sys.path.insert(0,'probe')
from sg import *
L=json.load(open('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1938-prepare/libraries.json'))
key=sys.argv[1]
inv={v:k for k,v in HV.items()}
cells=[f"p{a}{b}+n{b}{c}+p{c}{d}" for a,b,c,d in itertools.permutations(range(4))]
tot=collections.Counter(); hs=[]
for lib in L:
    have=set()
    for e in lib[key]:
        v=np.array([T.interpret(T.Tree(tuple(e['prefix'])),x) for x in inputs]).astype('<i8').tobytes()
        if v in inv: have.add(inv[v])
    hs.append(len(have))
    for c in cells:
        need={c[0:3],c[4:7],c[8:11]}; tot[len(need&have)]+=1
print(key,"entries",np.mean([len(l[key]) for l in L]),"helpers/24 mean",np.mean(hs),"needed-helper coverage (count of 3 needed: share of build x cell)",{k:round(v/sum(tot.values()),3) for k,v in sorted(tot.items())})
