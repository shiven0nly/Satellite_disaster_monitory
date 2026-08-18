from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class BandStats(BaseModel):
    mean_intensity: float = 0.0
    hotspot_ratio: float = 0.0
    water_pixel_ratio: float = 0.0
    sar_mean_db: float = 0.0
    anomaly_score: float = 0.0

class ImagesAnalyzed(BaseModel):
    optical: str = "Optical RGB image provided"
    sar: str = "SAR radar imagery provided"
    thermal_ir: str = "Thermal Infrared imagery provided"

class PredictionResult(BaseModel):
    disaster_type: str = "flood"
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    severity: str = "medium"
    image_type_detected: str = "Multi-Modal"
    flood_coverage_percentage: Optional[float] = None
    optical_water_index_ndwi: Optional[float] = None
    sar_backscatter_score: Optional[float] = None
    images_analyzed: Optional[ImagesAnalyzed] = None
    band_stats: BandStats = Field(default_factory=BandStats)

class HistoryRecord(BaseModel):
    id: str
    filename: str
    timestamp: str
    prediction: Dict[str, Any]
    explanation: str

class AnalysisResponse(BaseModel):
    prediction: Dict[str, Any]
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
