import os
import sys
import numpy as np

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

def load_tif(file_path):
    """Try loading TIF image using rasterio, tifffile, cv2, or PIL."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return None

    print(f"\n📂 Loading Wildfire TIF Image: {file_path}")
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
    except Exception as e:
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


def test_wildfire(tif_path):
    print("=" * 70)
    print("🔥 WILDFIRE MODEL TEST BENCH 🔥")
    print("=" * 70)

    # 1. Load image
    img_data = load_tif(tif_path)
    if img_data is None:
        return

    # 2. Check TensorFlow model file
    model_path = os.path.join(BACKEND_DIR, "models", "wildfire_model", "wildfire_model.h5")
    print(f"\n🧠 Model File Check:")
    print(f"   Path: {model_path}")
    print(f"   Exists: {os.path.exists(model_path)}")

    # 3. Direct Keras Model Inference
    if os.path.exists(model_path):
        try:
            import tensorflow as tf
            print("\n⚙️ Loading Keras Model...")
            model = tf.keras.models.load_model(model_path)
            print(f"✅ Model loaded successfully!")
            print(f"   Input shape  : {model.input_shape}")
            print(f"   Output shape : {model.output_shape}")

            # Preprocess image array for Keras model
            expected_shape = model.input_shape
            h, w = expected_shape[1] or 128, expected_shape[2] or 128
            c = expected_shape[3] or 3

            # Format channels
            arr = img_data.astype(np.float32)
            if arr.ndim == 2:
                arr = np.stack([arr] * c, axis=-1)
            elif arr.ndim == 3 and arr.shape[2] != c:
                if arr.shape[2] > c:
                    arr = arr[:, :, :c]
                else:
                    pads = [arr[:, :, -1:]] * (c - arr.shape[2])
                    arr = np.concatenate([arr] + pads, axis=-1)

            # Resize to expected HxW
            from PIL import Image
            img_pil = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            img_resized = img_pil.resize((w, h))
            norm_tensor = np.expand_dims(np.array(img_resized, dtype=np.float32) / 255.0, axis=0)

            print(f"\n🔮 Running Raw Model Predict on input tensor shape {norm_tensor.shape}...")
            raw_pred = model.predict(norm_tensor, verbose=0)
            print(f"   Raw Output Array : {raw_pred}")

            prob = float(raw_pred[0][0]) if raw_pred.ndim > 1 else float(raw_pred[0])
            print(f"   Wildfire Probability: {prob:.4f} ({prob*100:.2f}%)")

            if prob >= 0.5:
                print("   🔥 DETECTED: WILDFIRE CONFIRMED!")
            else:
                print("   🌲 DETECTED: NO WILDFIRE (Nominal Vegetation/Soil)")

        except Exception as e:
            print(f"❌ Keras model inference failed: {e}")

    # 4. Backend analyze_wildfire_images pipeline test
    print("\n⚡ Testing Backend Pipeline Function (analyze_wildfire_images)...")
    try:
        from app.model import analyze_wildfire_images
        with open(tif_path, "rb") as f:
            raw_bytes = f.read()

        result = analyze_wildfire_images(thermal_bytes=raw_bytes)
        print("\n📊 Backend Result Object:")
        for k, v in result.items():
            print(f"   - {k}: {v}")

        # Gemini API Parameter Explanation
        try:
            from app.gemini_explainer import explain_test_parameters
            print("\n" + "=" * 70)
            print("🤖 GEMINI PARAMETER EXPLANATION (gemini-2.5-flash)")
            print("=" * 70)
            explanation = explain_test_parameters("wildfire", result)
            print(explanation)
        except Exception as e:
            print(f"⚠️ Could not generate Gemini explanation: {e}")
    except Exception as e:
        print(f"❌ Backend function call failed: {e}")

    print("=" * 70)


def select_file_dialog(title="Select Wildfire Satellite Image (.tif, .png, .jpg)"):
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
        target_file = select_file_dialog("Select Wildfire Satellite Image (.tif)")

    if not target_file:
        target_file = input("Or enter path manually: ").strip().strip('"').strip("'")

    if target_file:
        test_wildfire(target_file)
    else:
        print("No input file selected.")
