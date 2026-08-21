import os
from typing import Any, Dict, List, Optional, Tuple
import requests

DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def check_backend_health(backend_url: str = DEFAULT_BACKEND_URL) -> bool:
    """Check health status of the backend FastAPI service."""
    try:
        response = requests.get(f"{backend_url.rstrip('/')}/health", timeout=5)
        if response.status_code == 200:
            return response.json().get("status") == "ok"
        return False
    except Exception:
        return False


def analyze_image(
    model_type: str = "flood",
    optical_bytes: Optional[bytes] = None,
    optical_name: Optional[str] = None,
    optical_mime: Optional[str] = None,
    sar_bytes: Optional[bytes] = None,
    sar_name: Optional[str] = None,
    sar_mime: Optional[str] = None,
    landslide_optical_bytes: Optional[bytes] = None,
    landslide_optical_name: Optional[str] = None,
    landslide_optical_mime: Optional[str] = None,
    landslide_dem_bytes: Optional[bytes] = None,
    landslide_dem_name: Optional[str] = None,
    landslide_dem_mime: Optional[str] = None,
    wildfire_optical_bytes: Optional[bytes] = None,
    wildfire_optical_name: Optional[str] = None,
    wildfire_optical_mime: Optional[str] = None,
    wildfire_sar_bytes: Optional[bytes] = None,
    wildfire_sar_name: Optional[str] = None,
    wildfire_sar_mime: Optional[str] = None,
    backend_url: str = DEFAULT_BACKEND_URL,
) -> Tuple[bool, Dict[str, Any]]:
    """POST satellite images to backend POST /analyze for Flood, Landslide, Wildfire, or Drought detection."""
    url = f"{backend_url.rstrip('/')}/analyze"
    files = {}
    data = {"disaster_type": model_type.lower()}

    # Select primary input file and optional secondary file (sentinel2 for flood)
    primary_bytes, primary_name, primary_mime = None, None, None
    sentinel2_bytes, sentinel2_name, sentinel2_mime = None, None, None

    if model_type == "wildfire":
        if wildfire_optical_bytes and wildfire_optical_name:
            primary_bytes, primary_name, primary_mime = wildfire_optical_bytes, wildfire_optical_name, wildfire_optical_mime
        elif wildfire_sar_bytes and wildfire_sar_name:
            primary_bytes, primary_name, primary_mime = wildfire_sar_bytes, wildfire_sar_name, wildfire_sar_mime
    elif model_type == "landslide":
        if landslide_optical_bytes and landslide_optical_name:
            primary_bytes, primary_name, primary_mime = landslide_optical_bytes, landslide_optical_name, landslide_optical_mime
        elif landslide_dem_bytes and landslide_dem_name:
            primary_bytes, primary_name, primary_mime = landslide_dem_bytes, landslide_dem_name, landslide_dem_mime
    else:  # flood / drought
        if optical_bytes and optical_name:
            primary_bytes, primary_name, primary_mime = optical_bytes, optical_name, optical_mime
        elif sar_bytes and sar_name:
            primary_bytes, primary_name, primary_mime = sar_bytes, sar_name, sar_mime

        if sar_bytes and sar_name and optical_bytes and optical_name:
            # If both uploaded for flood, send optical as sentinel2
            sentinel2_bytes, sentinel2_name, sentinel2_mime = sar_bytes, sar_name, sar_mime

    if not primary_bytes or not primary_name:
        return False, {"error": f"Please upload a valid satellite image for {model_type.upper()} detection."}

    files["file"] = (primary_name, primary_bytes, primary_mime or "image/tiff")
    if sentinel2_bytes and sentinel2_name:
        files["sentinel2"] = (sentinel2_name, sentinel2_bytes, sentinel2_mime or "image/tiff")

    try:
        response = requests.post(url, files=files, data=data, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        try:
            err_detail = response.json().get("detail", "Server returned an error.")
        except Exception:
            err_detail = f"HTTP Error {response.status_code}: {response.text}"
        return False, {"error": err_detail}
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Cannot reach backend at {backend_url}. Is it running?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timed out after 60 seconds."}
    except Exception as e:
        return False, {"error": f"An unexpected error occurred: {str(e)}"}


def fetch_history(backend_url: str = DEFAULT_BACKEND_URL) -> Tuple[bool, List[Dict[str, Any]]]:
    """Fetch all stored analysis reports from GET /history."""
    try:
        response = requests.get(f"{backend_url.rstrip('/')}/history", timeout=10)
        if response.status_code == 200:
            return True, response.json().get("history", [])
        return False, []
    except Exception:
        return False, []


def clear_backend_history(backend_url: str = DEFAULT_BACKEND_URL) -> bool:
    """Clear all analysis history via DELETE /history."""
    try:
        response = requests.delete(f"{backend_url.rstrip('/')}/history", timeout=5)
        return response.status_code == 200
    except Exception:
        return False
