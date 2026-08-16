from fastapi import FastAPI
from app.schemas import AnalysisResponse

app = FastAPI(title="Satellite Disaster Monitoring Backend", version="0.1.0")

@app.get("/")
def read_root():
    return {"status": "online", "system": "Satellite Disaster Monitoring API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
