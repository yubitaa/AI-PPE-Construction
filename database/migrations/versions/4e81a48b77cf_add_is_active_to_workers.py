"""add is_active to workers

Revision ID: 4e81a48b77cf
Revises: a6b22d9e7c6e
Create Date: 2026-09-13 19:24:19.441192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e81a48b77cf'
down_revision: Union[str, Sequence[str], None] = 'a6b22d9e7c6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "workers",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column("workers", "is_active")