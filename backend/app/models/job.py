import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SQLEnum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ImageType, JobStatus

if TYPE_CHECKING:
    from app.models.result import Result


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    image_type: Mapped[ImageType] = mapped_column(
        SQLEnum(ImageType, name="image_type_enum"),
        nullable=False,
        default=ImageType.OTHER,
    )
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, name="job_status_enum"),
        nullable=False,
        default=JobStatus.PENDING,
        index=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship to result
    result: Mapped[Optional["Result"]] = relationship(
        "Result",
        back_populates="job",
        cascade="all, delete-orphan",
        uselist=False,
    )
