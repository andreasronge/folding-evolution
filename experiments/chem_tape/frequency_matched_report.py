"""0125 complete-roster corpus intervals and capped-endpoint diagnostics."""

from collections import defaultdict
import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import interval, describe, balanced_target_n
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.solver_corpus_report import cost


def route(ck, eligible):
    if not eligible:
        return dict(label='incomplete', meaning='full fixed roster incomplete or error; no efficacy decision')
    low, high = ck['interval_95']
    if low >= 1.20:
        return dict(label='replacement_insufficient', meaning='this G4-based frequency map is insufficient within 20% on these cells')
    if high <= 1.20:
        return dict(label='replacement_adequate', meaning='this G4-based frequency map is adequate within the stated 20% bound on these cells')
    return dict(label='unresolved', meaning='interval crosses 1.20; representation choice unresolved')


def make_report(rows, references, schedule, config, error=None):
    def k(r):
        return tuple(r[x] for x in ('corpus', 'cell', 'seed'))
    expected = {k(r) for r in schedule}
    observed = {k(r): r for r in rows}
    if len(observed) != len(rows) or not set(observed) <= expected or any(r['arm'] != 'K' for r in rows):
        raise ValueError('unexpected or duplicate K observation')
    eligible = not error and len(rows) == 2048 and set(observed) == expected
    report = dict(efficacy_eligible=eligible, full_roster_complete=eligible,
                  searches=len(rows), error=error, scope=config['scope'], sensitivities={},
                  uncertainty_unit='corpus; fixed bank/cells/seeds; n=16, df=15',
                  censoring_caution='capped geometric costs; zero solves is not absence',
                  baseline_interval_limitation='K/G4 unpaired; corpus interval omits independent G4 sampling uncertainty')
    if not eligible:
        report['outcome'] = route({}, False)
        report['partial_K_counts'] = describe(rows)
        return report
    grouped = defaultdict(dict)
    g4 = defaultdict(list)
    for r in references + rows:
        if r['arm'] == 'G4':
            g4[r['cell']].append(r)
        else:
            grouped[k(r)][r['arm']] = r
    if any(set(grouped[x]) != {'C', 'T', 'K'} for x in expected):
        raise ValueError('C/T/K pairing incomplete')
    if any(len(g4[c]) != 16 for _, c, _ in expected):
        raise ValueError('G4 reference incomplete')
    corpora = sorted({r['corpus'] for r in schedule})
    cells = sorted({r['cell'] for r in schedule})

    def contrast(a, b, penalty=2, only_cells=None, both=False):
        scores, occupancy = {}, {}
        for tid in corpora:
            per_cell = []
            occupancy[tid] = {}
            for cid in only_cells or cells:
                pairs = [p for (t, c, _), p in grouped.items() if t == tid and c == cid]
                if both:
                    pairs = [p for p in pairs if p[a]['solved'] and p[b]['solved']]
                occupancy[tid][cid] = len(pairs)
                if pairs:
                    per_cell.append(np.mean([np.log(cost(p[b], penalty)) - np.log(cost(p[a], penalty)) for p in pairs]))
            if per_cell:
                scores[tid] = float(np.mean(per_cell))
        result = interval(list(scores.values()))
        result.update(corpus_scores_log=scores, occupancy=occupancy,
                      per_source_family={f: interval([v for t, v in scores.items() if t.startswith(f)]) for f in ('BE', 'PA')})
        return result

    for penalty in (2, 1):
        ck, ct, kt = [contrast(a, b, penalty) for a, b in (('C', 'K'), ('C', 'T'), ('K', 'T'))]
        logct, logkt = math.log(ct['speed_ratio']), math.log(kt['speed_ratio'])
        report['sensitivities'][f'unsolved_{penalty}cap'] = dict(
            C_K=ck, C_T=ct, K_T=kt,
            descriptive_log_K_T_over_log_C_T=logkt / logct if abs(logct) > 1e-12 else None,
            share_interpretation='descriptive arithmetic, not a fraction caused by order',
            arms={a: describe([r for r in references + rows if r['arm'] == a], penalty) for a in ('C', 'T', 'K', 'G4')},
            per_cell={cid: dict(C_K=contrast('C', 'K', penalty, [cid]),
                                arms={a: describe([r for r in references + rows if r['cell'] == cid and r['arm'] == a], penalty) for a in ('C', 'T', 'K', 'G4')}) for cid in cells},
            K_G4=interval([float(np.mean([
                np.mean([np.log(cost(r, penalty)) for r in g4[cid]])
                - np.mean([np.log(cost(p['K'], penalty)) for (t, c, _), p in grouped.items() if t == tid and c == cid])
                for cid in cells])) for tid in corpora]),
        )
    report['both_solved'] = {name: contrast(a, b, both=True) for name, a, b in (('C_K', 'C', 'K'), ('C_T', 'C', 'T'), ('K_T', 'K', 'T'))}
    report['both_solved_interpretation'] = 'selection-conditioned; occupied cells equally weighted within each corpus; missing cells omitted and occupancy reported'
    primary = report['sensitivities']['unsolved_2cap']['C_K']
    report['outcome'] = route(primary, True)
    report['sizing'] = dict(approximate_only=True,
                            assumption='additional independent corpora with same observed C/K spread, not more seeds; no top-up authorized',
                            corpora_for_10_percent_half_width=balanced_target_n(primary['sd_log'], math.log(1.10), 16),
                            current_half_width_log=primary['half_width_log'])
    return report


