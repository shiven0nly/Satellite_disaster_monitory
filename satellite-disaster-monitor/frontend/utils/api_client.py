import os
import requests
from typing import Dict, Any, Tuple, List

DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def check_backend_health(backend_url: str = DEFAULT_BACKEND_URL) -> bool:
    """Check health status of the backend FastAPI service."""
    try:
        url = f"{backend_url.rstrip('/')}/health"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("status") == "ok"
        return False
    except Exception:
        return False

def analyze_image(file_bytes: bytes, filename: str, mime_type: str, backend_url: str = DEFAULT_BACKEND_URL) -> Tuple[bool, Dict[str, Any]]:
    """POST satellite image bytes to backend /analyze endpoint."""
    url = f"{backend_url.rstrip('/')}/analyze"
    files = {"file": (filename, file_bytes, mime_type)}
    
    try:
        response = requests.post(url, files=files, timeout=30)
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
        return False, {"error": "Request timed out after 30 seconds."}
    except Exception as e:
        return False, {"error": f"An unexpected error occurred: {str(e)}"}

def fetch_history(backend_url: str = DEFAULT_BACKEND_URL) -> Tuple[bool, List[Dict[str, Any]]]:
    """Fetch all stored analysis reports from backend GET /history endpoint."""
    url = f"{backend_url.rstrip('/')}/history"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True, response.json().get("history", [])
        return False, []
    except Exception:
        return False, []

def clear_backend_history(backend_url: str = DEFAULT_BACKEND_URL) -> bool:
    """Clear all analysis history on backend DELETE /history endpoint."""
    url = f"{backend_url.rstrip('/')}/history"
    try:
        response = requests.delete(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False
