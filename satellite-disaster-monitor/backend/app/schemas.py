from pydantic import BaseModel
from typing import Optional

class AnalysisResponse(BaseModel):
    status: str
    disaster_type: str
    confidence: float
    affected_area_km2: float
    summary: Optional[str] = None
