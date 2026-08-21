"""Compatibility entry point for the one-band Sentinel-1 landslide test."""

from test_landslide2 import main


if __name__ == "__main__":
    main()
import os
import sys
import numpy as np
import rasterio
import torch

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

THRESHOLD = 0.37

def load_tif(file_path):
    """Try loading TIF image using rasterio, tifffile, cv2, or PIL."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return None

    print(f"\n📂 Loading Landslide TIF Image: {file_path}")
    print(f"   File size: {os.path.getsize(file_path) / 1024:.2f} KB")

    data = None
    loaded_by = None

    # Method 1: rasterio
    try:
        import rasterio
        with rasterio.open(file_path) as src:
            data = src.read()  # (channels, height, width)
            data = np.transpose(data, (1, 2, 0))  # (height, width, channels)
            loaded_by = f"rasterio (bands={src.count}, crs={src.crs})"
    except Exception:
        pass


    if data is not None:
        print(f"✅ Successfully loaded by {loaded_by}")
        print(f"   Array shape : {data.shape}")
        print(f"   Data type   : {data.dtype}")
        print(f"   Min value   : {np.min(data)}")
        print(f"   Max value   : {np.max(data)}")
        print(f"   Mean value  : {np.mean(data):.4f}")
    else:
        print("❌ All image readers failed to read this TIF file.")

    return data


def prepare_14_channel_input(img_data, model_dir):
    """Prepare a TIFF using the ensemble's 14-channel normalization contract."""
    arr = np.nan_to_num(img_data.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    if arr.ndim == 2:
        arr = arr[:, :, np.newaxis]

    band_count = arr.shape[2]
    if band_count == 0:
        raise ValueError("Input TIFF contains no bands.")

    stats_path = os.path.join(model_dir, "channel_stats.npz")
    if band_count == 14 and os.path.exists(stats_path):
        stats = np.load(stats_path)
        mean = stats["mean"].astype(np.float32)
        std = np.maximum(stats["std"].astype(np.float32), 1e-6)
        if mean.shape != (14,) or std.shape != (14,):
            raise ValueError(f"Expected 14 channel statistics, got {mean.shape} and {std.shape}")
        arr = (arr - mean.reshape(1, 1, 14)) / std.reshape(1, 1, 14)
        print(f"   Normalization  : channel_stats.npz ({stats_path})")
    else:
        if band_count != 14:
            print(
                f"   WARNING: Model expects 14 training channels, input has {band_count}; "
                "cycling available bands."
            )
        arr = np.stack(
            [
                (arr[:, :, band] - arr[:, :, band].mean())
                / max(float(arr[:, :, band].std()), 1e-6)
                for band in range(band_count)
            ],
            axis=2,
        )
        print("   Normalization  : per-band fallback (channel_stats.npz unavailable or non-14-band input)")

    ch14 = np.stack([arr[:, :, band % band_count] for band in range(14)], axis=0)
    input_tensor = torch.from_numpy(ch14).unsqueeze(0)
    return torch.nn.functional.interpolate(
        input_tensor, size=(128, 128), mode="bilinear", align_corners=False
    )


def test_landslide(tif_path, label="INPUT"):
    print("=" * 70)
    print(f"⛰️ LANDSLIDE MODEL TEST BENCH: {label} ⛰️")
    print("=" * 70)

    # 1. Load image
    img_data = load_tif(tif_path)
    if img_data is None:
        return

    # 2. Check PyTorch model weights
    landslide_dir = os.path.join(BACKEND_DIR, "models", "landslide_model")
    model_path = os.path.join(landslide_dir, "resnet34_unet_14ch_best.pth")
    result = None

    print(f"\n🧠 Checkpoint File Check:")
    print(f"   resnet34_unet_14ch_best.pth exists: {os.path.exists(model_path)}")
    print(f"   Using: {model_path}")

    # 3. Direct PyTorch Model Inference
    if os.path.exists(model_path):
        try:
            from models.landslide_model.train_landslide_14ch import DEVICE, ResNet34UNet
            print("\n⚙️ Loading ensemble ResNet34 UNet Landslide Model...")
            model = ResNet34UNet().to(DEVICE)
            checkpoint = torch.load(model_path, map_location=DEVICE, weights_only=False)
            state_dict = checkpoint.get("model_state_dict", checkpoint)
            model.load_state_dict(state_dict)
            model.eval()
            print("✅ Ensemble-compatible PyTorch model loaded successfully!")

            input_tensor = prepare_14_channel_input(img_data, landslide_dir).to(DEVICE)
            print(f"\n🔮 Running Model Forward Pass on tensor shape {input_tensor.shape}...")

            with torch.no_grad():
                logits = model(input_tensor)
                probs = torch.sigmoid(logits)
                mean_prob = float(probs.mean().item())
                max_prob = float(probs.max().item())

            print(f"   Output Logits Shape : {logits.shape}")
            print(f"   Mean Risk Probability: {mean_prob:.4f}")
            print(f"   Max Risk Probability : {max_prob:.4f}")
            detected_pixels = int(np.sum(probs.cpu().numpy() >= THRESHOLD))
            total_pixels = int(probs.numel())
            detected_percentage = detected_pixels / total_pixels * 100.0
            landslide_detected = detected_pixels > 0
            print(f"   Threshold             : {THRESHOLD:.2f}")
            print(f"   Landslide pixels      : {detected_pixels} / {total_pixels}")
            print(f"   Landslide area        : {detected_percentage:.3f}%")
            print("   ⛰️ DETECTED: LANDSLIDE RISK DETECTED!" if landslide_detected else "   🌲 DETECTED: NO LANDSLIDE (Stable Terrain)")
            result = {
                "label": label,
                "max_probability": max_prob,
                "mean_probability": mean_prob,
                "landslide_percentage": detected_percentage,
                "landslide_detected": landslide_detected,
            }

        except Exception as e:
            print(f"❌ PyTorch model inference failed: {e}")

    print("=" * 70)
    return result


def select_test_files():
    """Open native OS file picker window using Tkinter."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        filetypes = [("GeoTIFF files", "*.tif *.tiff"), ("All files", "*.*")]
        selected_files = {}
        for label in ("POSITIVE", "NEGATIVE"):
            selected_path = filedialog.askopenfilename(
                title=f"Select {label.lower()} landslide test image",
                filetypes=filetypes,
            )
            if selected_path:
                selected_files[label] = selected_path
        root.destroy()
        return selected_files
    except Exception as e:
        print(f"⚠️ Could not open GUI file dialog: {e}")
        return {}


if __name__ == "__main__":
    test_files = {"INPUT": sys.argv[1]} if len(sys.argv) > 1 else select_test_files()
    results = []
    if test_files:
        for label, target_file in test_files.items():
            print(f"\n===== {label} =====")
            result = test_landslide(target_file, label)
            if result:
                results.append(result)

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
            explanation = explain_test_parameters("landslide", {"threshold": THRESHOLD, "results": results}, model_name="gemini-3.6-flash")
            print(explanation)
            print("=" * 70)
        except Exception as e:
            print(f"⚠️ Could not generate Gemini explanation: {e}")
    else:
        print("No input file selected.")
