"""fix user password hash nullable

Revision ID: e2acc126a6ac
Revises: ae14ba9d2a6a
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e2acc126a6ac"
down_revision: Union[str, Sequence[str], None] = "ae14ba9d2a6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", recreate="always") as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=255),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("users", recreate="always") as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=255),
            nullable=True,
        )