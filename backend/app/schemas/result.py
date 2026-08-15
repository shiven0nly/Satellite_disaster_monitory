from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SeverityLevel


class ResultBase(BaseModel):
    disaster_type: str = Field(..., example="Wildfire")
    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM)
    affected_area_estimate: Optional[str] = Field(None, example="15.5 sq km")
    description: Optional[str] = Field(None, example="Active wildfire detected moving northeast.")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, example=0.94)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, example=34.0522)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, example=-118.2437)
    raw_model_output: Optional[Dict[str, Any]] = Field(None, description="Raw JSON data output from ML model/LLM")


class ResultCreate(ResultBase):
    job_id: UUID


class ResultUpdate(BaseModel):
    disaster_type: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    affected_area_estimate: Optional[str] = None
    description: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    raw_model_output: Optional[Dict[str, Any]] = None


class ParsedResult(ResultBase):
    """
    Structured assessment output produced by LLM parsing from ML model predictions.
    """
    model_config = ConfigDict(from_attributes=True)


class ResultRead(ResultBase):
    id: UUID
    job_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
