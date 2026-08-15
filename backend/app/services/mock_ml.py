"""
Mock Machine Learning and LLM processing services.

PLACEHOLDER: These functions simulate the vision ML model inference and LLM parser.
They will be replaced with actual ML inference engines (PyTorch / ONNX) and LLM APIs.
"""
from typing import Any, Dict


def fake_model_predict(image_path: str) -> Dict[str, Any]:
    """
    PLACEHOLDER: replace with real model.predict(image_path) call later.
    Simulates ML model image analysis on satellite/IR imagery.
    """
    return {
        "disaster_type": "Wildfire",
        "confidence": 0.92,
        "spectral_anomalies": {
            "thermal_intensity_kelvin": 620.5,
            "smoke_plume_density": "high",
            "ndvi_drop_percentage": 42.8,
        },
        "detected_bounding_boxes": [
            {"label": "active_fire_front", "bbox": [140, 95, 320, 240], "confidence": 0.94},
            {"label": "burn_scar", "bbox": [100, 50, 450, 380], "confidence": 0.89},
        ],
    }


def fake_llm_parse(model_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    PLACEHOLDER: replace with real LLM parser (e.g., OpenAI / Gemini API call) later.
    Parses raw ML model output into clean, structured assessment results.
    """
    return {
        "disaster_type": model_output.get("disaster_type", "Wildfire"),
        "severity": "HIGH",
        "affected_area_estimate": "18.4 sq km",
        "description": (
            "Thermal anomalies detected an active wildfire front spreading rapidly. "
            "NDVI drop of 42.8% indicates significant vegetation loss and high risk to surrounding areas."
        ),
        "confidence_score": model_output.get("confidence", 0.92),
        "latitude": 34.0522,
        "longitude": -118.2437,
        "raw_model_output": model_output,
    }
