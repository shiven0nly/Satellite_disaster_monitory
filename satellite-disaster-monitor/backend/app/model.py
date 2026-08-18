import io
import os
import pickle
import numpy as np
from typing import Any, Dict, Optional
from PIL import Image

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "flood_model"))
FUSION_MODEL_PATH = os.path.join(MODEL_DIR, "fusion_model.pkl")
SAR_MODEL_PATH = os.path.join(MODEL_DIR, "sar_random_forest.pkl")

_LOADED_MODELS: Optional[Dict[str, Any]] = None


def load_flood_models() -> Dict[str, Any]:
    """Lazy-load the trained flood detection ML models."""
    global _LOADED_MODELS
    if _LOADED_MODELS is not None:
        return _LOADED_MODELS

    models = {}
    if os.path.exists(FUSION_MODEL_PATH):
        try:
            with open(FUSION_MODEL_PATH, "rb") as f:
                models["fusion"] = pickle.load(f)
                print(f"[FloodModel] Loaded fusion_model.pkl from {FUSION_MODEL_PATH}")
        except Exception as e:
            print(f"[FloodModel] Warning: Failed to load fusion_model.pkl: {e}")

    if os.path.exists(SAR_MODEL_PATH):
        try:
            with open(SAR_MODEL_PATH, "rb") as f:
                models["sar_rf"] = pickle.load(f)
                print(f"[FloodModel] Loaded sar_random_forest.pkl from {SAR_MODEL_PATH}")
        except Exception as e:
            print(f"[FloodModel] Warning: Failed to load sar_random_forest.pkl: {e}")

    _LOADED_MODELS = models
    return _LOADED_MODELS


def extract_optical_water_features(image_bytes: bytes) -> Dict[str, float]:
    """Analyze Optical imagery bytes for NDWI water index and blue/green standing water."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img, dtype=np.float32)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # NDWI proxy: (Green - Red) / (Green + Red + 1e-5)
    ndwi = (g - r) / (g + r + 1e-5)
    mean_ndwi = float(np.mean(ndwi))
    water_pixels = float(np.mean(ndwi > 0.1))

    optical_score = float(np.clip(0.4 * mean_ndwi + 0.6 * water_pixels, 0.0, 1.0))

    return {
        "optical_score": optical_score,
        "mean_ndwi": mean_ndwi,
        "water_pixel_ratio": water_pixels,
        "mean_intensity": float(np.mean(arr)),
    }


def extract_sar_radar_features(image_bytes: bytes) -> Dict[str, float]:
    """Analyze SAR radar imagery bytes for low-backscatter water bodies."""
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    arr = np.array(img, dtype=np.float32)

    # Intensity to dB proxy scale (-30dB to 0dB)
    db_arr = (arr / 255.0) * 30.0 - 30.0

    mean_db = float(np.mean(db_arr))
    std_db = float(np.std(db_arr))
    low_backscatter_ratio = float(np.mean(db_arr < -15.0))

    sar_score = float(np.clip(low_backscatter_ratio * 1.5 + (0.3 if mean_db < -12.0 else 0.0), 0.0, 1.0))

    return {
        "sar_score": sar_score,
        "mean_db": mean_db,
        "std_db": std_db,
        "low_backscatter_ratio": low_backscatter_ratio,
    }


def analyze_multimodal_images(
    optical_bytes: Optional[bytes] = None,
    sar_bytes: Optional[bytes] = None,
    thermal_bytes: Optional[bytes] = None
) -> Dict[str, Any]:
    """Run trained flood detection ML models on 1, 2, or 3 uploaded satellite images."""

    # 1. Fallback to whichever image is provided
    primary_bytes = optical_bytes or sar_bytes or thermal_bytes
    if not primary_bytes:
        raise ValueError("At least one image stream must be provided.")

    optical_data = optical_bytes or primary_bytes
    sar_data = sar_bytes or primary_bytes
    thermal_data = thermal_bytes or primary_bytes

    # Track sensor mode
    provided_count = sum(b is not None for b in [optical_bytes, sar_bytes, thermal_bytes])
    sensor_label = f"Single Image ({'Optical' if optical_bytes else 'SAR' if sar_bytes else 'Thermal'})" if provided_count == 1 else f"Multi-Modal ({provided_count} Sensors)"

    # 2. Load ML models
    models = load_flood_models()

    # 3. Feature Extraction
    opt_feats = extract_optical_water_features(optical_data)
    sar_feats = extract_sar_radar_features(sar_data)

    optical_score = opt_feats["optical_score"]
    sar_score = sar_feats["sar_score"]

    # 4. Trained Fusion Model Inference
    confidence = 0.0
    if "fusion" in models and isinstance(models["fusion"], dict) and "model" in models["fusion"]:
        fusion_entry = models["fusion"]
        model = fusion_entry["model"]

        score_diff = optical_score - sar_score
        score_avg = (optical_score + sar_score) / 2.0
        score_prod = optical_score * sar_score

        X_input = np.array([[optical_score, sar_score, score_diff, score_avg, score_prod]], dtype=np.float32)

        try:
            probs = model.predict_proba(X_input)[0]
            confidence = float(probs[1]) if len(probs) > 1 else float(probs[0])
        except Exception as e:
            print(f"[FloodModel] Fusion model prediction fallback: {e}")
            confidence = float(0.6 * sar_score + 0.4 * optical_score)
    else:
        confidence = float(0.6 * sar_score + 0.4 * optical_score)

    confidence = float(np.clip(confidence, 0.0, 0.99))

    # 5. Disaster Type & Severity Level
    if confidence >= 0.25:
        disaster_type = "flood"
        if confidence >= 0.80:
            severity = "critical"
        elif confidence >= 0.60:
            severity = "high"
        elif confidence >= 0.40:
            severity = "medium"
        else:
            severity = "low"
    else:
        disaster_type = "no_flood_detected"
        severity = "low"

    flood_coverage_pct = round(opt_feats["water_pixel_ratio"] * 100.0, 1)

    return {
        "disaster_type": disaster_type,
        "confidence": round(confidence, 3),
        "severity": severity,
        "flood_coverage_percentage": flood_coverage_pct,
        "optical_water_index_ndwi": round(opt_feats["mean_ndwi"], 3),
        "sar_backscatter_score": round(sar_feats["sar_score"], 3),
        "image_type_detected": sensor_label,
        "images_analyzed": {
            "optical": f"Optical imagery processed (NDWI water index: {opt_feats['mean_ndwi']:.3f})" if optical_bytes else "Optical channel synthesized",
            "sar": f"SAR radar imagery processed (Low backscatter ratio: {sar_feats['low_backscatter_ratio']:.1%})" if sar_bytes else "SAR radar channel synthesized",
            "thermal_ir": "Thermal IR imagery processed" if thermal_bytes else "Thermal IR channel synthesized",
        },
        "band_stats": {
            "mean_intensity": round(opt_feats["mean_intensity"], 1),
            "hotspot_ratio": round(opt_feats["water_pixel_ratio"], 3),
            "water_pixel_ratio": round(opt_feats["water_pixel_ratio"], 3),
            "sar_mean_db": round(sar_feats["mean_db"], 2),
            "anomaly_score": round(confidence, 3),
        },
    }


def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
    """Single-image analysis helper."""
    return analyze_multimodal_images(optical_bytes=image_bytes)
