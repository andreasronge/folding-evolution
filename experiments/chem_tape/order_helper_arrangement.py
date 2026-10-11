"""1628 within-entry helper removal; no slot deletion or semantic deduplication."""

import copy
import hashlib

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.order_library import helpers
from experiments.chem_tape.tree_gp_search import Tree, interpret
from experiments.chem_tape.tree_permutation import permute, signature

TASK = '2026-10-11-1628'
REALIZATIONS = 4
MAX_DRAWS = 256


def seed(domain, *parts):
    raw = digest([TASK, '1628-' + domain, *parts]).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], 'big') & ((1 << 63) - 1)


class Semantics:
    """Cache exact D625 vectors, independently checking every unique subtree."""

    def __init__(self, inputs):
        self.inputs = inputs
        self.helper_vectors = helpers(inputs)
        self.helper_names = {v: k for k, v in self.helper_vectors.items()}
        self.cache = {}

    def vector(self, prefix):
        prefix = tuple(prefix)
        if prefix not in self.cache:
            tree = Tree(prefix)
            vm = outputs([tree.program], self.inputs, ALPHABET)[0]
            python = np.asarray([interpret(tree, x) for x in self.inputs], dtype='<i8')
            if not np.array_equal(vm, python):
                raise ValueError('D625 interpreter/VM disagreement')
            self.cache[prefix] = python.tobytes()
        return self.cache[prefix]

    def census(self, prefix):
        tree = Tree(tuple(prefix))
        return [dict(node=i, helper=self.helper_names[v])
                for i in range(len(tree.prefix))
                for v in [self.vector(tree.prefix[i:tree.ends[i]])]
                if v in self.helper_names]

    def projection(self, prefix):
        vector = self.vector(prefix)
        return [i for i in range(4) if vector == np.asarray(
            [x[i] for x in self.inputs], dtype='<i8').tobytes()]


def replace(entry, construction_seed, semantics, max_draws=MAX_DRAWS):
    # Calling the existing pool shuffler on ONE entry restricts every pool
    # to that entry. A new deterministic draw seed gives independent uniform
    # pool permutations; never condition on search performance.
    for draw in range(1, max_draws + 1):
        candidate = permute([entry], seed('draw', construction_seed, draw))[0][0]
        if not semantics.census(candidate['prefix']):
            result = copy.deepcopy(entry)
            result.update(candidate)
            result['semantic_hash'] = hashlib.sha256(semantics.vector(result['prefix'])).hexdigest()
            # Canonical labels and source recurrence metadata describe the
            # original entry, so retain them only in the audit, not the donor.
            from experiments.chem_tape.tree_library import canonical
            result['canonical'] = list(canonical(Tree(tuple(result['prefix']))))
            return result, draw
    raise ValueError(f'helper construction exhausted {max_draws} draws; seed={construction_seed}')


def build(libraries, inputs):
    semantics = Semantics(inputs)
    result, audit = [], []
    for b, lib in enumerate(libraries):
        original = lib['semantic_all']
        slots = []
        for slot, e in enumerate(original):
            vector = semantics.vector(e['prefix'])
            if hashlib.sha256(vector).hexdigest() != e['semantic_hash']:
                raise ValueError('saved semantic hash mismatch')
            root = semantics.helper_names.get(vector)
            embedded = semantics.census(e['prefix'])
            if root is None and embedded:
                raise ValueError('non-helper entry contains an embedded helper; approved audit differs')
            if root:
                slots.append((slot, root))
        constructions = []
        for realization in range(REALIZATIONS):
            entries = copy.deepcopy(original)
            changes = []
            for slot, helper in slots:
                s = seed('construction', b, realization, slot)
                entries[slot], draws = replace(original[slot], s, semantics)
                changes.append(dict(slot=slot, helper=helper, seed=s, draws=draws,
                                    original_semantic_hash=original[slot]['semantic_hash'],
                                    replacement_semantic_hash=entries[slot]['semantic_hash'],
                                    projection_inputs=semantics.projection(entries[slot]['prefix'])))
            changed_slots = {slot for slot, _ in slots}
            for slot, (before, after) in enumerate(zip(original, entries)):
                if signature([before]) != signature([after]):
                    raise ValueError('per-entry material/shape/length invariants failed')
                if slot not in changed_slots and digest(before) != digest(after):
                    raise ValueError('non-helper entry changed')
                if semantics.census(after['prefix']):
                    raise ValueError('helper survived in R-hx subtree')
            constructions.append(dict(realization=realization, entries=entries))
            audit.append(dict(build=b, realization=realization, entry_count=len(entries),
                              entries_hash=digest(entries), changed_slots=changes,
                              unchanged_nonhelpers=True, per_entry_invariants=True,
                              interpreter_vm_agreement=True, helper_subtrees=0,
                              unique_semantics=len({e['semantic_hash'] for e in entries}),
                              duplicate_slots_preserved=True))
        result.append(dict(build=b, entries=original, constructions=constructions))
    return result, dict(admitted=True, max_draws=MAX_DRAWS, realizations=REALIZATIONS,
                        helpers_per_build=[len(x['changed_slots']) for x in audit[::REALIZATIONS]],
                        unique_subtrees_validated=len(semantics.cache), per_construction=audit)
