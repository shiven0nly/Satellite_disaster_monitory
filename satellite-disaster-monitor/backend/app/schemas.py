from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class BandStats(BaseModel):
    mean_intensity: float
    hotspot_ratio: float
    anomaly_score: float

class ImagesAnalyzed(BaseModel):
    optical: str = "Optical RGB image provided"
    sar: str = "SAR radar imagery provided"
    thermal_ir: str = "Thermal Infrared imagery provided"

class PredictionResult(BaseModel):
    disaster_type: Literal["flood", "wildfire", "cyclone", "earthquake_damage", "none_detected"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: Literal["low", "moderate", "high", "critical"]
    image_type_detected: str       # e.g. "Multi-Modal (Optical + SAR + Thermal IR)"
    images_analyzed: Optional[ImagesAnalyzed] = None
    band_stats: BandStats

class HistoryRecord(BaseModel):
    id: str
    filename: str
    timestamp: str
    prediction: PredictionResult
    explanation: str

class AnalysisResponse(BaseModel):
    prediction: PredictionResult
    explanation: str
    status: str = "success"
    history_record: Optional[HistoryRecord] = None

class HistoryListResponse(BaseModel):
    history: List[HistoryRecord]
    total: int

class HealthResponse(BaseModel):
    status: str = "ok"

class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str
