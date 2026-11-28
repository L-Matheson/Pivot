"""Auto-import all provider modules so they self-register."""

from app.connectors.providers import google_gmail, google_sheets  # noqa: F401
