import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
TD='/Users/andreas/developer/folding-evolution/research/runs/2026-10-06-0132/'
gen=json.load(open(TD+'analysis_tmp/gen.json')); scan=json.load(open(TD+'analysis_tmp/scan.json'))
COL={'C':'#2a78d6','M':'#eb6834','T':'#1baf7a'}; GREY='#52514e'; MUTED='#9a998f'
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':MUTED,'axes.labelcolor':'#0b0b0b','xtick.color':GREY,'ytick.color':GREY,'axes.grid':True,'grid.color':'#e6e6e2','grid.linewidth':0.6})
# Fig 1: learning curves (parents' re-scored mean) per learner, small multiples
fig,axes=plt.subplots(1,3,figsize=(12,3.6),sharey=True)
G_ref=np.mean([13.856,13.810])
for ax,L in zip(axes,'CMT'):
    for k in range(1,7):
        c=gen['curves'][f'{L}{k}']
        ax.plot([x['gen'] for x in c],[x['parents_mean'] for x in c],color=COL[L],lw=1.4,alpha=0.75)
    ax.axhline(G_ref,color=GREY,lw=1,ls='--'); ax.text(25.3,G_ref,'G (stage 0)',color=GREY,va='center',fontsize=8)
    if L=='T':
        ax.axhline(15.69,color=MUTED,lw=1,ls=':'); ax.text(25.3,15.69,'G-marg\n(start)',color=MUTED,va='center',fontsize=8)
    ax.set_title({'C':'C: full 24×23 table (552 params)','M':'M: 23 token multipliers on G','T':'T: 23 tied token weights'}[L],fontsize=9,color='#0b0b0b',loc='left')
    ax.set_xlabel('outer generation'); ax.set_xlim(1,25)
axes[0].set_ylabel('parents\' mean log2 evals to solve\n(re-scored on fresh seeds, 65k cap; 17 = unsolved)')
fig.suptitle('Learning curves, six trajectories per learner. Each point is the four surviving parents re-scored on that generation\'s 24 fresh training searches.',fontsize=9,x=0.01,ha='left')
fig.tight_layout(); fig.savefig(TD+'learning_curves.png',dpi=150); plt.close(fig)
# Fig 2: forest plot of speed ratios vs G, per trajectory and pooled, per test set
sets=[('training524','fresh training (6 cells × 50 seeds)'),('holdout0524','holdout (S?M:S)+M (100 seeds)'),('holdout1524','holdout (S?M:S)+m (100 seeds)')]
fig,axes=plt.subplots(1,3,figsize=(12,3.8),sharey=True)
for ax,(key,title) in zip(axes,sets):
    y=0; labels=[]; ticks=[]
    for L,ref in [('C','G'),('M','G'),('T','G')]:
        v=scan['contrasts'][f'{key}:{L}/{ref}']
        pr=v['per_traj_ratio']
        ax.scatter(pr,[y]*6,s=28,color=COL[L],zorder=3,edgecolor='white',linewidth=0.8)
        ax.plot([v['lo'],v['hi']],[y-0.45,y-0.45],color=COL[L],lw=2.2,solid_capstyle='round')
        ax.scatter([v['ratio']],[y-0.45],s=40,color=COL[L],marker='D',zorder=4,edgecolor='white',linewidth=0.8)
        ax.text(v['hi']*1.06,y-0.45,f"{v['ratio']:.2f}× [{v['lo']:.2f}, {v['hi']:.2f}]",va='center',fontsize=7.5,color=GREY)
        ticks+= [y,y-0.45]; labels+=[f'{L} per trajectory','pooled, 95% CI']
        y-=1.4
    ax.axvline(1,color=GREY,lw=1); ax.axvline(1.5,color=MUTED,lw=1,ls=':')
    ax.set_xscale('log'); ax.set_xlim(0.25,6); ax.set_xticks([0.25,0.5,1,1.5,2,3,4]); ax.set_xticklabels(['0.25','0.5','1','1.5','2','3','4'])
    ax.set_title(title,fontsize=9,loc='left',color='#0b0b0b'); ax.set_xlabel('speed ratio vs frozen G (>1 = learned map faster)')
    ax.set_yticks(ticks); ax.set_yticklabels(labels,fontsize=7.5)
fig.suptitle('Learned maps against the frozen G start at the 524k test cap. Dotted line = 1.5× practical-effect threshold.',fontsize=9,x=0.01,ha='left')
fig.tight_layout(); fig.savefig(TD+'ratios_vs_G.png',dpi=150); plt.close(fig)
# Fig 3: M multipliers per token (dot plot), tokens sorted by mean
TOK=['NOP','INPUT','CONST_0','CONST_1','CHARS','SUM','ANY','ADD','GT','DUP','SWAP','REDUCE_ADD','SLOT_12','SLOT_13','MAP_EQ_E','CONST_2','CONST_5','IF_GT','REDUCE_MAX','THRESHOLD_SLOT','SEP_A','SEP_B','REDUCE_MIN']
Mv=np.array(gen['M_vectors']); Tv=np.array(gen['T_delta'])
fig,axes=plt.subplots(1,2,figsize=(11,5.2),sharey=True)
order=np.argsort(Mv.mean(0))
for ax,(V,L,title) in zip(axes,[(Mv,'M','M: learned log-multiplier on G\'s column, per token'),(Tv,'T','T: learned log-weight change from G-marg, per token')]):
    for yi,i in enumerate(order):
        ax.scatter(V[:,i]/np.log(2),[yi]*6,s=26,color=COL[L],alpha=0.7,edgecolor='white',linewidth=0.6,zorder=3)
        ax.scatter([V[:,i].mean()/np.log(2)],[yi],s=46,color=COL[L],marker='D',edgecolor='white',linewidth=0.8,zorder=4)
    ax.axvline(0,color=GREY,lw=1); ax.set_yticks(range(23)); ax.set_yticklabels([TOK[i] for i in order],fontsize=8)
    ax.set_xlabel('log2 weight change (6 dots = trajectories, diamond = mean)'); ax.set_title(title,fontsize=9,loc='left',color='#0b0b0b')
    ax.set_xlim(-4.2,4.2)
fig.suptitle('What the token-level learners changed. Tokens sorted by M\'s mean change.',fontsize=9,x=0.01,ha='left')
fig.tight_layout(); fig.savefig(TD+'learned_token_weights.png',dpi=150); plt.close(fig)
print('plots written')
