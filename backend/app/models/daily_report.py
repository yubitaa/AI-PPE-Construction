import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailyReport(Base):
    __tablename__ = "daily_reports"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    report_date: Mapped[date] = mapped_column(
        Date,
        unique=True,
        nullable=False,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    attendance_summary: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    ppe_summary: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    compliance_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    report_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )