# Architecture: The Folding Pipeline

## Overview

```
Genotype (string of 62 possible characters)
    | fold onto 2D grid (direction changes per character)
    v
Spatial arrangement (characters on grid positions)
    | find adjacent pairs (8-connected neighborhood)
    v
Fragment pairs (function+data, comparator+values, etc.)
    | assemble via multi-pass chemistry rules
    v
Program AST
    | evaluate in sandbox
    v
Output -> fitness
```

## Layer 1: Alphabet

Each of the 62 valid characters encodes two things:
1. **Fragment type** — what program construct it represents
2. **Fold instruction** — how it bends the chain during folding

### Fragment Types

```
Functions (consume adjacent fragments):
  A -> filter     B -> count      C -> map
  D -> get        E -> reduce     F -> group-by
  G -> set        H -> contains?  I -> first

Operators (binary):
  J -> +          K -> >          L -> <
  M -> =          N -> and        O -> or
  P -> not

Function wrappers:
  Q -> fn [x]     R -> let

Conditionals/Structural:
  W -> match      X -> if         Y -> assoc

Data sources (leaf nodes):
  S -> data/products    T -> data/employees
  U -> data/orders      V -> data/expenses

Field keys:
  a -> :price     b -> :status    c -> :department
  d -> :id        e -> :name      f -> :amount
  g -> :category  h -> :employee_id

Literals:
  0-9 -> numbers (0, 100, 200, ... 900)

Wildcards (for match patterns):
  i-z -> wildcard

Spacer:
  Z -> spacer (fold instruction only, no code)
```

### Fold Instructions

```
Uppercase letters (A-V) -> turn left
W -> straight (explicit)
X -> turn left (explicit)
Y -> turn right (explicit)
Z -> reverse (explicit)
Lowercase letters (a-z) -> straight (continue direction)
Digits (0-9) -> straight
```

## Layer 2: Folding Algorithm

Walk the genotype string character by character, placing each on a 2D grid.

```
State: (grid, position, direction)
Initial: (empty_grid, (0,0), right)

For each character:
  1. Place character at current position in grid
  2. Compute new direction from fold instruction
  3. Advance position one step in new direction
  4. Self-avoidance: if next cell occupied, try left, then right, then skip
```

### Example

```
Genotype: "QDaK5XASBw"

Q(fn) at (0,0), turn left -> heading up
D(get) at (0,-1), turn left -> heading left
a(:price) at (-1,-1), straight -> heading left
K(>) at (-2,-1), turn left -> heading down
5(500) at (-2,0), straight -> heading down
X(spacer) at (-2,1), turn left -> heading right
A(filter) at (-1,1), turn left -> heading up
S(data/products) at (-1,0), turn left -> heading left

Grid:
       -2    -1     0
  -1:   K     a     D
   0:   5     S     Q
   1:         A
```

Self-avoidance creates "junk DNA" — skipped characters that don't contribute to the phenotype but absorb mutations neutrally.

## Layer 3: Chemistry (Multi-Pass Assembly)

After folding, scan the grid for adjacent character pairs (8-connected neighborhood including diagonals). Fragments bond according to fixed rules in sequential passes.

### Pass 1 — Leaf Bonds
- `get + field_key` -> `(get x :key)`
- `assoc + field_key + value` -> `(assoc x :key value)`
- Data sources and literals stay as leaves

### Pass 2 — Predicate Bonds
- `comparator + two_values` -> `(> val1 val2)`
- `fn + expression` -> `(fn [x] expression)`
- Priority: assembled fragments (pass 1) preferred over raw literals/data

### Pass 3 — Structural Bonds
- `filter/map + fn + data` -> `(filter fn data)`
- `count/first + collection` -> `(count collection)`
- `reduce + fn + init + data` -> `(reduce fn init data)`

### Pass 4 — Composition Bonds
- `and/or + two_exprs` -> `(and expr1 expr2)`
- `not + expr` -> `(not expr)`
- `set + collection` -> `(set collection)`
- `contains? + set + value` -> `(contains? set value)`

### Pass 5 — Conditional Bonds
- `match + fragments` -> structural pattern match
- `if + predicate + then [+ else]` -> `(if pred then else)`

### Key Properties

- **Fragments consumed in earlier passes can't bond again** — prevents ambiguity
- **Creates developmental cascades** — what forms in pass 1 constrains pass 2+
- **Deterministic** — same grid always produces same phenotype
- **Bond priority** — when a fragment has multiple adjacent candidates, prefer assembled > literal > data_source

### Assembly Example

```
Grid:
       -2    -1     0
  -1:   K     a     D
   0:   5     S     Q
   1:         A

Pass 1: D adjacent to a -> (get x :price)
        S stays as data/products
        5 stays as 500

Pass 2: K adjacent to (get x :price) and 5 -> (> (get x :price) 500)
        Q adjacent to (> ...) -> (fn [x] (> (get x :price) 500))

Pass 3: A adjacent to (fn [x] ...) and S ->
        (filter (fn [x] (> (get x :price) 500)) data/products)

Result: A 10-character genotype folded into a valid filter expression.
```

## Layer 4: Genetic Operators

### Mutation

```
Point mutation:  flip one character to random (conservative)
Insertion:       insert random character at random position (frameshift)
Deletion:        remove character at random position (frameshift)
```

Point mutations are conservative. Insertions/deletions shift the entire downstream fold — analogous to frameshift mutations in biology.

### Crossover

```
Single-point splice:
  Parent A: "QDaK5XASBw"
  Parent B: "CEhT3YFGdR"
  Cut A at 4, Cut B at 6:
  Offspring: "QDaK" + "FGdR" = "QDaKFGdR"
```

The head folds as parent A. At the splice point, parent B's characters continue the fold. New adjacencies appear at the splice junction — novel bonds that neither parent had.

## Design Decisions (from Elixir implementation)

1. **2D grid, 8-connected adjacency** — provides enough bonding opportunities. No need for 1D or 3D.

2. **Self-avoidance: try left, right, skip** — creates junk DNA regions that absorb mutations.

3. **Bond priority: assembled > literal > data** — gives pass-1 results priority as comparator operands. Without this, raw data sources get consumed before assembled get-expressions.

4. **Data sources emit namespace symbols** — `data/products` not bare `products`. Critical for correct evaluation in the target language.

5. **Deterministic folding** — same genotype always produces same phenotype. Stochastic folding could increase robustness but complicates fitness evaluation.

6. **62-character alphabet** — may be too large. The i-z range is all wildcards/spacers. Could reduce to ~30 characters for denser coding.

## Python Implementation Notes

The pipeline is pure computation with no I/O:
- **Fold**: dict mapping (x,y) -> character. Simple loop with direction state.
- **Chemistry**: graph algorithm on the grid adjacency. Each pass filters unbonded positions.
- **Operators**: string manipulation (splice, replace, insert, delete).
- **Evaluation**: the assembled AST needs an interpreter. In Elixir this was PTC-Lisp. In Python, options include: direct Python AST evaluation, a simple Lisp interpreter, or DEAP's tree-based GP representation.

The fold and chemistry are representation-agnostic — they produce an AST regardless of what language evaluates it.
