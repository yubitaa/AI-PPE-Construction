"""update_ppe_compliance_logs_timestamps

Revision ID: <NEW_REVISION_ID>
Revises: 84c2666ad27e
Create Date: 2026-08-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '<NEW_REVISION_ID>' # Keep the auto-generated ID here
down_revision: Union[str, None] = '84c2666ad27e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add start_timestamp and end_timestamp columns
    op.add_column('ppe_compliance_logs', sa.Column('start_timestamp', sa.DateTime(timezone=True), nullable=True))
    op.add_column('ppe_compliance_logs', sa.Column('end_timestamp', sa.DateTime(timezone=True), nullable=True))

    # 2. Convert Unix epoch numbers (double precision) to timestamptz
    op.execute(
        "UPDATE ppe_compliance_logs "
        "SET start_timestamp = to_timestamp(timestamp), "
        "    end_timestamp = to_timestamp(timestamp)"
    )

    # 3. Enforce NOT NULL on start_timestamp
    op.alter_column('ppe_compliance_logs', 'start_timestamp', nullable=False)

    # 4. Drop the old float timestamp column
    op.drop_column('ppe_compliance_logs', 'timestamp')


def downgrade() -> None:
    # 1. Re-add timestamp column as double precision
    op.add_column('ppe_compliance_logs', sa.Column('timestamp', sa.Float(), nullable=True))

    # 2. Convert timestamptz back to epoch float
    op.execute(
        "UPDATE ppe_compliance_logs "
        "SET timestamp = EXTRACT(EPOCH FROM start_timestamp)"
    )

    # 3. Enforce NOT NULL on timestamp
    op.alter_column('ppe_compliance_logs', 'timestamp', nullable=False)

    # 4. Drop start_timestamp and end_timestamp
    op.drop_column('ppe_compliance_logs', 'end_timestamp')
    op.drop_column('ppe_compliance_logs', 'start_timestamp')