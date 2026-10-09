"""add data connections

Revision ID: 7b4b5d6e9c10
Revises: f31c4f82a771
"""

from alembic import op
import sqlalchemy as sa


revision = "7b4b5d6e9c10"
down_revision = "f31c4f82a771"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "data_connections",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "connector_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "config",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "last_tested_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "last_refreshed_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_data_connections_organization_id",
        "data_connections",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_data_connections_connector_type",
        "data_connections",
        ["connector_type"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_data_connections_connector_type",
        table_name="data_connections",
    )

    op.drop_index(
        "ix_data_connections_organization_id",
        table_name="data_connections",
    )

    op.drop_table("data_connections")
