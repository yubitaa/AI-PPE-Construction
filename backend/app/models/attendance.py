import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    attendance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workers.worker_id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Fixed: Variable renamed to record_date, DB column remains "date"
    record_date: Mapped[date] = mapped_column(
        "date",
        Date,
        nullable=False,
    )

    clock_in: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "worker_id",
            "date", # This refers to the exact DB column name, so it stays "date"
            name="uq_attendance_worker_date",
        ),
    )

    worker = relationship(
        "Worker",
        back_populates="attendance_records",
    )