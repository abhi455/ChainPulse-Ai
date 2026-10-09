"""add encrypted connection secrets

Revision ID: 83c2d4e5f601
Revises: 7b4b5d6e9c10
"""

from alembic import op
import sqlalchemy as sa

revision = "83c2d4e5f601"
down_revision = "7b4b5d6e9c10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "data_connections",
        sa.Column(
            "secret_config",
            sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "data_connections",
        "secret_config",
    )
