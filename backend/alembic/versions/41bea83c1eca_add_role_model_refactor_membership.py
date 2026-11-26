"""add_role_model_refactor_membership

Revision ID: 41bea83c1eca
Revises: 4dcc53de8d88
Create Date: 2026-11-26 16:35:08.667151

"""

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes  # noqa: F401
from sqlalchemy.dialects import postgresql

revision: str = "41bea83c1eca"
down_revision: str | Sequence[str] | None = "4dcc53de8d88"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
MEMBER_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


def upgrade() -> None:
    role_table = op.create_table(
        "role",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column(
            "name",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=False,
        ),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column(
            "permissions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_role_workspace_id"), "role", ["workspace_id"], unique=False
    )

    now = datetime.now(timezone.utc)
    op.bulk_insert(
        role_table,
        [
            {
                "id": ADMIN_ROLE_ID,
                "workspace_id": None,
                "name": "admin",
                "is_system": True,
                "permissions": {},
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": MEMBER_ROLE_ID,
                "workspace_id": None,
                "name": "member",
                "is_system": True,
                "permissions": {
                    "automations": {
                        "view": ["*"],
                        "edit": False,
                        "execute": False,
                        "manage": False,
                    },
                    "connections": {"view": True, "manage": False},
                    "members": {"view": True, "manage": False},
                    "settings": {"view": False, "manage": False},
                    "stats": {"view": True},
                },
                "created_at": now,
                "updated_at": now,
            },
        ],
    )

    op.add_column(
        "workspacemembership",
        sa.Column("role_id", sa.Uuid(), nullable=True),
    )

    op.execute(
        sa.text(
            f"UPDATE workspacemembership SET role_id = '{ADMIN_ROLE_ID}' "
            "WHERE role = 'owner'"
        )
    )
    op.execute(
        sa.text(
            f"UPDATE workspacemembership SET role_id = '{MEMBER_ROLE_ID}' "
            "WHERE role IN ('editor', 'viewer')"
        )
    )
    op.execute(
        sa.text(
            f"UPDATE workspacemembership SET role_id = '{MEMBER_ROLE_ID}' "
            "WHERE role_id IS NULL"
        )
    )

    op.alter_column("workspacemembership", "role_id", nullable=False)

    op.create_foreign_key(
        "fk_workspacemembership_role_id",
        "workspacemembership",
        "role",
        ["role_id"],
        ["id"],
    )

    op.drop_column("workspacemembership", "role")

    workspacerole = postgresql.ENUM(
        "owner", "editor", "viewer", name="workspacerole"
    )
    workspacerole.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    workspacerole = postgresql.ENUM(
        "owner", "editor", "viewer", name="workspacerole", create_type=True
    )
    workspacerole.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "workspacemembership",
        sa.Column("role", workspacerole, nullable=True),
    )

    op.execute(
        sa.text(
            f"UPDATE workspacemembership SET role = 'owner' "
            f"WHERE role_id = '{ADMIN_ROLE_ID}'"
        )
    )
    op.execute(
        sa.text(
            f"UPDATE workspacemembership SET role = 'viewer' "
            f"WHERE role_id = '{MEMBER_ROLE_ID}'"
        )
    )
    op.execute(
        sa.text(
            "UPDATE workspacemembership SET role = 'viewer' WHERE role IS NULL"
        )
    )

    op.alter_column("workspacemembership", "role", nullable=False)

    op.drop_constraint(
        "fk_workspacemembership_role_id",
        "workspacemembership",
        type_="foreignkey",
    )
    op.drop_column("workspacemembership", "role_id")
    op.drop_index(op.f("ix_role_workspace_id"), table_name="role")
    op.drop_table("role")
