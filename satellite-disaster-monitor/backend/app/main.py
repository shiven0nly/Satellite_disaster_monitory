from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
from PIL import Image

from app.schemas import AnalysisResponse, HealthResponse, ErrorResponse, HistoryListResponse
from app.model import analyze_multimodal_images
from app.llm_service import explain_prediction
from app.history import add_to_history, get_history, clear_history

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB per file limit

app = FastAPI(
    title="Satellite Disaster Monitoring API",
    version="0.1.0",
    description="FastAPI service for multi-modal satellite image analysis and disaster assessment"
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
    """Retrieve all past multi-modal satellite image analysis reports."""
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
async def analyze_disaster_images(
    optical_file: UploadFile = File(...),
    sar_file: UploadFile = File(...),
    thermal_file: UploadFile = File(...)
):
    """Accepts three multi-modal satellite images (Optical, SAR, Thermal IR), performs model analysis, and generates LLM brief."""
    files_map = {
        "Optical": optical_file,
        "SAR": sar_file,
        "Thermal IR": thermal_file
    }

    image_bytes_dict = {}

    for sensor_name, file in files_map.items():
        # 1. Content-Type check
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{sensor_name} file is not a valid image. Must be image/* content type."
            )

        try:
            # 2. Read bytes in-memory and validate file size
            raw_bytes = await file.read()
            if len(raw_bytes) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{sensor_name} file size exceeds maximum allowed limit of 10MB."
                )
            if len(raw_bytes) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{sensor_name} file is empty."
                )

            # 3. Validate image with PIL (in-memory)
            img = Image.open(io.BytesIO(raw_bytes))
            img.verify()
            image_bytes_dict[sensor_name] = raw_bytes
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{sensor_name} file is not a valid image or is corrupted."
            )

    try:
        # 4. Multi-modal model inference across Optical, SAR, and Thermal IR
        prediction_dict = analyze_multimodal_images(
            optical_bytes=image_bytes_dict["Optical"],
            sar_bytes=image_bytes_dict["SAR"],
            thermal_bytes=image_bytes_dict["Thermal IR"]
        )
        
        # 5. LLM explanation call using prompt_builder system prompt
        explanation = explain_prediction(prediction_dict)

        # 6. Save report to backend history store
        history_record = add_to_history(
            filename=f"Ensemble: {optical_file.filename}, {sar_file.filename}, {thermal_file.filename}",
            prediction=prediction_dict,
            explanation=explanation
        )

        # 7. Structured response
        return AnalysisResponse(
            prediction=prediction_dict,
            explanation=explanation,
            status="success",
            history_record=history_record
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "detail": "Internal server error while analyzing multi-modal satellite images."}
        )
