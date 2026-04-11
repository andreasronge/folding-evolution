"""Tree-walking evaluator for folding evolution AST nodes."""

from __future__ import annotations

from typing import Any

from folding_evolution.ast_nodes import Keyword, ListExpr, Literal, NsSymbol, Symbol


def evaluate(node, ctx: dict, env: dict | None = None) -> Any:
    """Evaluate an AST node. ctx = data context, env = local bindings."""
    try:
        return _eval(node, ctx, env)
    except Exception:
        return None


def _eval(node, ctx: dict, env: dict | None) -> Any:
    if isinstance(node, Literal):
        return node.value

    if isinstance(node, Keyword):
        return node.name

    if isinstance(node, NsSymbol):
        if node.ns == "data":
            return ctx.get(node.name)
        return None

    if isinstance(node, Symbol):
        if env is not None:
            return env.get(node.name)
        return None

    if isinstance(node, ListExpr):
        return _eval_list(node, ctx, env)

    return None


def _eval_list(node: ListExpr, ctx: dict, env: dict | None) -> Any:
    items = node.items
    if not items:
        return None

    op = items[0]
    if not isinstance(op, Symbol):
        return None

    name = op.name
    args = items[1:]

    # Special forms (don't eagerly evaluate all args)
    if name == "fn":
        return _eval_fn(args, ctx, env)
    if name == "if":
        return _eval_if(args, ctx, env)
    if name == "and":
        return _eval_and(args, ctx, env)
    if name == "or":
        return _eval_or(args, ctx, env)

    # Evaluate all operands
    vals = [_eval(a, ctx, env) for a in args]

    if name == "count":
        v = vals[0]
        return len(v) if isinstance(v, list) else None
    if name == "first":
        v = vals[0]
        return v[0] if isinstance(v, list) and v else None
    if name == "rest":
        v = vals[0]
        return v[1:] if isinstance(v, list) else None
    if name == "get":
        record, key = vals[0], vals[1]
        if isinstance(record, dict):
            return record.get(key)
        return None
    if name == "filter":
        fn, data = vals[0], vals[1]
        if callable(fn) and isinstance(data, list):
            return [x for x in data if fn(x)]
        return None
    if name == "map":
        fn, data = vals[0], vals[1]
        if callable(fn) and isinstance(data, list):
            return [fn(x) for x in data]
        return None
    if name == "+":
        return vals[0] + vals[1]
    if name == "-":
        return vals[0] - vals[1]
    if name == ">":
        return vals[0] > vals[1]
    if name == "<":
        return vals[0] < vals[1]
    if name == "=":
        return vals[0] == vals[1]
    if name == "not":
        return not vals[0]

    return None


def _eval_fn(args, ctx: dict, env: dict | None):
    if len(args) < 2:
        return None
    param = args[0]
    if not isinstance(param, Symbol):
        return None
    body = args[1]
    param_name = param.name
    captured_env = dict(env) if env else {}

    def closure(arg):
        local_env = {**captured_env, param_name: arg}
        return _eval(body, ctx, local_env)

    return closure


def _eval_if(args, ctx: dict, env: dict | None):
    if not args:
        return None
    cond = _eval(args[0], ctx, env)
    if cond:
        return _eval(args[1], ctx, env) if len(args) > 1 else None
    else:
        return _eval(args[2], ctx, env) if len(args) > 2 else None


def _eval_and(args, ctx: dict, env: dict | None):
    if len(args) < 2:
        return None
    a = _eval(args[0], ctx, env)
    if not a:
        return a
    return _eval(args[1], ctx, env)


def _eval_or(args, ctx: dict, env: dict | None):
    if len(args) < 2:
        return None
    a = _eval(args[0], ctx, env)
    if a:
        return a
    return _eval(args[1], ctx, env)
