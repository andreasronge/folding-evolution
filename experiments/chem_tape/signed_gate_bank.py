"""1938 performance-blind signed-gate bank; canonical trees validate labels only."""

import hashlib
import itertools
import json
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.four_reducer_bank import EXECUTABLE
from experiments.chem_tape.independent_input_bank import ALPHABET, XMachine, semantic_outputs
from experiments.chem_tape.order_bank import old_banks
from experiments.chem_tape.rectified_bank import executable_check
from experiments.chem_tape.tree_gp_search import Tree, interpret, random_tree
from experiments.chem_tape.tree_gp_validate import python_output

BANK = 'x4-signed-gate-v1'
SEEN = ('O:p01+n23', 'O:p12+n30', 'O:p23+n01', 'O:p31+n02')


def helper(kind, a, b):
    if kind not in ('p', 'n') or not (0 <= a < 4 and 0 <= b < 4 and a != b):
        raise ValueError('invalid signed helper')
    # IF_GT children are else, then, condition; zero takes the else branch.
    return Tree((11, 5, b, a) if kind == 'p' else (11, b, 5, a))


def roster():
    xs = np.asarray(inputs_for('D625'))
    cells = []

    def emit(cid, shape, tree, labels, helpers):
        labels = labels.astype('<i8')
        cells.append(dict(id=cid, shape=shape, canonical_tree=list(tree.prefix),
                          canonical=list(tree.program), labels=labels.tolist(),
                          label_hash=hashlib.sha256(labels.tobytes()).hexdigest(), helpers=helpers))

    for kind in ('p', 'n'):
        for a, b in itertools.permutations(range(4), 2):
            labels = np.where(xs[:, a] > 0, xs[:, b], 0) if kind == 'p' else np.where(xs[:, a] > 0, 0, xs[:, b])
            for c in sorted(set(range(4)) - {a, b}):
                emit(f'S:{kind}{a}{b}+2X{c}', 'source',
                     Tree((9,) + helper(kind, a, b).prefix + (9, c, c)),
                     labels + xs[:, c] + xs[:, c], [f'{kind}{a}{b}'])
    for a, b, c, d in itertools.permutations(range(4)):
        emit(f'O:p{a}{b}+n{c}{d}', 'destination',
             Tree((9,) + helper('p', a, b).prefix + helper('n', c, d).prefix),
             np.where(xs[:, a] > 0, xs[:, b], 0) + np.where(xs[:, c] > 0, 0, xs[:, d]),
             [f'p{a}{b}', f'n{c}{d}'])
    return sorted(cells, key=lambda c: (c['label_hash'], c['id']))


def verify(cells):
    inputs = inputs_for('D625')
    for cell in cells:
        tree = Tree(tuple(cell['canonical_tree']))
        if (len(tree.prefix) != (8 if cell['shape'] == 'source' else 9)
                or len(tree.program) != (12 if cell['shape'] == 'source' else 13)
                or list(tree.program) != cell['canonical']
                or hashlib.sha256(np.asarray(cell['labels'], dtype='<i8').tobytes()).hexdigest() != cell['label_hash']):
            raise ValueError('signed-gate canonical/hash changed')
        if ([interpret(tree, x) for x in inputs] != cell['labels']
                or [python_output(tree, x) for x in inputs] != cell['labels']
                or outputs([tree.program], inputs, ALPHABET)[0].tolist() != cell['labels']):
            raise ValueError('signed-gate interpreter/Python/VM disagreement')
        if 'witness' in cell:
            witness = outputs([cell['witness']], inputs, ALPHABET)
            if (not np.array_equal(witness, semantic_outputs([cell['witness']], inputs))
                    or int(np.count_nonzero(witness[0] == cell['labels'])) != cell['best_matches']):
                raise ValueError('alias witness semantics changed')
    return dict(passed=True, cells=len(cells), protected_searches=0)


