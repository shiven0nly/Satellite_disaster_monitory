import os
import sys
import numpy as np
import pickle

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

def load_tif(file_path):
    """Try loading TIF image using rasterio, tifffile, cv2, or PIL."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return None

    print(f"\n📂 Loading Flood TIF Image: {file_path}")
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

    # Method 2: tifffile
    if data is None:
        try:
            import tifffile
            data = tifffile.imread(file_path)
            loaded_by = "tifffile"
        except Exception:
            pass

    # Method 3: OpenCV
    if data is None:
        try:
            import cv2
            data = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if data is not None:
                if data.ndim == 3 and data.shape[2] == 3:
                    data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
                loaded_by = "OpenCV (cv2)"
        except Exception:
            pass

    # Method 4: PIL
    if data is None:
        try:
            from PIL import Image
            img = Image.open(file_path)
            data = np.array(img)
            loaded_by = "PIL (Pillow)"
        except Exception as e:
            print(f"❌ Failed to load image with PIL: {e}")

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


def test_flood(tif_path):
    print("=" * 70)
    print("🌊 FLOOD MODEL TEST BENCH 🌊")
    print("=" * 70)

    # 1. Load image
    img_data = load_tif(tif_path)
    if img_data is None:
        return

    # 2. Check Flood models in backend/models/flood_model
    flood_dir = os.path.join(BACKEND_DIR, "models", "flood_model")
    fusion_path = os.path.join(flood_dir, "fusion_model.pkl")
    sar_path = os.path.join(flood_dir, "sar_random_forest.pkl")
    prithvi_path = os.path.join(flood_dir, "Prithvi-EO-V2-300M-TL-Sen1Floods11.pt")

    print(f"\n🧠 Flood Models Check:")
    print(f"   fusion_model.pkl exists : {os.path.exists(fusion_path)}")
    print(f"   sar_random_forest.pkl   : {os.path.exists(sar_path)}")
    print(f"   Prithvi-EO-V2 PyTorch  : {os.path.exists(prithvi_path)}")

    # 3. Test Scikit-Learn / Fusion Models
    if os.path.exists(fusion_path):
        try:
            print("\n⚙️ Testing Fusion Model Predict...")
            with open(fusion_path, "rb") as f:
                fusion_model = pickle.load(f)

            print(f"   Fusion Model Type: {type(fusion_model)}")
        except Exception as e:
            print(f"⚠️ Fusion model test: {e}")

    # 4. Backend analyze_multimodal_images pipeline test
    print("\n⚡ Testing Backend Pipeline Function (analyze_multimodal_images)...")
    try:
        from app.model import analyze_multimodal_images
        with open(tif_path, "rb") as f:
            raw_bytes = f.read()

        result = analyze_multimodal_images(optical_bytes=raw_bytes)
        print("\n📊 Backend Result Object:")
        for k, v in result.items():
            print(f"   - {k}: {v}")

        # Gemini API Parameter Explanation
        try:
            from app.gemini_explainer import explain_test_parameters
            print("\n" + "=" * 70)
            print("🤖 GEMINI PARAMETER EXPLANATION (gemini-3.6-flash)")
            print("=" * 70)
            explanation = explain_test_parameters("flood", result, model_name="gemini-3.6-flash")
            print(explanation)
        except Exception as e:
            print(f"⚠️ Could not generate Gemini explanation: {e}")
    except Exception as e:
        print(f"❌ Backend function call failed: {e}")

    print("=" * 70)


def select_file_dialog(title="Select Flood Satellite Image (.tif, .png, .jpg)"):
    """Open native OS file picker window using Tkinter."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected_path = filedialog.askopenfilename(
            title=title,
            filetypes=[
                ("Satellite Imagery", "*.tif *.tiff *.png *.jpg *.jpeg"),
                ("All Files", "*.*"),
            ],
        )
        root.destroy()
        return selected_path
    except Exception as e:
        print(f"⚠️ Could not open GUI file dialog: {e}")
        return None


if __name__ == "__main__":
    target_file = None
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        print("📂 Opening Windows file selector dialog...")
        target_file = select_file_dialog("Select Flood Satellite Image (.tif)")

    if not target_file:
        target_file = input("Or enter path manually: ").strip().strip('"').strip("'")

    if target_file:
        test_flood(target_file)
    else:
        print("No input file selected.")
