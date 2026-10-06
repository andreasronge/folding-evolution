import json, collections, math
import numpy as np
from scipy.stats import t as tdist, pearsonr, spearmanr
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D='/Users/andreas/developer/folding-evolution/research/runs/2026-10-06-1425'
O='/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-1425-saved-map-shape-shift'
rc=json.load(open(D+'/recompute.json')); C={tuple(k.split('|')):v for k,v in rc['C'].items()}; grp=rc['grp']; old=rc['old_a']
res=json.load(open(O+'/result.json')); ifgt=res['IF_GT_frequencies']
def ival(v):
    v=np.array(v); m=v.mean(); h=tdist.ppf(0.975,5)*v.std(ddof=1)/math.sqrt(6); return m,h
# family means a vs b, and vs starts
print('Family group costs (mean over 6 starts) BE / LIN:')
for fam in ('M','M+','R','R_abl','R_fm'):
    for s in ('a','b'):
        if fam=='M' and s=='b': continue
        names=[f'M{i}' for i in range(1,7)] if fam=='M' else [f'{fam}{i}{s}' for i in range(1,7)]
        print(f"{fam:6}{s if fam!='M' else ' '} BE {np.mean([grp[n]['BE'] for n in names]):.3f}  LIN {np.mean([grp[n]['LIN'] for n in names]):.3f}")
print('G BE',round(grp['G']['BE'],3),'LIN',round(grp['G']['LIN'],3))
# within-family a-b difference per start (log2, positive => a cheaper)
print('\nPer-start a−b group-cost difference (positive = b costlier than a), BE | LIN:')
for fam in ('M+','R','R_abl','R_fm'):
    be=[grp[f'{fam}{i}b']['BE']-grp[f'{fam}{i}a']['BE'] for i in range(1,7)]
    lin=[grp[f'{fam}{i}b']['LIN']-grp[f'{fam}{i}a']['LIN'] for i in range(1,7)]
    m1,h1=ival(be); m2,h2=ival(lin)
    print(f"{fam:6} BE {m1:+.3f} ±{h1:.3f} (per start {' '.join(f'{x:+.2f}' for x in be)}) | LIN {m2:+.3f} ±{h2:.3f} ({' '.join(f'{x:+.2f}' for x in lin)})")
# vs start M: continuation gains on BE and LIN (M/M+ and M/R), both letters
print('\nContinuation effect vs its M start, log2 (positive = continuation faster):')
for fam in ('M+','R','R_fm'):
    for s in ('a','b'):
        be=[grp[f'M{i}']['BE']-grp[f'{fam}{i}{s}']['BE'] for i in range(1,7)]
        lin=[grp[f'M{i}']['LIN']-grp[f'{fam}{i}{s}']['LIN'] for i in range(1,7)]
        m1,h1=ival(be); m2,h2=ival(lin)
        print(f"{fam:5}{s} BE {2**m1:.3f} [{2**(m1-h1):.2f},{2**(m1+h1):.2f}]  LIN {2**m2:.3f} [{2**(m2-h2):.2f},{2**(m2+h2):.2f}]")
# IF_GT covariate
print('\nIF_GT: pair, M+, R, diff, shift(R/M+ log2)')
xs=[];ys=[]
for i in range(1,7):
    for s in 'ab':
        p=f'{i}{s}'; d=ifgt[f'R{p}']-ifgt[f'M+{p}']; sh=C[(p,'R/M+')]['shift']; xs.append(d); ys.append(sh)
        print(p, f"{ifgt[f'M+{p}']:.3f} {ifgt[f'R{p}']:.3f} {d:+.3f} {sh:+.3f}")
print('pearson',pearsonr(xs,ys),'spearman',spearmanr(xs,ys))
# BE R/M+ vs IF_GT diff
ys2=[C[(f'{i}{s}','R/M+')]['BE'] for i in range(1,7) for s in 'ab']
print('BE vs IFGT diff pearson',pearsonr(xs,ys2))
# IF_GT level vs BE cost across all learned maps
names=[n for n in grp if n not in ('G',) and not (n.startswith('M') and len(n)==2)]
print('IF_GT vs BE cost across', len(names),'learned maps: pearson',pearsonr([ifgt[n] for n in names],[grp[n]['BE'] for n in names]))
print('IF_GT vs LIN cost: pearson',pearsonr([ifgt[n] for n in names],[grp[n]['LIN'] for n in names]))

# ---- plots
fig,axes=plt.subplots(1,3,figsize=(13,4.2),sharey=False)
cols={'a':'#c0392b','b':'#2471a3'}
for ax,g in zip(axes,('BE','LIN','shift')):
    for j,s in enumerate('ab'):
        v=[C[(f'{i}{s}','R/M+')][g] for i in range(1,7)]
        ax.scatter(np.arange(1,7)+(j-0.5)*0.15, v, color=cols[s], label=f'"{s}" continuations (fresh seeds)', zorder=3)
        m,h=ival(v); ax.axhspan(m-h,m+h,color=cols[s],alpha=0.12); ax.axhline(m,color=cols[s],lw=1)
    idx={'BE':0,'LIN':1,'shift':2}[g]
    ax.scatter(np.arange(1,7)-0.25,[o[idx] for o in old],marker='x',color='#7f8c8d',label='"a" on 0811 seeds',zorder=3)
    ax.axhline(0,color='k',lw=0.8,ls='--'); ax.set_title(f'log2 R/M+ {g}'); ax.set_xlabel('M start'); ax.set_xticks(range(1,7))
axes[0].set_ylabel('log2 ratio (>0: R faster)'); axes[2].legend(fontsize=7,loc='lower left')
fig.suptitle('R vs M+ per start: the "a" pattern repeats on fresh seeds; the "b" continuations show the opposite shift'); fig.tight_layout()
fig.savefig(D+'/per_start_R_over_Mplus.png',dpi=130)

fig,axes=plt.subplots(1,3,figsize=(13,4.2))
for ax,lab in zip(axes,('R/R_fm','R/R_abl','R_fm/M+')):
    for j,s in enumerate('ab'):
        for k,g in enumerate(('BE','LIN','shift')):
            v=[C[(f'{i}{s}',lab)][g] for i in range(1,7)]
            m,h=ival(v)
            ax.errorbar(k+(j-0.5)*0.25, m, yerr=h, fmt='o', color=cols[s], capsize=4, label=f'"{s}"' if k==0 else None)
            ax.scatter([k+(j-0.5)*0.25]*6, v, color=cols[s], alpha=0.35, s=12)
    ax.axhline(0,color='k',lw=0.8,ls='--'); ax.set_xticks(range(3)); ax.set_xticklabels(['BE','LIN','shift']); ax.set_title(f'log2 {lab}')
axes[0].set_ylabel('log2 ratio, mean ± 95% t (df 5)'); axes[0].legend(fontsize=8)
fig.suptitle('Dependency contrasts by continuation letter (b-only is the unselected set)'); fig.tight_layout()
fig.savefig(D+'/dependency_by_letter.png',dpi=130)

fig,ax=plt.subplots(figsize=(5.5,4.2))
for i in range(1,7):
    for s in 'ab':
        p=f'{i}{s}'; ax.scatter(ifgt[f'R{p}']-ifgt[f'M+{p}'], C[(p,'R/M+')]['shift'], color=cols[s]); ax.annotate(p,(ifgt[f'R{p}']-ifgt[f'M+{p}'], C[(p,'R/M+')]['shift']),fontsize=7,xytext=(3,3),textcoords='offset points')
ax.axhline(0,color='k',lw=0.8,ls='--'); ax.axvline(0,color='k',lw=0.8,ls='--')
ax.set_xlabel('IF_GT emitted frequency, R − M+'); ax.set_ylabel('log2 shift R/M+ (BE ratio ÷ LIN ratio)'); ax.set_title('Shift vs IF_GT frequency difference')
fig.tight_layout(); fig.savefig(D+'/shift_vs_ifgt.png',dpi=130)
print('plots written')
