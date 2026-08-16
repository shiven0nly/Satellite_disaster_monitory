import os
import requests
from typing import Dict, Any, Tuple, List

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
    optical_bytes: bytes,
    optical_name: str,
    optical_mime: str,
    sar_bytes: bytes,
    sar_name: str,
    sar_mime: str,
    thermal_bytes: bytes,
    thermal_name: str,
    thermal_mime: str,
    backend_url: str = DEFAULT_BACKEND_URL,
) -> Tuple[bool, Dict[str, Any]]:
    """POST three multi-modal satellite images to backend POST /analyze.

    Returns:
        Tuple[bool, Dict[str, Any]]: (success, response_data_or_error_dict)
    """
    url = f"{backend_url.rstrip('/')}/analyze"
    files = {
        "optical_file":  (optical_name,  optical_bytes,  optical_mime),
        "sar_file":      (sar_name,       sar_bytes,      sar_mime),
        "thermal_file":  (thermal_name,   thermal_bytes,  thermal_mime),
    }
    try:
        response = requests.post(url, files=files, timeout=60)
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
