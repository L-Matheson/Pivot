"""Condition (If/Else) executor — evaluates a simple expression and
signals which branch to follow via the ``branch`` output key.

The runner reads ``output["branch"]`` and compares it against each
outgoing edge's ``source_handle`` to decide which successors are
reachable.
"""

import operator
from typing import Any

from app.engine.base import BaseNodeExecutor, ExecutionContext, NodeResult
from app.engine.registry import register_executor

_OPS: dict[str, Any] = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    "contains": lambda a, b: b.lower() in a.lower() if isinstance(a, str) and isinstance(b, str) else False,
    "not_contains": lambda a, b: b.lower() not in a.lower() if isinstance(a, str) and isinstance(b, str) else True,
    "is_empty": lambda a, _: a is None or a == "" or a == [] or a == {},
    "is_not_empty": lambda a, _: not (a is None or a == "" or a == [] or a == {}),
}


def _resolve_value(key: str, inputs: dict[str, Any]) -> Any:
    parts = key.split(".", 1)
    if len(parts) == 2:
        node_data = inputs.get(parts[0], {})
        if isinstance(node_data, dict):
            return node_data.get(parts[1])
    for node_data in inputs.values():
        if isinstance(node_data, dict) and key in node_data:
            return node_data[key]
    return None


class ConditionExecutor(BaseNodeExecutor):
    def execute(
        self,
        node_id: str,
        config: dict[str, Any],
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> NodeResult:
        field = config.get("field", "")
        op_name = config.get("operator", "eq")
        compare_value = config.get("value")

        op_fn = _OPS.get(op_name)
        if op_fn is None:
            return NodeResult(
                node_id=node_id, status="failed",
                error=f"Unknown operator: {op_name}",
            )

        actual = _resolve_value(field, inputs) if field else None

        try:
            result = bool(op_fn(actual, compare_value))
        except Exception:
            result = False

        return NodeResult(
            node_id=node_id,
            status="completed",
            output={
                "result": result,
                "branch": "yes" if result else "no",
                "actual_value": actual,
            },
        )


register_executor("condition", ConditionExecutor())
