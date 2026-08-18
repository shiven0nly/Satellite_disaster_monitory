import io
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from app.schemas import AnalysisResponse, HealthResponse, ErrorResponse, HistoryListResponse
from app.model import analyze_multimodal_images
from app.llm_service import explain_prediction
from app.history import add_to_history, get_history, clear_history

logger = logging.getLogger(__name__)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per file limit

app = FastAPI(
    title="Satellite Disaster Monitoring API",
    version="0.1.0",
    description="FastAPI service for satellite image disaster assessment (Single & Multi-Modal)"
)

# CORS Middleware
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
async def analyze_disaster_images(
    optical_file: Optional[UploadFile] = File(None),
    sar_file: Optional[UploadFile] = File(None),
    thermal_file: Optional[UploadFile] = File(None)
):
    """Accepts 1, 2, or 3 satellite images (Optical, SAR, Thermal IR), performs model inference, and generates Groq LLM assessment."""
    
    # 1. Ensure at least one image is uploaded
    provided_files = {
        "Optical": optical_file,
        "SAR": sar_file,
        "Thermal IR": thermal_file
    }
    active_files = {name: file for name, file in provided_files.items() if file is not None and file.filename}

    if not active_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one satellite image (Optical, SAR, or Thermal IR) must be provided for analysis."
        )

    image_bytes_dict = {}
    filenames_used = []

    # 2. Read and validate provided images
    for sensor_name, file in active_files.items():
        try:
            raw_bytes = await file.read()
            if len(raw_bytes) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{sensor_name} file exceeds 20MB maximum size limit."
                )
            if len(raw_bytes) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{sensor_name} file is empty."
                )

            # In-memory PIL validation
            img = Image.open(io.BytesIO(raw_bytes))
            img.verify()
            image_bytes_dict[sensor_name] = raw_bytes
            filenames_used.append(f"{sensor_name}: {file.filename}")
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error validating {sensor_name} image: {err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{sensor_name} file '{file.filename}' is not a valid image format."
            )

    try:
        # 3. Model inference (with single/multi image fallback)
        prediction_dict = analyze_multimodal_images(
            optical_bytes=image_bytes_dict.get("Optical"),
            sar_bytes=image_bytes_dict.get("SAR"),
            thermal_bytes=image_bytes_dict.get("Thermal IR")
        )

        # 4. Groq LLM assessment brief
        explanation = explain_prediction(prediction_dict)

        # 5. Store history
        filename_str = ", ".join(filenames_used)
        history_record = add_to_history(
            filename=filename_str,
            prediction=prediction_dict,
            explanation=explanation
        )

        return AnalysisResponse(
            prediction=prediction_dict,
            explanation=explanation,
            status="success",
            history_record=history_record
        )
    except Exception as e:
        logger.exception(f"Internal error during disaster analysis: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "detail": f"Analysis error: {str(e)}"}
        )
