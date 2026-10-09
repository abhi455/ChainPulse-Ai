"""add user authentication fields

Revision ID: ae14ba9d2a6a
Revises: e044bb8cc159
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ae14ba9d2a6a"
down_revision: Union[str, Sequence[str], None] = "e044bb8cc159"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "password_hash" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "password_hash",
                sa.String(length=255),
                nullable=False,
                server_default="",
            ),
        )

    if "is_active" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "is_active" in columns:
        op.drop_column("users", "is_active")

    if "password_hash" in columns:
        op.drop_column("users", "password_hash")
