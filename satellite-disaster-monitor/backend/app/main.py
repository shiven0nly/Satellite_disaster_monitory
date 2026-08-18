import io
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from app.schemas import AnalysisResponse, HealthResponse, ErrorResponse, HistoryListResponse
from app.model import analyze_multimodal_images, analyze_landslide_images
from app.llm_service import explain_prediction
from app.history import add_to_history, get_history, clear_history

logger = logging.getLogger(__name__)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per file limit

app = FastAPI(
    title="Satellite Disaster Monitoring API",
    version="0.2.0",
    description="FastAPI service for Flood & Landslide disaster assessment using trained ML models"
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
    model_type: Optional[str] = Form("auto"),
    optical_file: Optional[UploadFile] = File(None),
    sar_file: Optional[UploadFile] = File(None),
    thermal_file: Optional[UploadFile] = File(None),
    landslide_optical_file: Optional[UploadFile] = File(None),
    landslide_dem_file: Optional[UploadFile] = File(None),
    landslide_sar_file: Optional[UploadFile] = File(None),
):
    """Accepts satellite images for Flood or Landslide detection, runs trained ML models, and generates Groq LLM assessment."""
    
    is_landslide_request = (
        model_type == "landslide" or
        landslide_optical_file is not None or
        landslide_dem_file is not None or
        landslide_sar_file is not None
    )

    if is_landslide_request:
        # Landslide ML Pipeline
        active_landslide_files = {
            "Landslide Optical": landslide_optical_file or optical_file,
            "DEM Elevation": landslide_dem_file or sar_file,
            "SAR Slope Texture": landslide_sar_file or thermal_file
        }
        active_files = {name: f for name, f in active_landslide_files.items() if f is not None and f.filename}

        if not active_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one landslide imagery file (Optical, DEM, or SAR) must be uploaded."
            )

        image_bytes_dict = {}
        filenames_used = []

        for sensor_name, file in active_files.items():
            try:
                raw_bytes = await file.read()
                if len(raw_bytes) > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{sensor_name} file exceeds 20MB limit."
                    )
                img = Image.open(io.BytesIO(raw_bytes))
                img.verify()
                image_bytes_dict[sensor_name] = raw_bytes
                filenames_used.append(f"{sensor_name}: {file.filename}")
            except HTTPException:
                raise
            except Exception as err:
                logger.error(f"Error validating {sensor_name}: {err}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{sensor_name} file '{file.filename}' is corrupted or invalid."
                )

        try:
            prediction_dict = analyze_landslide_images(
                optical_bytes=image_bytes_dict.get("Landslide Optical"),
                dem_bytes=image_bytes_dict.get("DEM Elevation"),
                sar_bytes=image_bytes_dict.get("SAR Slope Texture")
            )

            explanation = explain_prediction(prediction_dict)

            filename_str = "[Landslide Model] " + ", ".join(filenames_used)
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
            logger.exception(f"Internal error during landslide analysis: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status": "error", "detail": f"Landslide analysis error: {str(e)}"}
            )
    else:
        # Flood ML Pipeline
        active_flood_files = {
            "Optical": optical_file,
            "SAR": sar_file,
            "Thermal IR": thermal_file
        }
        active_files = {name: f for name, f in active_flood_files.items() if f is not None and f.filename}

        if not active_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one satellite image must be provided for analysis."
            )

        image_bytes_dict = {}
        filenames_used = []

        for sensor_name, file in active_files.items():
            try:
                raw_bytes = await file.read()
                if len(raw_bytes) > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{sensor_name} file exceeds 20MB limit."
                    )
                img = Image.open(io.BytesIO(raw_bytes))
                img.verify()
                image_bytes_dict[sensor_name] = raw_bytes
                filenames_used.append(f"{sensor_name}: {file.filename}")
            except HTTPException:
                raise
            except Exception as err:
                logger.error(f"Error validating {sensor_name}: {err}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{sensor_name} file '{file.filename}' is corrupted or invalid."
                )

        try:
            prediction_dict = analyze_multimodal_images(
                optical_bytes=image_bytes_dict.get("Optical"),
                sar_bytes=image_bytes_dict.get("SAR"),
                thermal_bytes=image_bytes_dict.get("Thermal IR")
            )

            explanation = explain_prediction(prediction_dict)

            filename_str = "[Flood Model] " + ", ".join(filenames_used)
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
            logger.exception(f"Internal error during flood analysis: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status": "error", "detail": f"Flood analysis error: {str(e)}"}
            )
