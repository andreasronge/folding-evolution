import json, numpy as np
R=24000; FLOOR=250
cor=json.load(open('/tmp/posprobe/corpora.json'))
def P_of(t): return np.diff(np.asarray(t,float),prepend=0,axis=1)/R
def posmarg(p):
    m=[p[24].copy()]
    for _ in range(31): m.append(m[-1]@p[:24])
    return np.array(m)
def quant(row):
    # floor + largest remainder, simple
    c=np.maximum(np.floor(row*R),FLOOR); 
    while c.sum()>R: i=np.argmax(np.where(c>FLOOR,c,0)); c[i]-=1
    rem=row*R-c; 
    while c.sum()<R: i=np.argmax(rem); c[i]+=1; rem[i]-=1
    return c/R
g4=None
res=[]
for name,rec in cor.items():
    C=P_of(rec['tables']['C']); K=P_of(rec['tables']['K']); T=P_of(rec['tables']['T'])
    if g4 is None:
        pass
    mC=posmarg(C); mK=posmarg(K)
    # G4 baseline: recover from K? need G4; approximate G4 from T via ratio not possible; use K as template (G4 x multipliers) - same column structure
    G=K  # K = G4*w normalized per row; reweighting K columns spans same family as G4 columns (up to floor)
    # Build Q: per position multipliers on template columns, match mC[j] given propagated Qmarg
    prev=None; Qerr=[]; Qrows=[]
    m_prev=None
    for j in range(32):
        target=mC[j]
        rows = G[24:25] if j==0 else G[:24]
        w_prev = np.array([1.0]) if j==0 else m_prev
        lw=np.zeros(24)
        for _ in range(2000):
            q=rows*np.exp(lw); q/=q.sum(1,keepdims=True)
            q=np.array([quant(r) for r in q]) if _==1999 else q
            em=w_prev@q
            if _<1999: lw+=0.7*(np.log(target)-np.log(em))
        Qerr.append(np.abs(em-target).max()); m_prev=em
        Qrows.append(q.min())
    Pq=np.array([quant(r) for r in mC]); Perr=np.abs(Pq-mC).max()
    tv0=0.5*np.abs(mC[0]-mK[0]).sum(); tvm=np.mean(0.5*np.abs(mC-mK).sum(1))
    res.append((name,max(Qerr),min(Qrows)*R,Perr,Pq.min()*R,tv0,tvm))
for r in res: print('%s Qmaxerr=%.2e Qminwidth=%.0f Pmaxerr=%.2e Pminwidth=%.0f TV0(C,K)=%.3f TVmean=%.4f'%r)

print('--- dependence and mutation cascade')
rng=np.random.default_rng(0)
def build_Q(G,mC):
    Qs=[];m_prev=None
    for j in range(32):
        rows = G[24:25] if j==0 else G[:24]; w_prev=np.array([1.0]) if j==0 else m_prev
        lw=np.zeros(24)
        for _ in range(3000):
            q=rows*np.exp(lw); q/=q.sum(1,keepdims=True); em=w_prev@q
            lw+=0.7*(np.log(mC[j])-np.log(em))
        Qs.append(q); m_prev=em
    return Qs
def kl(a,b): return (a*np.log2(a/b)).sum(-1)
def decode(al, rowfn):
    out=np.empty(al.shape,dtype=int); prev=np.full(len(al),24)
    for j in range(32):
        cdf=rowfn(j)  # (25,24) cumulative probs
        u=al[:,j]
        out[:,j]=np.minimum((u[:,None] >= cdf[prev]).sum(1),23)
        prev=out[:,j]
    return out
for name in ['BE1','PA3','BE7','PA8']:
    rec=cor[name]; C=P_of(rec['tables']['C']); K=P_of(rec['tables']['K'])
    mC=posmarg(C); Qs=build_Q(K,mC)
    # float fit error
    m=None; err=0
    for j,q in enumerate(Qs):
        em = q[0] if j==0 else m@q; err=max(err,np.abs(em-mC[j]).max()); m=em
    # conditional KL C vs Q (bits/transition), C vs K, MI of C
    klQ=np.mean([mC[j-1]@kl(C[:24],Qs[j]) for j in range(1,32)])
    klK=np.mean([mC[j-1]@kl(C[:24],K[:24]) for j in range(1,32)])
    miC=np.mean([mC[j-1]@kl(C[:24],mC[j][None,:]) for j in range(1,32)])
    # cascade
    N=4000; al=rng.random((N,32))
    def cdfC(j): return np.cumsum(C,1)
    def cdfQ(j):
        q=Qs[j]; full=np.vstack([q,q[:1]]) if j>0 else np.repeat(q,25,0)
        return np.cumsum(full,1)
    cdfP_=np.cumsum(mC,1)
    def cdfP(j): return np.repeat(cdfP_[j][None,:],25,0)
    al2=al.copy(); pos=rng.integers(0,32,N); al2[np.arange(N),pos]=rng.random(N)
    casc={}
    for nm,f in [('C',cdfC),('Q',cdfQ),('P',cdfP)]:
        a=decode(al,f); b=decode(al2,f); casc[nm]=(a!=b).sum(1).mean()
    print(name,'Qfloaterr=%.1e KL(C||Q)=%.3f KL(C||K)=%.3f MI_C=%.3f bits/trans; tokens changed per point mutation C=%.2f Q=%.2f P=%.2f'%(err,klQ,klK,miC,casc['C'],casc['Q'],casc['P']))
