"""add_role_full_access

Revision ID: c60bdfb2610f
Revises: ff7aef69e032
Create Date: 2026-11-26 17:01:54.420837

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "c60bdfb2610f"
down_revision: str | Sequence[str] | None = "ff7aef69e032"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "role",
        sa.Column(
            "full_access",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.execute(
        sa.text(
            "UPDATE role SET full_access = true "
            "WHERE is_system = true AND name = 'admin'"
        )
    )


def downgrade() -> None:
    op.drop_column("role", "full_access")
