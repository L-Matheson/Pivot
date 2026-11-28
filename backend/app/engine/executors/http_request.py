"""HTTP Request executor — calls any REST endpoint."""

from typing import Any
from urllib.parse import urlparse

import httpx

from app.engine.base import BaseNodeExecutor, ExecutionContext, NodeResult
from app.engine.registry import register_executor

_BLOCKED_NETWORKS = ("127.", "10.", "172.16.", "172.17.", "172.18.", "172.19.",
                     "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                     "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                     "172.30.", "172.31.", "192.168.", "0.", "169.254.")
_BLOCKED_HOSTS = ("localhost", "metadata.google.internal")
_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
_MAX_RESPONSE_BYTES = 1_048_576  # 1 MB


def _is_blocked_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if host in _BLOCKED_HOSTS:
        return True
    return any(host.startswith(prefix) for prefix in _BLOCKED_NETWORKS)


class HttpRequestExecutor(BaseNodeExecutor):
    def execute(
        self,
        node_id: str,
        config: dict[str, Any],
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> NodeResult:
        url = config.get("url", "").strip()
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body")
        timeout = min(config.get("timeout", 30), 60)

        if not url:
            return NodeResult(node_id=node_id, status="failed", error="URL is required.")

        if method not in _ALLOWED_METHODS:
            return NodeResult(
                node_id=node_id, status="failed",
                error=f"Unsupported method: {method}",
            )

        if _is_blocked_url(url):
            return NodeResult(
                node_id=node_id, status="failed",
                error="Requests to private/loopback addresses are blocked.",
            )

        try:
            with httpx.Client(timeout=timeout, max_redirects=5) as client:
                resp = client.request(method, url, headers=headers, json=body)
        except httpx.TimeoutException:
            return NodeResult(node_id=node_id, status="failed", error="Request timed out.")
        except Exception as exc:
            return NodeResult(node_id=node_id, status="failed", error=str(exc))

        response_text = resp.text[:_MAX_RESPONSE_BYTES]
        try:
            response_body = resp.json()
        except Exception:
            response_body = response_text

        return NodeResult(
            node_id=node_id,
            status="completed",
            output={
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "body": response_body,
            },
        )


register_executor("http_request", HttpRequestExecutor())
