import json, time, sys
from pathlib import Path
from experiments.chem_tape import inherited_bias as ib
A = Path("/Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-0918-acquisition/acquisition/main")
def main():
    jobs = []
    for fam, arm, reps in [("max","inherited",[0,1,2]),("max","broken",[0,1]),("sum","inherited",[0]),("sum","broken",[0])]:
        for rep in reps:
            r = json.load(open(A/fam/arm/f"{rep}.json"))
            for th in ("1","5"):
                for idx in (1000,1001):
                    j = ib.frozen_job(fam+th, f"{arm}/{rep}", r["probs"], idx, phase="probe")
                    j["seconds"] = 480
                    jobs.append(j)
    t=time.monotonic()
    rows = ib.parallel(ib.score, jobs, workers=10)
    print("WALL", time.monotonic()-t)
    json.dump(rows, open("/tmp/ib-probe-out/rows.json","w"), default=str)
if __name__=="__main__":
    main()
