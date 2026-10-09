"""add multi provider authentication

Revision ID: f31c4f82a771
Revises: e2acc126a6ac
"""

from alembic import op
import sqlalchemy as sa


revision = "f31c4f82a771"
down_revision = "e2acc126a6ac"
branch_labels = None
depends_on = None


def upgrade() -> None:

    with op.batch_alter_table(
        "users",
        schema=None,
    ) as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=255),
            nullable=True,
        )

    op.create_table(
        "user_identities",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "provider",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "provider_subject",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "last_used_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider",
            "provider_subject",
            name="uq_user_identity_provider_subject",
        ),
        sa.UniqueConstraint(
            "user_id",
            "provider",
            name="uq_user_identity_user_provider",
        ),
    )

    op.create_index(
        "ix_user_identities_user_id",
        "user_identities",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_user_identities_provider",
        "user_identities",
        ["provider"],
        unique=False,
    )

    op.create_index(
        "ix_user_identities_email",
        "user_identities",
        ["email"],
        unique=False,
    )

    op.create_table(
        "oauth_login_codes",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "code_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "consumed_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "code_hash",
        ),
    )

    op.create_index(
        "ix_oauth_login_codes_user_id",
        "oauth_login_codes",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_oauth_login_codes_code_hash",
        "oauth_login_codes",
        ["code_hash"],
        unique=True,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_oauth_login_codes_code_hash",
        table_name="oauth_login_codes",
    )

    op.drop_index(
        "ix_oauth_login_codes_user_id",
        table_name="oauth_login_codes",
    )

    op.drop_table(
        "oauth_login_codes"
    )

    op.drop_index(
        "ix_user_identities_email",
        table_name="user_identities",
    )

    op.drop_index(
        "ix_user_identities_provider",
        table_name="user_identities",
    )

    op.drop_index(
        "ix_user_identities_user_id",
        table_name="user_identities",
    )

    op.drop_table(
        "user_identities"
    )

    with op.batch_alter_table(
        "users",
        schema=None,
    ) as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=255),
            nullable=False,
        )
