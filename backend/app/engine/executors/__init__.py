"""Auto-import all executor modules so they self-register."""

from app.engine.executors import (  # noqa: F401
    condition,
    http_request,
    manual_trigger,
    send_email,
    send_notification,
    transform,
    write_spreadsheet,
)
