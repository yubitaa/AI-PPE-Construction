"""convert PPE timestamps to float video offsets

Revision ID: d7e4f1a2b9c3
Revises: <NEW_REVISION_ID>
Create Date: 2026-09-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7e4f1a2b9c3"
down_revision: Union[str, None] = "<NEW_REVISION_ID>"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "ppe_compliance_logs",
        "start_timestamp",
        type_=sa.Float(),
        postgresql_using="EXTRACT(EPOCH FROM start_timestamp)",
    )
    op.alter_column(
        "ppe_compliance_logs",
        "end_timestamp",
        type_=sa.Float(),
        postgresql_using="EXTRACT(EPOCH FROM end_timestamp)",
    )


def downgrade() -> None:
    op.alter_column(
        "ppe_compliance_logs",
        "start_timestamp",
        type_=sa.DateTime(timezone=True),
        postgresql_using="to_timestamp(start_timestamp)",
    )
    op.alter_column(
        "ppe_compliance_logs",
        "end_timestamp",
        type_=sa.DateTime(timezone=True),
        postgresql_using="to_timestamp(end_timestamp)",
    )
