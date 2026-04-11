"""Chemistry: multi-pass assembly of folded grid into AST fragments.

Scans the 2D grid for adjacent character pairs (8-connected neighborhood)
and assembles them into AST nodes through 5 sequential passes:
1. Leaf bonds (get + field_key, assoc + field_key + value)
2. Predicate bonds (comparator + values, fn + expression)
3. Structural bonds (filter/map + fn + data, count/first + collection)
4. Composition bonds (and/or + exprs, not + expr, set, contains?)
5. Conditional bonds (if + pred + branches, match + pattern)

When a position is consumed into a bond, its parent inherits the consumed
position's adjacencies. This allows assembly to chain through multiple hops
(e.g., K sees (get x :price) through consumed field_key position).

Optional DevGenome parameter enables evolvable chemistry: distance-2 bonds,
affinity-weighted neighbor scoring, subassembly stability, and occupancy
penalties. When dev_genome is None, behavior is identical to the original
hard-coded chemistry.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .alphabet import to_fragment
from .ast_nodes import ASTNode, Keyword, ListExpr, Literal, NsSymbol, Symbol

if TYPE_CHECKING:
    from .dev_genome import DevGenome

Position = tuple[int, int]
Grid = dict[Position, str]

Fragment = tuple | str
_NEIGHBORS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

# Distance-2 neighbor offsets (Chebyshev distance 2, excluding distance 1)
_NEIGHBORS_D2 = [
    (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2),
    (-2, -1),                                (2, -1),
    (-2,  0),                                (2,  0),
    (-2,  1),                                (2,  1),
    (-2,  2), (-1,  2), (0,  2), (1,  2), (2,  2),
]


def assemble(grid: Grid, dev_genome: DevGenome | None = None) -> list[ASTNode]:
    """Assemble a folded grid into AST nodes.

    Args:
        grid: 2D grid mapping positions to characters (from fold()).
        dev_genome: Optional evolvable chemistry parameters. When None,
            uses the original hard-coded chemistry (backward compatible).
            When provided, enables distance-2 bonds and other evolvable
            chemistry features.
    """
    if dev_genome is not None:
        adjacency = _build_adjacency_dev(grid, dev_genome)
    else:
        adjacency = _build_adjacency(grid)

    fragment_map: dict[Position, Fragment] = {}
    for pos, char in grid.items():
        frag = to_fragment(char)
        if frag != "spacer":
            fragment_map[pos] = frag

    wildcard_positions = {pos for pos, frag in fragment_map.items() if frag == "wildcard"}
    consumed: set[Position] = set()

    fragment_map, consumed, adjacency = _pass_leaf_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_predicate_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_structural_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_composition_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_conditional_bonds(
        fragment_map, adjacency, consumed, wildcard_positions
    )

    result = []
    for pos, frag in fragment_map.items():
        if pos not in consumed:
            ast = _fragment_to_ast(frag)
            if ast is not None:
                result.append(ast)
    return result


def assemble_with_consumed(
    grid: Grid, dev_genome: DevGenome | None = None,
) -> tuple[list[ASTNode], set[Position]]:
    """Like assemble(), but also returns the set of grid positions that
    participated in bonds (were consumed during assembly).

    Returns (fragments, consumed_positions).
    """
    if dev_genome is not None:
        adjacency = _build_adjacency_dev(grid, dev_genome)
    else:
        adjacency = _build_adjacency(grid)

    fragment_map: dict[Position, Fragment] = {}
    for pos, char in grid.items():
        frag = to_fragment(char)
        if frag != "spacer":
            fragment_map[pos] = frag

    wildcard_positions = {pos for pos, frag in fragment_map.items() if frag == "wildcard"}
    consumed: set[Position] = set()

    fragment_map, consumed, adjacency = _pass_leaf_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_predicate_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_structural_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_composition_bonds(fragment_map, adjacency, consumed)
    fragment_map, consumed, adjacency = _pass_conditional_bonds(
        fragment_map, adjacency, consumed, wildcard_positions
    )

    result = []
    # Include parent positions (bond roots) in the consumed set for callers
    bonded_positions = set(consumed)
    for pos, frag in fragment_map.items():
        if pos not in consumed:
            ast = _fragment_to_ast(frag)
            if ast is not None:
                result.append(ast)
            # Parent positions that hold assembled fragments are also bonded
            if isinstance(frag, tuple) and frag[0] == "assembled":
                bonded_positions.add(pos)

    return result, bonded_positions


def _bond(fmap, adj, consumed, parent_pos, child_positions, assembled):
    """Execute a bond: place assembled at parent, consume children, extend adjacency."""
    fmap[parent_pos] = assembled
    consumed |= child_positions

    # Parent inherits adjacencies from consumed children
    parent_neighbors = list(adj.get(parent_pos, ()))
    for cp in child_positions:
        for neighbor in adj.get(cp, ()):
            if neighbor != parent_pos and neighbor not in child_positions and neighbor not in parent_neighbors:
                parent_neighbors.append(neighbor)
    adj[parent_pos] = parent_neighbors

    # Also make new neighbors point back to parent
    for neighbor in parent_neighbors:
        if neighbor not in consumed and neighbor != parent_pos:
            neighbor_adj = adj.get(neighbor)
            if neighbor_adj is not None:
                new_adj = [p for p in neighbor_adj if p not in child_positions]
                if parent_pos not in new_adj:
                    new_adj.append(parent_pos)
                adj[neighbor] = new_adj

    return fmap, consumed, adj


def _get_unconsumed_neighbors(pos, adj, consumed, fmap):
    """Return adjacent unconsumed positions with their fragments."""
    result = []
    for npos in adj.get(pos, ()):
        if npos not in consumed:
            frag = fmap.get(npos)
            if frag is not None:
                result.append((npos, frag))
    return result


# === Pass 1: Leaf Bonds ===


def _pass_leaf_bonds(fmap, adj, consumed):
    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if frag == ("fn_fragment", "get"):
            fmap, consumed, adj = _try_get_bond(pos, fmap, adj, consumed)

    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if frag == ("fn_fragment", "assoc"):
            fmap, consumed, adj = _try_assoc_bond(pos, fmap, adj, consumed)

    return fmap, consumed, adj


def _try_get_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if frag != ("fn_fragment", "get"):
        return fmap, consumed, adj

    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    for npos, nfrag in neighbors:
        if isinstance(nfrag, tuple) and len(nfrag) == 2 and nfrag[0] == "field_key":
            key = nfrag[1]
            ast = ListExpr((Symbol("get"), Symbol("x"), Keyword(key)))
            fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {npos}, ("assembled", ast))
            return fmap, consumed, adj

    return fmap, consumed, adj


def _try_assoc_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if frag != ("fn_fragment", "assoc"):
        return fmap, consumed, adj

    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    key_frag = None
    val_frag = None
    for npos, nfrag in neighbors:
        if isinstance(nfrag, tuple) and len(nfrag) == 2 and nfrag[0] == "field_key" and key_frag is None:
            key_frag = (npos, nfrag)
        elif _is_value_fragment(nfrag) and val_frag is None:
            val_frag = (npos, nfrag)

    if key_frag and val_frag:
        kp, kf = key_frag
        vp, vf = val_frag
        key = kf[1]
        ast = ListExpr((Symbol("assoc"), Symbol("x"), Keyword(key), _fragment_to_ast(vf)))
        fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {kp, vp}, ("assembled", ast))

    return fmap, consumed, adj


# === Pass 2: Predicate Bonds ===


def _pass_predicate_bonds(fmap, adj, consumed):
    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if isinstance(frag, tuple) and len(frag) == 2 and frag[0] == "comparator":
            fmap, consumed, adj = _try_comparator_bond(pos, fmap, adj, consumed)

    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if frag == ("fn_fragment", "fn"):
            fmap, consumed, adj = _try_fn_bond(pos, fmap, adj, consumed)

    return fmap, consumed, adj


def _try_comparator_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if not (isinstance(frag, tuple) and len(frag) == 2 and frag[0] == "comparator"):
        return fmap, consumed, adj

    op = frag[1]
    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    values = [(npos, nfrag) for npos, nfrag in neighbors if _is_value_fragment(nfrag)]
    values.sort(key=lambda x: _value_priority(x[1]))

    if len(values) >= 2:
        (p1, f1), (p2, f2) = values[0], values[1]
        ast = ListExpr((Symbol(op), _fragment_to_ast(f1), _fragment_to_ast(f2)))
        fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {p1, p2}, ("assembled", ast))

    return fmap, consumed, adj


def _value_priority(frag: Fragment) -> int:
    if isinstance(frag, tuple) and len(frag) == 2:
        if frag[0] == "assembled":
            return 0
        if frag[0] == "literal":
            return 1
        if frag[0] == "data_source":
            return 2
    return 3


def _try_fn_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if frag != ("fn_fragment", "fn"):
        return fmap, consumed, adj

    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    for npos, nfrag in neighbors:
        if _is_expression_fragment(nfrag):
            ast = ListExpr((Symbol("fn"), Symbol("x"), _fragment_to_ast(nfrag)))
            fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {npos}, ("assembled", ast))
            return fmap, consumed, adj

    return fmap, consumed, adj


# === Pass 3: Structural Bonds ===


_HIGHER_ORDER_OPS = frozenset(("filter", "map", "reduce", "group_by"))
_WRAPPER_OPS = frozenset(("count", "first", "reverse", "sort", "rest", "last"))

def _pass_structural_bonds(fmap, adj, consumed):
    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if isinstance(frag, tuple) and frag[0] == "fn_fragment" and frag[1] in _HIGHER_ORDER_OPS:
            fmap, consumed, adj = _try_higher_order_bond(pos, fmap, adj, consumed)

    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if isinstance(frag, tuple) and frag[0] == "fn_fragment" and frag[1] in _WRAPPER_OPS:
            fmap, consumed, adj = _try_wrapper_bond(pos, fmap, adj, consumed)

    return fmap, consumed, adj


def _try_higher_order_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if not (isinstance(frag, tuple) and frag[0] == "fn_fragment" and frag[1] in ("filter", "map", "reduce", "group_by")):
        return fmap, consumed, adj

    op = frag[1]
    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    fn_frag = None
    data_frag = None
    for npos, nfrag in neighbors:
        if _is_fn_expression(nfrag) and fn_frag is None:
            fn_frag = (npos, nfrag)
        elif _is_data_fragment(nfrag) and data_frag is None:
            data_frag = (npos, nfrag)

    if fn_frag and data_frag:
        fn_pos, fn_f = fn_frag
        data_pos, data_f = data_frag
        ast = ListExpr((Symbol(op), _fragment_to_ast(fn_f), _fragment_to_ast(data_f)))
        fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {fn_pos, data_pos}, ("assembled", ast))

    return fmap, consumed, adj


def _try_wrapper_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if not (isinstance(frag, tuple) and frag[0] == "fn_fragment" and frag[1] in ("count", "first", "reverse", "sort", "rest", "last")):
        return fmap, consumed, adj

    op = frag[1]
    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    for npos, nfrag in neighbors:
        if _is_collection_fragment(nfrag):
            ast = ListExpr((Symbol(op), _fragment_to_ast(nfrag)))
            fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {npos}, ("assembled", ast))
            return fmap, consumed, adj

    return fmap, consumed, adj


# === Pass 4: Composition Bonds ===


def _pass_composition_bonds(fmap, adj, consumed):
    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if isinstance(frag, tuple) and frag[0] == "connective" and frag[1] in ("and", "or"):
            fmap, consumed, adj = _try_logical_bond(pos, fmap, adj, consumed)

    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if frag == ("connective", "not"):
            fmap, consumed, adj = _try_not_bond(pos, fmap, adj, consumed)

    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if frag == ("fn_fragment", "set"):
            fmap, consumed, adj = _try_set_bond(pos, fmap, adj, consumed)

    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if frag == ("fn_fragment", "contains?"):
            fmap, consumed, adj = _try_contains_bond(pos, fmap, adj, consumed)

    return fmap, consumed, adj


def _try_logical_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if not (isinstance(frag, tuple) and frag[0] == "connective" and frag[1] in ("and", "or")):
        return fmap, consumed, adj

    op = frag[1]
    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    exprs = [(npos, nfrag) for npos, nfrag in neighbors if _is_expression_fragment(nfrag)]

    if len(exprs) >= 2:
        (p1, f1), (p2, f2) = exprs[0], exprs[1]
        ast = ListExpr((Symbol(op), _fragment_to_ast(f1), _fragment_to_ast(f2)))
        fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {p1, p2}, ("assembled", ast))

    return fmap, consumed, adj


def _try_not_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if frag != ("connective", "not"):
        return fmap, consumed, adj

    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    for npos, nfrag in neighbors:
        if _is_expression_fragment(nfrag):
            ast = ListExpr((Symbol("not"), _fragment_to_ast(nfrag)))
            fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {npos}, ("assembled", ast))
            return fmap, consumed, adj

    return fmap, consumed, adj


def _try_set_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if frag != ("fn_fragment", "set"):
        return fmap, consumed, adj

    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    for npos, nfrag in neighbors:
        if _is_collection_fragment(nfrag):
            ast = ListExpr((Symbol("set"), _fragment_to_ast(nfrag)))
            fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {npos}, ("assembled", ast))
            return fmap, consumed, adj

    return fmap, consumed, adj


def _try_contains_bond(pos, fmap, adj, consumed):
    frag = fmap.get(pos)
    if frag != ("fn_fragment", "contains?"):
        return fmap, consumed, adj

    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    sets = [(npos, nfrag) for npos, nfrag in neighbors if _is_set_fragment(nfrag)]
    values = [(npos, nfrag) for npos, nfrag in neighbors if _is_value_fragment(nfrag)]

    if sets and values:
        sp, sf = sets[0]
        vp, vf = values[0]
        ast = ListExpr((Symbol("contains?"), _fragment_to_ast(sf), _fragment_to_ast(vf)))
        fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {sp, vp}, ("assembled", ast))

    return fmap, consumed, adj


# === Pass 5: Conditional Bonds ===


def _pass_conditional_bonds(fmap, adj, consumed, wildcard_positions):
    for pos in list(fmap.keys()):
        if pos in consumed:
            continue
        frag = fmap.get(pos)
        if frag == ("fn_fragment", "match"):
            fmap, consumed, adj = _try_match_bond(pos, fmap, adj, consumed, wildcard_positions)
        elif frag == ("fn_fragment", "if"):
            fmap, consumed, adj = _try_if_bond(pos, fmap, adj, consumed)

    return fmap, consumed, adj


def _try_match_bond(pos, fmap, adj, consumed, wildcard_positions):
    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    pattern_fragments = [
        (npos, nfrag) for npos, nfrag in neighbors
        if not (isinstance(nfrag, tuple) and nfrag[0] == "fn_fragment")
    ]
    pattern_fragments.sort(key=lambda x: x[0])

    if not pattern_fragments:
        return fmap, consumed, adj

    parts = []
    for npos, nfrag in pattern_fragments:
        if npos in wildcard_positions:
            parts.append("*")
        else:
            ast = _fragment_to_ast(nfrag)
            parts.append(_format_pattern_ast(ast))

    if len(parts) == 1:
        pattern_str = parts[0]
    else:
        pattern_str = "(" + " ".join(parts) + ")"

    match_ast = ListExpr((
        NsSymbol("tool", "match"),
        Keyword("pattern"),
        Symbol(pattern_str),
    ))

    child_positions = {npos for npos, _ in pattern_fragments}
    fmap, consumed, adj = _bond(fmap, adj, consumed, pos, child_positions, ("assembled", match_ast))
    return fmap, consumed, adj


def _try_if_bond(pos, fmap, adj, consumed):
    neighbors = _get_unconsumed_neighbors(pos, adj, consumed, fmap)
    usable = [
        (npos, nfrag) for npos, nfrag in neighbors
        if nfrag not in (("fn_fragment", "if"), ("fn_fragment", "match"))
    ]

    preds = [(p, f) for p, f in usable if _is_predicate_fragment(f)]
    non_preds = [(p, f) for p, f in usable if not _is_predicate_fragment(f)]

    # if-bond requires at least one predicate neighbor
    if not preds:
        return fmap, consumed, adj

    sorted_frags = preds + non_preds

    if len(sorted_frags) >= 3:
        (pp, pf), (tp, tf), (ep, ef) = sorted_frags[0], sorted_frags[1], sorted_frags[2]
        ast = ListExpr((Symbol("if"), _fragment_to_ast(pf), _fragment_to_ast(tf), _fragment_to_ast(ef)))
        fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {pp, tp, ep}, ("assembled", ast))
    elif len(sorted_frags) >= 2:
        (pp, pf), (tp, tf) = sorted_frags[0], sorted_frags[1]
        ast = ListExpr((Symbol("if"), _fragment_to_ast(pf), _fragment_to_ast(tf)))
        fmap, consumed, adj = _bond(fmap, adj, consumed, pos, {pp, tp}, ("assembled", ast))

    return fmap, consumed, adj


def _is_predicate_fragment(frag: Fragment) -> bool:
    if isinstance(frag, tuple) and frag[0] == "assembled":
        ast = frag[1]
        if isinstance(ast, ListExpr) and len(ast.items) > 0:
            head = ast.items[0]
            if isinstance(head, Symbol) and head.name in (">", "<", "=", "and", "or", "not", "contains?"):
                return True
            if isinstance(head, NsSymbol) and head.ns == "tool" and head.name == "match":
                return True
    return False


# === Fragment Classification ===


def _is_value_fragment(frag: Fragment) -> bool:
    if isinstance(frag, tuple) and len(frag) == 2:
        return frag[0] in ("assembled", "literal", "data_source")
    return False


def _is_expression_fragment(frag: Fragment) -> bool:
    if isinstance(frag, tuple) and len(frag) == 2:
        if frag[0] == "assembled":
            return True
        if frag[0] == "literal":
            return True
    return False


def _is_fn_expression(frag: Fragment) -> bool:
    if isinstance(frag, tuple) and frag[0] == "assembled":
        ast = frag[1]
        if isinstance(ast, ListExpr) and len(ast.items) > 0:
            head = ast.items[0]
            return isinstance(head, Symbol) and head.name == "fn"
    return False


def _is_data_fragment(frag: Fragment) -> bool:
    if isinstance(frag, tuple) and len(frag) == 2:
        if frag[0] == "data_source":
            return True
        if frag[0] == "assembled":
            ast = frag[1]
            if isinstance(ast, ListExpr) and len(ast.items) > 0:
                head = ast.items[0]
                if isinstance(head, Symbol) and head.name in ("filter", "map", "reduce", "group_by", "sort"):
                    return True
    return False


def _is_collection_fragment(frag: Fragment) -> bool:
    if isinstance(frag, tuple) and len(frag) == 2:
        return frag[0] in ("assembled", "data_source")
    return False


def _is_set_fragment(frag: Fragment) -> bool:
    if isinstance(frag, tuple) and frag[0] == "assembled":
        ast = frag[1]
        if isinstance(ast, ListExpr) and len(ast.items) > 0:
            head = ast.items[0]
            return isinstance(head, Symbol) and head.name == "set"
    return False


# === Fragment -> AST Conversion ===


def _fragment_to_ast(frag: Fragment) -> ASTNode | None:
    if frag is None:
        return None
    if isinstance(frag, tuple) and len(frag) == 2:
        kind, value = frag
        if kind == "assembled":
            return value
        if kind == "literal":
            return Literal(value)
        if kind == "data_source":
            return NsSymbol("data", value)
        if kind == "field_key":
            return Keyword(value)
        if kind == "fn_fragment":
            return Symbol(value)
        if kind == "comparator":
            return Symbol(value)
        if kind == "connective":
            return Symbol(value)
    if frag == "wildcard":
        return Symbol("*")
    return None


def _format_pattern_ast(ast: ASTNode | None) -> str:
    if ast is None:
        return "*"
    if isinstance(ast, Symbol):
        return ast.name
    if isinstance(ast, Keyword):
        return f":{ast.name}"
    if isinstance(ast, NsSymbol):
        return f"{ast.ns}/{ast.name}"
    if isinstance(ast, Literal):
        return str(ast.value)
    if isinstance(ast, ListExpr):
        inner = " ".join(_format_pattern_ast(item) for item in ast.items)
        return f"({inner})"
    return "*"


# === Adjacency Helpers ===


def _build_adjacency(grid: Grid) -> dict[Position, list[Position]]:
    """Build adjacency graph. Neighbors are in NEIGHBORS scan order (deterministic)."""
    positions = grid.keys()
    result: dict[Position, list[Position]] = {}
    for pos in positions:
        x, y = pos
        neighbors = []
        for dx, dy in _NEIGHBORS:
            npos = (x + dx, y + dy)
            if npos in positions:
                neighbors.append(npos)
        result[pos] = neighbors
    return result


def _build_adjacency_dev(grid: Grid, dev_genome: DevGenome) -> dict[Position, list[Position]]:
    """Build adjacency graph with DevGenome-controlled distance-2 bonds.

    Distance-1 neighbors are always included (weight from dev_genome.distance_weights[0]).
    Distance-2 neighbors are included when dev_genome.distance_weights[1] > 0.

    Neighbor order: distance-1 first (in scan order), then distance-2 (in scan order).
    This preserves determinism and gives distance-1 priority in first-match passes.
    """
    from .dev_genome import DevGenome  # runtime import to avoid circular

    positions = grid.keys()
    d2_weight = dev_genome.distance_weights[1]
    result: dict[Position, list[Position]] = {}

    for pos in positions:
        x, y = pos
        neighbors: list[Position] = []

        # Distance-1 neighbors (always included)
        for dx, dy in _NEIGHBORS:
            npos = (x + dx, y + dy)
            if npos in positions:
                neighbors.append(npos)

        # Distance-2 neighbors (only if weight > 0)
        if d2_weight > 0:
            for dx, dy in _NEIGHBORS_D2:
                npos = (x + dx, y + dy)
                if npos in positions:
                    neighbors.append(npos)

        result[pos] = neighbors

    return result
