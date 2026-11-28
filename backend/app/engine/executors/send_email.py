"""Send Email executor — sends via Gmail API."""

import base64
from email.mime.text import MIMEText
from typing import Any

from app.engine.base import BaseNodeExecutor, ExecutionContext, NodeResult
from app.engine.executors._google_helpers import (
    CredentialError,
    get_google_credentials,
    google_api_request,
)
from app.engine.registry import register_executor

GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


class SendEmailExecutor(BaseNodeExecutor):
    def execute(
        self,
        node_id: str,
        config: dict[str, Any],
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> NodeResult:
        connection_id = config.get("connection_id")
        if not connection_id:
            return NodeResult(
                node_id=node_id,
                status="failed",
                error="No connection_id configured.",
            )

        to = config.get("to", "")
        subject = config.get("subject", "")
        body_text = config.get("body", "")

        if not to:
            return NodeResult(
                node_id=node_id,
                status="failed",
                error="Recipient (to) is required.",
            )

        try:
            access_token, conn = get_google_credentials(connection_id, context)
        except CredentialError as exc:
            return NodeResult(
                node_id=node_id, status="failed", error=str(exc)
            )

        msg = MIMEText(body_text)
        msg["To"] = to
        msg["Subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        try:
            result = google_api_request(
                method="POST",
                url=GMAIL_SEND_URL,
                access_token=access_token,
                body={"raw": raw},
                connection=conn,
                context=context,
            )
        except Exception as exc:
            return NodeResult(
                node_id=node_id, status="failed", error=str(exc)
            )

        return NodeResult(
            node_id=node_id,
            status="completed",
            output={
                "message_id": result.get("id", ""),
                "thread_id": result.get("threadId", ""),
            },
        )


register_executor("send_email", SendEmailExecutor())
