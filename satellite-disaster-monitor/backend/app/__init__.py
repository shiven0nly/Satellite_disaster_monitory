from fastapi import FastAPI

app = FastAPI(title="Satellite Disaster Monitoring API")

@app.get("/")
def read_root():
    return {"message": "Satellite Disaster Monitoring API is active"}
