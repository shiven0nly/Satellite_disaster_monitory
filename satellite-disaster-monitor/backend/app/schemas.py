from pydantic import BaseModel, Field
from typing import Dict, Literal

class BandStats(BaseModel):
    mean_intensity: float
    hotspot_ratio: float
    anomaly_score: float

class PredictionResult(BaseModel):
    disaster_type: Literal["flood", "wildfire", "cyclone", "earthquake_damage", "none_detected"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: Literal["low", "moderate", "high", "critical"]
    image_type_detected: Literal["IR", "thermal", "RGB", "SAR"]
    band_stats: BandStats

class AnalysisResponse(BaseModel):
    prediction: PredictionResult
    explanation: str
    status: str = "success"

class HealthResponse(BaseModel):
    status: str = "ok"

class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str
