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
    thermal_bytes: Optional[bytes] = None,
    thermal_name: Optional[str] = None,
    thermal_mime: Optional[str] = None,
    landslide_optical_bytes: Optional[bytes] = None,
    landslide_optical_name: Optional[str] = None,
    landslide_optical_mime: Optional[str] = None,
    landslide_dem_bytes: Optional[bytes] = None,
    landslide_dem_name: Optional[str] = None,
    landslide_dem_mime: Optional[str] = None,
    landslide_sar_bytes: Optional[bytes] = None,
    landslide_sar_name: Optional[str] = None,
    landslide_sar_mime: Optional[str] = None,
    backend_url: str = DEFAULT_BACKEND_URL,
) -> Tuple[bool, Dict[str, Any]]:
    """POST satellite images to backend POST /analyze for Flood or Landslide detection."""
    url = f"{backend_url.rstrip('/')}/analyze"
    files = {}
    data = {"model_type": model_type}

    if model_type == "landslide":
        if landslide_optical_bytes and landslide_optical_name:
            files["landslide_optical_file"] = (landslide_optical_name, landslide_optical_bytes, landslide_optical_mime or "image/jpeg")
        if landslide_dem_bytes and landslide_dem_name:
            files["landslide_dem_file"] = (landslide_dem_name, landslide_dem_bytes, landslide_dem_mime or "image/jpeg")
        if landslide_sar_bytes and landslide_sar_name:
            files["landslide_sar_file"] = (landslide_sar_name, landslide_sar_bytes, landslide_sar_mime or "image/jpeg")
    else:
        if optical_bytes and optical_name:
            files["optical_file"] = (optical_name, optical_bytes, optical_mime or "image/jpeg")
        if sar_bytes and sar_name:
            files["sar_file"] = (sar_name, sar_bytes, sar_mime or "image/jpeg")
        if thermal_bytes and thermal_name:
            files["thermal_file"] = (thermal_name, thermal_bytes, thermal_mime or "image/jpeg")

    if not files:
        return False, {"error": f"Please upload at least one satellite image for {model_type.upper()} detection."}

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
