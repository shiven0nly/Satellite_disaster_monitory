from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ImageType, JobStatus
from app.schemas.result import ResultRead


class JobBase(BaseModel):
    image_url: str = Field(..., example="https://storage.provider.com/images/sat_01.jpg")
    image_type: ImageType = Field(default=ImageType.OTHER)


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    image_url: Optional[str] = None
    image_type: Optional[ImageType] = None
    status: Optional[JobStatus] = None
    error_message: Optional[str] = None


class JobRead(JobBase):
    id: UUID
    status: JobStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    result: Optional[ResultRead] = None

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    total: int = Field(..., example=42)
    skip: int = Field(..., example=0)
    limit: int = Field(..., example=20)
    jobs: List[JobRead]
