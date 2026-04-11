"""Data contexts for fitness evaluation.

Creates contexts with VARYING data sizes so count() produces different
values per context. This is critical for the data-dependence gate.
"""

from __future__ import annotations


def make_contexts() -> list[dict]:
    """Generate evaluation contexts with varying collection sizes."""
    return [
        {
            "products": [{"id": i, "price": i * 10, "name": f"p{i}", "status": "active", "category": "A"} for i in range(2)],
            "employees": [{"id": i, "name": f"e{i}", "department": "eng"} for i in range(3)],
            "orders": [{"id": i, "amount": i * 100} for i in range(1)],
            "expenses": [{"id": i, "amount": i * 50} for i in range(4)],
        },
        {
            "products": [{"id": i, "price": i * 10, "name": f"p{i}", "status": "active", "category": "B"} for i in range(3)],
            "employees": [{"id": i, "name": f"e{i}", "department": "sales"} for i in range(5)],
            "orders": [{"id": i, "amount": i * 100} for i in range(2)],
            "expenses": [{"id": i, "amount": i * 50} for i in range(1)],
        },
        {
            "products": [{"id": i, "price": i * 10, "name": f"p{i}", "status": "inactive", "category": "C"} for i in range(5)],
            "employees": [{"id": i, "name": f"e{i}", "department": "hr"} for i in range(2)],
            "orders": [{"id": i, "amount": i * 100} for i in range(4)],
            "expenses": [{"id": i, "amount": i * 50} for i in range(3)],
        },
        {
            "products": [{"id": i, "price": i * 10, "name": f"p{i}", "status": "active", "category": "A"} for i in range(7)],
            "employees": [{"id": i, "name": f"e{i}", "department": "eng"} for i in range(1)],
            "orders": [{"id": i, "amount": i * 100} for i in range(6)],
            "expenses": [{"id": i, "amount": i * 50} for i in range(2)],
        },
        {
            "products": [{"id": i, "price": i * 10, "name": f"p{i}", "status": "active", "category": "B"} for i in range(4)],
            "employees": [{"id": i, "name": f"e{i}", "department": "sales"} for i in range(4)],
            "orders": [{"id": i, "amount": i * 100} for i in range(3)],
            "expenses": [{"id": i, "amount": i * 50} for i in range(5)],
        },
    ]
