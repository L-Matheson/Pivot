"""Write Spreadsheet executor — appends rows via Google Sheets API."""

import json
from typing import Any

from app.engine.base import BaseNodeExecutor, ExecutionContext, NodeResult
from app.engine.executors._google_helpers import (
    CredentialError,
    get_google_credentials,
    google_api_request,
)
from app.engine.registry import register_executor

SHEETS_APPEND_URL = (
    "https://sheets.googleapis.com/v4/spreadsheets"
    "/{spreadsheet_id}/values/{range}:append"
    "?valueInputOption=USER_ENTERED"
)


class WriteSpreadsheetExecutor(BaseNodeExecutor):
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

        spreadsheet_id = config.get("spreadsheet_id", "")
        sheet_name = config.get("sheet_name", "Sheet1")
        values = config.get("values", [])

        if not values and config.get("values_json"):
            try:
                values = json.loads(config["values_json"])
            except (json.JSONDecodeError, TypeError):
                return NodeResult(
                    node_id=node_id,
                    status="failed",
                    error="values_json is not valid JSON.",
                )

        if not spreadsheet_id:
            return NodeResult(
                node_id=node_id,
                status="failed",
                error="spreadsheet_id is required.",
            )

        if not values:
            return NodeResult(
                node_id=node_id,
                status="failed",
                error="values list is required.",
            )

        # Normalize: a flat list becomes a single row
        if values and not isinstance(values[0], list):
            values = [values]

        try:
            access_token, conn = get_google_credentials(connection_id, context)
        except CredentialError as exc:
            return NodeResult(
                node_id=node_id, status="failed", error=str(exc)
            )

        url = SHEETS_APPEND_URL.format(
            spreadsheet_id=spreadsheet_id,
            range=f"{sheet_name}!A1",
        )

        try:
            result = google_api_request(
                method="POST",
                url=url,
                access_token=access_token,
                body={"values": values},
                connection=conn,
                context=context,
            )
        except Exception as exc:
            return NodeResult(
                node_id=node_id, status="failed", error=str(exc)
            )

        updates = result.get("updates", {})
        return NodeResult(
            node_id=node_id,
            status="completed",
            output={
                "updated_range": updates.get("updatedRange", ""),
                "updated_rows": updates.get("updatedRows", 0),
                "updated_cells": updates.get("updatedCells", 0),
            },
        )


register_executor("write_spreadsheet", WriteSpreadsheetExecutor())
