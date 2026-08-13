import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Worker(Base):
    __tablename__ = "workers"

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    employee_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    tag_id: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
    )

    face_embeddings = relationship(
        "FaceEmbedding",
        back_populates="worker",
    )

    attendance_records = relationship(
        "AttendanceRecord",
        back_populates="worker",
    )

    ppe_logs = relationship(
        "PPEComplianceLog",
        back_populates="worker",
    )