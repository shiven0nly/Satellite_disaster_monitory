from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
from PIL import Image

from app.schemas import AnalysisResponse, HealthResponse, ErrorResponse, HistoryListResponse
from app.model import analyze_image
from app.llm_service import explain_prediction
from app.history import add_to_history, get_history, clear_history

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

app = FastAPI(
    title="Satellite Disaster Monitoring API",
    version="0.1.0",
    description="FastAPI service for satellite image analysis and disaster assessment"
)

# CORS Middleware allowing Streamlit frontend and local clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Service health check endpoint."""
    return HealthResponse(status="ok")

@app.get("/history", response_model=HistoryListResponse)
def get_analysis_history():
    """Retrieve all past satellite image analysis reports."""
    records = get_history()
    return HistoryListResponse(history=records, total=len(records))

@app.delete("/history")
def delete_analysis_history():
    """Clear all stored analysis history."""
    clear_history()
    return {"status": "success", "message": "Analysis history cleared"}

@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image payload or size limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal analysis error"}
    }
)
async def analyze_disaster_image(file: UploadFile = File(...)):
    """Accepts an uploaded satellite image, performs analysis, generates LLM brief, and saves report to history."""
    # 1. Content-Type check
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid image. Must be image/* content type."
        )

    try:
        # 2. Read bytes in-memory and validate file size
        image_bytes = await file.read()
        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE // (1024 * 1024)}MB."
            )
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        # 3. Validate image with PIL (in-memory)
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid image or is corrupted."
        )

    try:
        # 4. Model inference
        prediction_dict = analyze_image(image_bytes)
        
        # 5. LLM explanation call
        explanation = explain_prediction(prediction_dict)

        # 6. Save report to backend history store
        history_record = add_to_history(
            filename=file.filename or "satellite_image.jpg",
            prediction=prediction_dict,
            explanation=explanation
        )

        # 7. Structured Pydantic response with history record
        return AnalysisResponse(
            prediction=prediction_dict,
            explanation=explanation,
            status="success",
            history_record=history_record
        )
    except Exception as e:
        # Prevent stack trace leakage to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "detail": "Internal server error while analyzing satellite image."}
        )
