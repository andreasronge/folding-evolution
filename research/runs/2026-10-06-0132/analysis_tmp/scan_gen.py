import json, collections
import numpy as np
OUT='/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-0132-post-addition-map-learning'
TOK=['NOP','INPUT','CONST_0','CONST_1','CHARS','SUM','ANY','ADD','GT','DUP','SWAP','REDUCE_ADD','SLOT_12','SLOT_13','MAP_EQ_E','CONST_2','CONST_5','IF_GT','REDUCE_MAX','THRESHOLD_SLOT','SEP_A','SEP_B','REDUCE_MIN']
curves=collections.defaultdict(list)
with open(OUT+'/generations.jsonl') as f:
    for line in f:
        r=json.loads(line)
        if r['calibration']: continue
        sc=np.array(r['scores'])
        sel=r['selected_indices']
        curves[r['trajectory']].append(dict(gen=r['generation'],parents_mean=float(sc[:4].mean()),children_mean=float(sc[4:].mean()),best=float(sc.min()),all_mean=float(sc.mean()),
            n_children_selected=int(sum(1 for i in sel if i>=4)),sel_drift=float(np.mean([r['candidates'][i]['l1_drift'] for i in sel])),
            cum_evals=r['cumulative_inner_evaluations'],cum_sec=r['cumulative_seconds'],
            paired_child_minus_parent=float(np.mean([m['paired_difference_mean'] for m in r['mutations']]))))
print("trajectories",sorted(curves),"gens",set(len(v) for v in curves.values()))
# summary per learner: parents_mean at gen 1,5,10,15,20,25
for L in 'CMT':
    print(f"\n== {L}: parents' re-scored mean log2 cost (65k) per generation (gen1 = start map, 4 copies) ==")
    for k in range(1,7):
        c=curves[f'{L}{k}']
        print(f"{L}{k}: "+' '.join(f"{c[g-1]['parents_mean']:5.2f}" for g in (1,2,3,5,8,10,13,15,18,20,23,25)), f"| children selected/gen: {np.mean([x['n_children_selected'] for x in c]):.2f} | final sel drift {c[-1]['sel_drift']:.2f} | child-parent paired mean {np.mean([x['paired_child_minus_parent'] for x in c]):+.3f}")
# final maps
fm=json.load(open(OUT+'/final_maps.json'))
print("\n== final maps ==")
for tid,m in fm.items():
    print(f"{tid}: selected {m['selected_parent_id']:22s} sel scores {[round(s,2) for s in m['selection_scores']]} l1_drift {m['l1_drift']:.3f} adapt_evals {m['adaptation_evaluations']/1e6:.0f}M adapt_s {m['adaptation_seconds']/60:.1f}min")
print("\n== M learned log-multipliers (ln) per token, 6 trajectories ==")
Mv=np.array([fm[f'M{k}']['vector'] for k in range(1,7)])
print(f"{'token':15s}"+''.join(f"{'M%d'%k:>7s}" for k in range(1,7))+"   mean   sign-consistent")
for i,t in enumerate(TOK):
    v=Mv[:,i]; cons = 'all+' if (v>0.25).all() else 'all-' if (v<-0.25).all() else ''
    print(f"{t:15s}"+''.join(f"{x:7.2f}" for x in v)+f"  {v.mean():6.2f}  {cons}")
print("\n== T learned log-weights minus G-marg start, per token ==")
from experiments.chem_tape.assembly_maps import frozen_controls
from experiments.chem_tape.map_learning import initial, table_for
ctl=frozen_controls()
t0=initial('T',ctl); Tv=np.array([fm[f'T{k}']['vector'] for k in range(1,7)])-t0
gm=np.diff(ctl['G-marg'],prepend=0,axis=1)[0]/23000
print(f"{'token':15s}{'Gmarg p':>8s}"+''.join(f"{'T%d'%k:>7s}" for k in range(1,7))+"   mean   sign-consistent")
for i,t in enumerate(TOK):
    v=Tv[:,i]; cons = 'all+' if (v>0.25).all() else 'all-' if (v<-0.25).all() else ''
    print(f"{t:15s}{gm[i]:8.3f}"+''.join(f"{x:7.2f}" for x in v)+f"  {v.mean():6.2f}  {cons}")
# resulting token marginals of M maps vs G: compute marginal under uniform previous? Instead show final table row-mean probability per token
print("\n== mean over 24 rows of token probability: G vs M maps (x1000) ==")
def rowp(table): return np.diff(np.array(table),prepend=0,axis=1)/23000
Gp=rowp(ctl['G']).mean(0)
Mp=np.array([rowp(fm[f'M{k}']['table']).mean(0) for k in range(1,7)])
for i,t in enumerate(TOK):
    print(f"{t:15s} G {Gp[i]*1000:6.1f}  M {' '.join(f'{x*1000:6.1f}' for x in Mp[:,i])}")
# C per-row drift (L1 over probability per row)
print("\n== C maps: per-row L1 prob drift from G (sum over tokens), rows = previous token (0..22) + start row? ==")
Cd=np.array([np.abs(rowp(fm[f'C{k}']['table'])-rowp(ctl['G'])).sum(1) for k in range(1,7)])
for r in range(24):
    print(f"row {r:2d} {TOK[r] if r<23 else 'row23':15s} "+' '.join(f"{x:5.2f}" for x in Cd[:,r])+f"  mean {Cd[:,r].mean():.2f}")
print("C total drift per traj",[round(x,2) for x in Cd.sum(1)], " M total", [round(fm[f'M{k}']['l1_drift'],2) for k in range(1,7)], " T total",[round(fm[f'T{k}']['l1_drift'],2) for k in range(1,7)])
# M vector bound hits
print("M vectors at bound (|v|>=ln16-1e-6):",int((np.abs(Mv)>=np.log(16)-1e-6).sum()), " T:",int((np.abs(Tv)>=np.log(16)-1e-6).sum()))
json.dump(dict(curves=curves,M_vectors=Mv.tolist(),T_delta=Tv.tolist(),C_rowdrift=Cd.tolist()),open('/Users/andreas/developer/folding-evolution/research/runs/2026-10-06-0132/analysis_tmp/gen.json','w'))