def save_report(out, report, rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm in ('C', 'T', 'K', 'G4'):
        selected = [r for r in rows if r['arm'] == arm]
        if not selected:
            continue
        budgets = np.geomspace(256, 524288, 100)
        axes[0].plot(budgets, [np.mean([r['solved'] and r['evaluations'] <= b for r in selected]) for b in budgets], label=arm)
        points = defaultdict(list)
        for r in selected:
            for ev, accuracy, diversity in r['curve']:
                points[ev].append((accuracy, diversity))
        x = sorted(points)
        for ax, i in ((axes[1], 0), (axes[2], 1)):
            ax.plot(x, [np.median([v[i] for v in points[ev]]) for ev in x], label=arm)
    for ax, label in zip(axes, ('Fraction D1331-exact', 'Median correct training cases (active runs)', 'Median behavioural diversity (active runs)')):
        ax.set(xlabel='Evaluations', ylabel=label, xscale='log')
        if ax.lines:
            ax.legend()
    fig.tight_layout()
    fig.savefig(out / 'diagnostics.png', dpi=150)
    plt.close(fig)
    write_json(out, 'result.json', report)
    lines = ['# Frozen frequency-matched replacement', '',
             f"Outcome: {report['outcome']['label']} — {report['outcome']['meaning']}", '',
             report['scope'], '', f"K observations: {report['searches']}/2048. Error: {report['error']}", '',
             '| Unsolved cost | C/K (95% corpus interval) | C/T | K/T |', '|---|---|---|---|']
    for name, val in report['sensitivities'].items():
        lines.append(f"| {name} | {val['C_K']['speed_ratio']} {val['C_K']['interval_95']} | {val['C_T']['speed_ratio']} | {val['K_T']['speed_ratio']} |")
    if report['efficacy_eligible']:
        arms = report['sensitivities']['unsolved_2cap']['arms']
        lines += ['', 'Solve counts: ' + '; '.join(f"{a} {r['solved']}/{r['n']}" for a, r in arms.items()), '',
                  'This decision concerns capped costs on the selected development bank. K retains G4 context. A C/K advantage does not establish fragments or active-order causation.',
                  'Both-solved sensitivities condition on success; per-cell occupancy, family intervals, K/G4 and descriptive log share are in result.json.']
    lines += ['', report['baseline_interval_limitation'], report['censoring_caution']]
    (out / 'report.md').write_text('\n'.join(lines) + '\n')
