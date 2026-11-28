"""Transform Data executor — map, filter, or format values between steps."""

import json
from typing import Any

from app.engine.base import BaseNodeExecutor, ExecutionContext, NodeResult
from app.engine.registry import register_executor


def _resolve_input_data(inputs: dict[str, Any]) -> Any:
    if len(inputs) == 1:
        return next(iter(inputs.values()))
    return inputs


def _op_map(data: Any, mapping: dict[str, str]) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"value": data}
    return {dest: data.get(src) for dest, src in mapping.items()}


def _op_pick(data: Any, fields: list[str]) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"value": data}
    return {k: v for k, v in data.items() if k in fields}


def _op_filter_rows(data: Any, field: str, value: Any) -> list[Any]:
    if not isinstance(data, list):
        return [data]
    return [row for row in data if isinstance(row, dict) and row.get(field) == value]


class TransformExecutor(BaseNodeExecutor):
    def execute(
        self,
        node_id: str,
        config: dict[str, Any],
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> NodeResult:
        operation = config.get("operation", "passthrough")
        data = _resolve_input_data(inputs)

        if operation == "passthrough":
            return NodeResult(
                node_id=node_id, status="completed",
                output={"data": data},
            )

        if operation == "map":
            mapping = config.get("mapping", {})
            if not mapping:
                return NodeResult(
                    node_id=node_id, status="failed",
                    error="Map operation requires a 'mapping' dict.",
                )
            return NodeResult(
                node_id=node_id, status="completed",
                output={"data": _op_map(data, mapping)},
            )

        if operation == "pick":
            fields = config.get("fields", [])
            if not fields:
                return NodeResult(
                    node_id=node_id, status="failed",
                    error="Pick operation requires a 'fields' list.",
                )
            return NodeResult(
                node_id=node_id, status="completed",
                output={"data": _op_pick(data, fields)},
            )

        if operation == "filter":
            field = config.get("field", "")
            value = config.get("value")
            if not field:
                return NodeResult(
                    node_id=node_id, status="failed",
                    error="Filter operation requires a 'field'.",
                )
            return NodeResult(
                node_id=node_id, status="completed",
                output={"data": _op_filter_rows(data, field, value)},
            )

        if operation == "json_parse":
            raw = config.get("raw", "")
            if not raw and isinstance(data, str):
                raw = data
            try:
                parsed = json.loads(raw)
            except (json.JSONDecodeError, TypeError) as exc:
                return NodeResult(
                    node_id=node_id, status="failed",
                    error=f"JSON parse error: {exc}",
                )
            return NodeResult(
                node_id=node_id, status="completed",
                output={"data": parsed},
            )

        return NodeResult(
            node_id=node_id, status="failed",
            error=f"Unknown transform operation: {operation}",
        )


register_executor("transform", TransformExecutor())
