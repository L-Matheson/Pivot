"""Send Notification executor — delivers in-app or log-based notifications.

Actual delivery channels (Slack, push, email digest) are added as
connectors become available. For now this records the notification as
output so downstream nodes and the execution log can reference it.
"""

from typing import Any

from app.engine.base import BaseNodeExecutor, ExecutionContext, NodeResult
from app.engine.registry import register_executor


class SendNotificationExecutor(BaseNodeExecutor):
    def execute(
        self,
        node_id: str,
        config: dict[str, Any],
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> NodeResult:
        message = config.get("message", "")
        channel = config.get("channel", "in_app")
        target = config.get("target", "")

        if not message:
            return NodeResult(
                node_id=node_id, status="failed",
                error="Notification message is required.",
            )

        return NodeResult(
            node_id=node_id,
            status="completed",
            output={
                "delivered": True,
                "channel": channel,
                "target": target,
                "message": message,
            },
        )


register_executor("send_notification", SendNotificationExecutor())
