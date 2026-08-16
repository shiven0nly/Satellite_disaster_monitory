import uuid
from datetime import datetime
from typing import List, Dict, Any

# In-memory history store (kept clean & fast)
_HISTORY_STORE: List[Dict[str, Any]] = []

def add_to_history(filename: str, prediction: Dict[str, Any], explanation: str) -> Dict[str, Any]:
    """Store analysis record in history."""
    record = {
        "id": str(uuid.uuid4())[:8],
        "filename": filename,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "prediction": prediction,
        "explanation": explanation
    }
    _HISTORY_STORE.insert(0, record)  # Newest first
    return record

def get_history() -> List[Dict[str, Any]]:
    """Retrieve all past analysis records."""
    return _HISTORY_STORE

def clear_history() -> None:
    """Clear all stored history records."""
    global _HISTORY_STORE
    _HISTORY_STORE = []
