import numpy as np
rng=np.random.default_rng(1)
def cost(q): return 32+42*np.exp(-q/0.104)
def traj(s,u=1/32,p=1/16,f0=1/16,Ne=100,N=256,eps=12,G=64,psolve=0.5,extract='final'):
    f=f0; hist=[]
    for e in range(eps):
        solve_at = 64 if rng.random()>psolve else rng.integers(5,40)
        for g in range(G-1):
            ss = s if g<solve_at else 0.0
            ps = f+ss*f*(1-f)
            rf = rng.binomial(Ne,min(max(ps,0),1))/Ne
            kids = rng.binomial(254,rf)
            # mutation redraw
            redraw_on = rng.binomial(kids, u*(1-p))  # on->off
            redraw_off = rng.binomial(254-kids, u*p) # off->on
            kids = kids - redraw_on + redraw_off
            elite = rng.binomial(2,f)
            f=(kids+elite)/N
            hist.append(f)
    return f, np.mean(hist)
for s in [0,0.02,0.036,0.06]:
    fins=[];avgs=[]
    for i in range(400):
        a,b=traj(s); fins.append(a); avgs.append(b)
    fins=np.array(fins); avgs=np.array(avgs)
    print(f"s={s}: final f mean {fins.mean():.3f} sd {fins.std():.3f} P(f=0) {np.mean(fins==0):.2f} | time-avg {avgs.mean():.3f} | E cost(final) {cost(0.5*fins).mean():.1f}k  cost(q0) {cost(1/32):.1f}k ratio {cost(0.5*fins).mean()/cost(1/32):.3f}  ratio time-avg {cost(0.5*avgs).mean()/cost(1/32):.3f}")
print('--- sensitivity')
for (u,Ne,s) in [(1/32,60,0.036),(1/32,150,0.036),(1/128,100,0.036),(1/128,100,0.06),(1/8,100,0.036),(1/32,100,0.1)]:
    fins=[];avgs=[]
    for i in range(300):
        a,b=traj(s,u=u,Ne=Ne); fins.append(a); avgs.append(b)
    fins=np.array(fins)
    print(f"u={u:.4f} Ne={Ne} s={s}: final mean {fins.mean():.3f} P0 {np.mean(fins==0):.2f} ratio {cost(0.5*fins).mean()/cost(1/32):.3f}")
