"""Manual trigger executor — fires when a user clicks Run."""

from typing import Any

from app.engine.base import BaseNodeExecutor, ExecutionContext, NodeResult
from app.engine.registry import register_executor


class ManualTriggerExecutor(BaseNodeExecutor):
    def execute(
        self,
        node_id: str,
        config: dict[str, Any],
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> NodeResult:
        return NodeResult(
            node_id=node_id,
            status="completed",
            output={
                "triggered": True,
                "triggered_by": str(context.user_id),
            },
        )


register_executor("manual_trigger", ManualTriggerExecutor())