def executor_check():
    inputs = inputs_for('D625')
    rng = np.random.default_rng(202610111938)
    trees = [helper(k, a, b) for k in ('p', 'n') for a, b in itertools.permutations(range(4), 2)]
    trees += [random_tree(rng, 4) for _ in range(64)]
    vm = outputs([t.program for t in trees], inputs, ALPHABET)
    for tree, values in zip(trees, vm):
        if (values.tolist() != [interpret(tree, x) for x in inputs]
                or values.tolist() != [python_output(tree, x) for x in inputs]):
            raise ValueError('random/helper executor disagreement')
    xs = np.asarray(inputs)
    for kind, a, b in itertools.product(('p', 'n'), range(4), range(4)):
        if a == b:
            continue
        labels = np.where(xs[:, a] > 0, xs[:, b], 0) if kind == 'p' else np.where(xs[:, a] > 0, 0, xs[:, b])
        if not np.array_equal(outputs([helper(kind, a, b).program], inputs, ALPHABET)[0], labels):
            raise ValueError('helper labels/operand-order mismatch')
    return dict(passed=True, helpers=24, random_trees=64, seed=202610111938,
                conditions=['negative', 'zero', 'positive'], executable=executable_check())


def overlap(cells):
    # old_banks uses *bank*.json; rectifier's frozen manifest is also an old bank.
    from experiments.chem_tape.rectified_run import DATA
    old = old_banks()
    path = DATA / 'manifest.json'
    old.append((str(path), json.loads(path.read_text())))
    labels = np.asarray([c['labels'] for _, b in old for c in b['screen']['cells']])
    refs = [(path, c['id']) for path, b in old for c in b['screen']['cells']]
    audit = []
    for cell in cells:
        counts = np.count_nonzero(labels == cell['labels'], axis=1)
        i = int(np.argmax(counts))
        audit.append(dict(id=cell['id'], best_old_matches=int(counts[i]), old_bank=refs[i][0],
                          old_cell=refs[i][1], old_excluded=5 * int(counts[i]) >= 4 * 625))
    return audit, {path: hashlib.sha256(json.dumps(b, sort_keys=True).encode()).hexdigest() for path, b in old}


def split(cells):
    source = [c for c in cells if c['shape'] == 'source']
    destinations = sorted((c for c in cells if c['shape'] == 'destination'), key=lambda c: (c['label_hash'], c['id']))
    if not set(SEEN) <= {c['id'] for c in destinations}:
        raise ValueError('seen development cells excluded')
    if ({c['helpers'][0][0] for c in source} != {'p', 'n'}
            or {int(i) for c in source for i in c['helpers'][0][1:]} != set(range(4))):
        raise ValueError('insufficient source gate/input coverage')
    development = list(SEEN) + [c['id'] for c in destinations if c['id'] not in SEEN][:2]
    protected = [c['id'] for c in destinations if c['id'] not in development]
    if len(development) != 6 or len(protected) < 8:
        raise ValueError('insufficient protected roster')
    return dict(source=[c['id'] for c in source], development=development, protected=protected)


def build(deadline=None):
    start = time.monotonic()
    executable_check()
    verification = executor_check()
    cells = roster()
    verify(cells)
    audit, hashes = overlap(cells)
    screen = screen_domain('D625', 9, deadline, cells=cells, tokens=EXECUTABLE,
                           machine_type=XMachine, alphabet=ALPHABET)
    by = {c['id']: c for c in audit}
    admitted = []
    for cell in screen['cells']:
        cell.update(by[cell['id']])
        cell['retained'] = cell['best_matches'] < 625 and not cell['duplicate_ids'] and not cell['old_excluded']
        cell['exclusion_reason'] = ('old_agreement_at_least_80_percent' if cell['old_excluded'] else
                                    'short_exact_alias' if cell['best_matches'] == 625 else
                                    'duplicate_label' if cell['duplicate_ids'] else None)
        if cell['retained']:
            if any(5 * np.count_nonzero(np.asarray(cell['labels']) == c['labels']) >= 4 * 625 for c in admitted):
                cell['retained'], cell['exclusion_reason'] = False, 'pairwise_agreement_at_least_80_percent'
            else:
                admitted.append(cell)
    bank = dict(name=BANK, alphabet=ALPHABET, inputs=inputs_for('D625'), screen=screen,
                overlap=audit, old_bank_hashes=hashes, verification=verify(screen['cells']),
                executor_check=verification, seconds=time.monotonic()-start, split=None,
                admission='no exact alias through nine executable tokens; old/admitted pairwise agreement <80%; short near-aliases descriptive',
                tie_break='label SHA256/id; four stage-0 seen plus lowest two remaining; all remaining protected')
    try:
        bank['split'], bank['admitted'] = split(admitted), True
    except ValueError as error:
        bank['admitted'], bank['failure'] = False, str(error)
    return bank
