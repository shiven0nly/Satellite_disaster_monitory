import argparse
from pathlib import Path

import numpy as np
import rasterio
import torch
import torch.nn.functional as F

from models.drought_model.drought_model import (
    DroughtMultiModalV2,
    OPTICAL_MEAN,
    OPTICAL_STD,
    SAR_MEAN,
    SAR_STD,
    THERMAL_MEAN,
    THERMAL_STD,
)

BACKEND_DIR = Path(__file__).resolve().parent
MODEL_DIR = BACKEND_DIR / "models" / "drought_model"
MODEL_PATH = MODEL_DIR / "drought_multimodal_best.pth"
DEFAULT_THRESHOLD = 0.180
IMAGE_SIZE = (128, 128)


def read_raster(path):
    with rasterio.open(path) as source:
        image = source.read().astype(np.float32)
        print(f"  {path.name}: {source.width}x{source.height}, bands={source.count}, dtype={source.dtypes[0]}")
    return np.nan_to_num(image, nan=0.0, posinf=0.0, neginf=0.0)


def resize_channels(image):
    tensor = torch.from_numpy(image).unsqueeze(0)
    return F.interpolate(tensor, size=IMAGE_SIZE, mode="bilinear", align_corners=False)[0]


def select_channels(image, count):
    if image.shape[0] >= count:
        return image[:count]
    return np.concatenate([image] + [image[-1:]] * (count - image.shape[0]), axis=0)


def prepare_inputs(optical_path, sar_path, thermal_path):
    optical = select_channels(read_raster(optical_path), 6)
    sar = select_channels(read_raster(sar_path), 2)
    thermal = select_channels(read_raster(thermal_path), 1)

    optical = (resize_channels(optical) - torch.from_numpy(OPTICAL_MEAN)[:, None, None]) / (torch.from_numpy(OPTICAL_STD)[:, None, None] + 1e-6)
    sar = (resize_channels(sar) - torch.from_numpy(SAR_MEAN)[:, None, None]) / (torch.from_numpy(SAR_STD)[:, None, None] + 1e-6)
    thermal = (resize_channels(thermal) - THERMAL_MEAN) / (THERMAL_STD + 1e-6)
    return optical.unsqueeze(0), sar.unsqueeze(0), thermal.unsqueeze(0)


def load_model(device):
    model = DroughtMultiModalV2().to(device)
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict)
    model.eval()
    threshold = float(checkpoint.get("val_threshold", DEFAULT_THRESHOLD))
    print(f"Loaded checkpoint: {MODEL_PATH.name}")
    print(f"Training epoch: {checkpoint.get('epoch', 'unknown')}")
    print(f"Model inputs: optical=6, SAR=2, thermal=1, size={IMAGE_SIZE}")
    return model, threshold


def evaluate(model, label, optical_path, sar_path, thermal_path, threshold, device):
    print("=" * 70)
    print(f"{label}: DROUGHT MODEL TEST")
    print("=" * 70)
    optical, sar, thermal = prepare_inputs(optical_path, sar_path, thermal_path)
    optical, sar, thermal = optical.to(device), sar.to(device), thermal.to(device)
    print(f"  Input tensors: optical={tuple(optical.shape)}, SAR={tuple(sar.shape)}, thermal={tuple(thermal.shape)}")

    with torch.no_grad():
        probability = float(torch.sigmoid(model(optical, sar, thermal)).item())

    if probability < 0.18:
        risk_level = "Low"
    elif probability < 0.35:
        risk_level = "Moderate"
    elif probability < 0.55:
        risk_level = "Severe"
    else:
        risk_level = "Extreme"

    result = {
        "label": label,
        "probability": probability,
        "threshold": threshold,
        "detected": probability >= threshold,
        "risk_level": risk_level,
    }
    print("\nRESULT")
    print("---------------------------")
    print(f"Drought probability: {probability:.6f}")
    print(f"Threshold          : {threshold:.6f}")
    print(f"Risk level         : {risk_level}")
    print(f"Drought detected   : {'YES' if result['detected'] else 'NO'}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Evaluate the multimodal drought model.")
    parser.add_argument("images", nargs="*", help="One or two images; one image is reused for all modalities")
    parser.add_argument("--optical", type=Path, help="Optical TIFF, expected six bands")
    parser.add_argument("--sar", type=Path, help="SAR TIFF, expected two bands")
    parser.add_argument("--thermal", type=Path, help="Thermal TIFF, expected one band")
    args = parser.parse_args()

    if args.images or args.optical or args.sar or args.thermal:
        paths = [Path(path) for path in args.images]
        optical_path = args.optical or (paths[0] if paths else None)
        if optical_path is None:
            raise ValueError("Provide an image or --optical path.")
        sar_path = args.sar or (paths[1] if len(paths) > 1 else optical_path)
        thermal_path = args.thermal or (paths[2] if len(paths) > 2 else optical_path)
        cases = [("INPUT", optical_path, sar_path, thermal_path)]
    else:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        cases = []
        for label in ("POSITIVE", "NEGATIVE"):
            selected = filedialog.askopenfilename(
                title=f"Select {label.lower()} drought optical image",
                filetypes=[("GeoTIFF files", "*.tif *.tiff"), ("All files", "*.*")],
            )
            if selected:
                cases.append((label, Path(selected), Path(selected), Path(selected)))
        root.destroy()
        if not cases:
            print("No input image selected.")
            return

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing drought checkpoint: {MODEL_PATH}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    model, threshold = load_model(device)
    results = [evaluate(model, label, optical, sar, thermal, threshold, device) for label, optical, sar, thermal in cases]

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for result in results:
        print(f"{result['label']:>10} | detected={str(result['detected']):<5} | probability={result['probability']:.6f} | risk={result['risk_level']}")

    # Gemini API Parameter Explanation
    try:
        from app.gemini_explainer import explain_test_parameters
        print("\n" + "=" * 70)
        print("🤖 GEMINI PARAMETER EXPLANATION (gemini-3.6-flash)")
        print("=" * 70)
        explanation = explain_test_parameters("drought", {"results": results}, model_name="gemini-3.6-flash")
        print(explanation)
        print("=" * 70)
    except Exception as e:
        print(f"⚠️ Could not generate Gemini explanation: {e}")


if __name__ == "__main__":
    main()
