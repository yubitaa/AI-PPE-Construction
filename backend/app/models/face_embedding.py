import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    embedding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workers.worker_id", ondelete="RESTRICT"),
        nullable=False,
    )

    embedding_vector: Mapped[list[float]] = mapped_column(
        VECTOR(512),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    worker = relationship(
        "Worker",
        back_populates="face_embeddings",
    )