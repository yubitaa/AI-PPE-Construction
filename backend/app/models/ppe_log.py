import enum
import uuid

from sqlalchemy import Boolean, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PPEStatus(str, enum.Enum):
    FULL_PPE = "FULL_PPE"
    HELMET_MISSING = "HELMET_MISSING"
    VEST_MISSING = "VEST_MISSING"
    NO_PPE = "NO_PPE"


class PPEComplianceLog(Base):
    __tablename__ = "ppe_compliance_logs"

    log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workers.worker_id", ondelete="RESTRICT"),
        nullable=False,
    )

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("video_sources.video_id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Position in the pre-recorded video, measured in seconds.
    start_timestamp: Mapped[float] = mapped_column(
    Float,
    nullable=False,
    )

    end_timestamp: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    helmet_detected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    vest_detected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    compliance_status: Mapped[PPEStatus] = mapped_column(
        Enum(
            PPEStatus,
            name="ppe_status_enum",
        ),
        nullable=False,
    )

    worker = relationship(
        "Worker",
        back_populates="ppe_logs",
    )

    video = relationship(
        "VideoSource",
        back_populates="ppe_logs",
    )