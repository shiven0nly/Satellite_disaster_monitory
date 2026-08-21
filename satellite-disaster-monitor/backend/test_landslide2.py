import argparse
import os
from pathlib import Path

import numpy as np
import rasterio
import torch

BACKEND_DIR = Path(__file__).resolve().parent
MODEL_DIR = BACKEND_DIR / "models" / "landslide_model"
MODEL_PATH = MODEL_DIR / "resnet34_unet_14ch_best.pth"
THRESHOLD = 0.37
MIN_AREA_PERCENTAGE = 0.5
CLIP_PERCENTILES = (2.0, 98.0)
MAD_SCALE = 1.4826


def load_one_band(path, band_number):
    print(f"\nLoading Sentinel-1 SAR image: {path}")
    with rasterio.open(path) as source:
        if band_number < 1 or band_number > source.count:
            raise ValueError(
                f"Band {band_number} is unavailable; image contains {source.count} band(s)."
            )
        image = source.read(band_number).astype(np.float32)
        print(f"Size: {source.width} x {source.height}")
        print(f"Bands: {source.count} (using band {band_number})")
        print(f"Dtype: {source.dtypes[band_number - 1]}")
    return np.nan_to_num(image, nan=0.0, posinf=0.0, neginf=0.0)


def prepare_one_band_input(image):
    low, high = np.percentile(image, CLIP_PERCENTILES)
    if high <= low:
        normalized = np.zeros_like(image, dtype=np.float32)
    else:
        normalized = np.clip((image - low) / (high - low), 0.0, 1.0)

    median = float(np.median(normalized))
    mad = float(np.median(np.abs(normalized - median)))
    robust_std = max(MAD_SCALE * mad, 1e-6)
    normalized = (normalized - median) / robust_std
    one_band = torch.from_numpy(normalized).float().unsqueeze(0).unsqueeze(0)
    one_band = torch.nn.functional.interpolate(
        one_band, size=(128, 128), mode="bilinear", align_corners=False
    )
    return one_band.repeat(1, 14, 1, 1), low, high, median, robust_std


def load_model(device):
    from models.landslide_model.train_landslide_14ch import ResNet34UNet

    model = ResNet34UNet().to(device)
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict)
    model.eval()
    print(f"Loaded checkpoint: {MODEL_PATH.name}")
    print(f"Training epoch: {checkpoint.get('epoch', 'unknown')}")
    print("Model input: 14 channels (one SAR band replicated 14 times)")
    return model


def evaluate(model, path, label, band_number, device, threshold, min_area_percentage):
    print("=" * 70)
    print(f"{label}: ONE-BAND SAR LANDSLIDE TEST")
    print("=" * 70)

    image = load_one_band(path, band_number)
    tensor, low, high, median, robust_std = prepare_one_band_input(image)
    tensor = tensor.to(device)
    print(f"Input tensor: {tuple(tensor.shape)}")
    print(f"Percentile normalization: {low:.6g} to {high:.6g}")
    print(f"Median/MAD normalization: median={median:.6g}, robust_std={robust_std:.6g}")

    with torch.no_grad():
        probabilities = torch.sigmoid(model(tensor)).cpu().numpy()[0, 0]

    detected = probabilities >= threshold
    detected_pixels = int(detected.sum())
    total_pixels = int(detected.size)
    area_percentage = detected_pixels / total_pixels * 100.0
    landslide_detected = area_percentage >= min_area_percentage
    result = {
        "label": label,
        "max_probability": float(probabilities.max()),
        "mean_probability": float(probabilities.mean()),
        "landslide_percentage": area_percentage,
        "landslide_detected": landslide_detected,
    }

    print("\nRESULT")
    print("---------------------------")
    print(f"Max probability : {result['max_probability']:.6f}")
    print(f"Mean probability: {result['mean_probability']:.6f}")
    print(f"Threshold       : {threshold:.2f}")
    print(f"Landslide pixels: {detected_pixels} / {total_pixels}")
    print(f"Landslide area  : {area_percentage:.3f}%")
    print(f"Minimum area    : {min_area_percentage:.3f}%")
    print(f"Detected        : {'YES' if result['landslide_detected'] else 'NO'}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Evaluate one Sentinel-1 band with the landslide model.")
    parser.add_argument("images", nargs="*", help="One or two Sentinel-1 GeoTIFF paths")
    parser.add_argument("--band", type=int, default=1, help="1-based SAR band to use (default: 1)")
    parser.add_argument("--threshold", type=float, default=THRESHOLD, help="Pixel probability threshold")
    parser.add_argument(
        "--min-area",
        type=float,
        default=MIN_AREA_PERCENTAGE,
        help="Minimum predicted area percentage required for a landslide (default: 0.5)",
    )
    args = parser.parse_args()

    paths = args.images
    if not paths:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        paths = list(
            filedialog.askopenfilenames(
                title="Select Sentinel-1 landslide test images",
                filetypes=[("GeoTIFF files", "*.tif *.tiff"), ("All files", "*.*")],
            )
        )
        root.destroy()

    if not paths:
        print("No input image selected.")
        return
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing checkpoint: {MODEL_PATH}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    stats_path = MODEL_DIR / "channel_stats.npz"
    if stats_path.exists():
        print(f"Normalization stats: {stats_path}")
    else:
        print("WARNING: channel_stats.npz is missing; using hardcoded robust SAR fallback.")
        print("         Fallback: clip 2nd-98th percentiles, center by median, scale by 1.4826*MAD.")
    model = load_model(device)
    results = []
    for index, image_path in enumerate(paths):
        results.append(
            evaluate(
                model,
                image_path,
                f"INPUT {index + 1}",
                args.band,
                device,
                args.threshold,
                args.min_area,
            )
        )

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for result in results:
        print(
            f"{result['label']:>10} | "
            f"detected={str(result['landslide_detected']):<5} | "
            f"max={result['max_probability']:.6f} | "
            f"mean={result['mean_probability']:.6f} | "
            f"area={result['landslide_percentage']:.3f}%"
        )

    # Gemini API Parameter Explanation
    try:
        from app.gemini_explainer import explain_test_parameters
        print("\n" + "=" * 70)
        print("🤖 GEMINI PARAMETER EXPLANATION (gemini-3.6-flash)")
        print("=" * 70)
        explanation = explain_test_parameters("landslide", {"threshold": args.threshold, "min_area": args.min_area, "results": results}, model_name="gemini-3.6-flash")
        print(explanation)
        print("=" * 70)
    except Exception as e:
        print(f"⚠️ Could not generate Gemini explanation: {e}")


if __name__ == "__main__":
    main()
