import json, itertools, re
scr = json.load(open("/tmp/probe/roster_screen.json"))
probed = {"BE:F>S?F:M+m","BE:F>S?m:M+M","BE:F>m?S:F+M","BE:M>F?S:F+m","BE:S>F?M:F+m","BE:S>F?m:M+S",
"PA:(F>S?F:m)+M","PA:(F>S?m:M)+F","PA:(F>m?M:S)+m","PA:(M>F?F:m)+S","PA:(M>F?m:S)+S","PA:(S>F?M:m)+m"}
def roles(cid):
    fam, b = cid[:2], cid[3:]
    if fam == "BE":
        A,B,C,D,E = b[0],b[2],b[4],b[6],b[8]
        return {("A",A),("B",B),("C",C),("sum",D),("sum",E)}
    A,B,C,D,E = b[1],b[3],b[5],b[7],b[10]
    return {("A",A),("B",B),("C",C),("D",D),("E",E)}
for fam in ("BE","PA"):
    ret = [sorted(c["ids"])[0] for c in scr if c["fam"]==fam and c["retained"]]
    ret.sort()
    tr_pool = [c for c in ret if c in probed]
    ho_pool = [c for c in ret if c not in probed]
    best=None; n=0
    for k in (4,5,6):
        for tr in itertools.combinations(tr_pool, k):
            cov = set().union(*map(roles,tr))
            ok = [h for h in ho_pool if roles(h) <= cov]
            if len(ok) >= 4:
                n+=1
                if best is None or len(ok)>best[2]: best=(k,tr,len(ok))
        if best: break
    print(fam, "retained", len(ret), "unprobed", len(ho_pool), "best", best, "n splits", n)
    # also distribution of agree for retained
    ag = sorted(c["agree"] for c in scr if c["fam"]==fam and c["retained"])
    print("  agree range", round(ag[0],3), round(ag[len(ag)//2],3), round(ag[-1],3))
    ex=[c for c in scr if c["fam"]==fam and not c["retained"]]
    print("  excluded", len(ex))
from collections import Counter
TR = {"BE": ('BE:F>S?F:M+m', 'BE:F>m?S:F+M', 'BE:S>F?M:F+m', 'BE:S>F?m:M+S'),
      "PA": ('PA:(F>S?F:m)+M', 'PA:(F>S?m:M)+F', 'PA:(M>F?m:S)+S', 'PA:(S>F?M:m)+m')}
for fam in ("BE","PA"):
    ret = sorted(sorted(c["ids"])[0] for c in scr if c["fam"]==fam and c["retained"])
    cov = set().union(*map(roles, TR[fam]))
    cand = [h for h in ret if h not in probed and roles(h) <= cov]
    rep = lambda c: [k for k,v in Counter(ch for ch in c[3:] if ch in "SMmF").items() if v==2][0]
    print(fam, len(cand), Counter(rep(c) for c in cand))
