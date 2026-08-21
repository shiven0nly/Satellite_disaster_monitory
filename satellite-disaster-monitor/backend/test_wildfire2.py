import os
import numpy as np
import rasterio
import tensorflow as tf
import tkinter as tk
from tkinter import filedialog

# Resolve paths relative to this script's directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

WILDFIRE_DIR = os.path.join(_SCRIPT_DIR, "models", "wildfire_model")
MODEL_PATHS = [
    os.path.join(WILDFIRE_DIR, "forest_fire_finetuned.h5"),
    os.path.join(WILDFIRE_DIR, "wildfire_model.h5"),
]

THRESHOLD = 0.20


def select_test_files():
    """Open tkinter file dialogs to let the user pick test .tif files."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    filetypes = [("GeoTIFF files", "*.tif *.tiff"), ("All files", "*.*")]
    test_files = {}

    print("[File Picker] Select the POSITIVE wildfire test image (.tif)...")
    pos_path = filedialog.askopenfilename(
        title="Select POSITIVE wildfire test image",
        filetypes=filetypes,
    )
    if pos_path:
        test_files["POSITIVE"] = pos_path
    else:
        print("  Skipped (no file selected).")

    print("[File Picker] Select the NEGATIVE wildfire test image (.tif)...")
    neg_path = filedialog.askopenfilename(
        title="Select NEGATIVE wildfire test image",
        filetypes=filetypes,
    )
    if neg_path:
        test_files["NEGATIVE"] = neg_path
    else:
        print("  Skipped (no file selected).")

    root.destroy()

    if not test_files:
        print("\nNo files selected — nothing to test.")

    return test_files


def load_model(model_path):
    print("Loading wildfire model...")
    print("Model path:", model_path)

    from keras.layers import Conv2DTranspose, BatchNormalization

    # Monkey-patch the real classes so Keras 3's internal deserializer picks
    # them up (custom_objects doesn't work with the new serialization format).

    _orig_bn_init = BatchNormalization.__init__
    _orig_ct_init = Conv2DTranspose.__init__

    def _patched_bn_init(self, *args, **kwargs):
        axis = kwargs.get("axis", -1)
        if isinstance(axis, (list, tuple)) and len(axis) == 1:
            kwargs["axis"] = axis[0]
        _orig_bn_init(self, *args, **kwargs)

    def _patched_ct_init(self, *args, **kwargs):
        kwargs.pop("groups", None)
        _orig_ct_init(self, *args, **kwargs)

    BatchNormalization.__init__ = _patched_bn_init
    Conv2DTranspose.__init__ = _patched_ct_init

    try:
        model = tf.keras.models.load_model(
            model_path,
            compile=False,
        )
    finally:
        # Restore original __init__ methods
        BatchNormalization.__init__ = _orig_bn_init
        Conv2DTranspose.__init__ = _orig_ct_init

    print("Model loaded")
    print("Input :", model.input_shape)
    print("Output:", model.output_shape)
    print()

    return model


def prepare_image(path, model):
    expected_shape = model.input_shape
    height = expected_shape[1] or 128
    width = expected_shape[2] or 128
    channels = expected_shape[3] or 3

    with rasterio.open(path) as src:

        print("  Size :", src.width, "x", src.height)
        print("  Bands:", src.count)
        print("  Dtype:", src.dtypes)

        if src.count < 6:
            raise ValueError(f"Expected at least 6 bands, got {src.count}")

        # Your Sentinel-2 dataset:
        #
        # Band 4 = B8A
        # Band 5 = B11
        # Band 6 = B12
        #
        # Model input:
        # B12, B11, B8A

        selected_bands = [6, 5, 4]
        image = src.read(selected_bands).astype(np.float32)

    image /= 10000.0

    image = np.transpose(image, (1, 2, 0))
    if image.shape[2] != channels:
        if image.shape[2] > channels:
            image = image[:, :, :channels]
        else:
            image = np.concatenate(
                [image] + [image[:, :, -1:]] * (channels - image.shape[2]),
                axis=2,
            )

    from PIL import Image
    image = np.array(
        Image.fromarray(np.clip(image * 255.0, 0, 255).astype(np.uint8)).resize(
            (width, height)
        ),
        dtype=np.float32,
    ) / 255.0

    return np.expand_dims(image, axis=0)


def test_image(model, label, path):

    print("=" * 70)
    print(label)
    print("=" * 70)

    print("File:", path)

    if not os.path.isfile(path):
        print("ERROR: File does not exist.")
        return

    x = prepare_image(path, model)

    print("Model input:", x.shape)
    print(
        "Input range:",
        float(x.min()),
        "to",
        float(x.max())
    )

    raw_prediction = model.predict(x, verbose=0)
    prediction = np.asarray(raw_prediction).squeeze()
    if prediction.ndim == 0:
        prediction = prediction.reshape(1)

    max_probability = float(prediction.max())

    mean_probability = float(prediction.mean())

    fire_pixels = int(
        np.sum(prediction >= THRESHOLD)
    )

    total_pixels = prediction.size

    fire_percentage = (
        fire_pixels /
        total_pixels *
        100
    )

    fire_detected = fire_pixels > 0

    print()
    print("RESULT")
    print("---------------------------")
    print(
        "Max probability :",
        f"{max_probability:.6f}"
    )
    print(
        "Mean probability:",
        f"{mean_probability:.6f}"
    )
    print(
        "Threshold        :",
        THRESHOLD
    )
    print(
        "Fire pixels      :",
        fire_pixels,
        "/",
        total_pixels
    )
    print(
        "Fire area        :",
        f"{fire_percentage:.3f}%"
    )
    print(
        "Fire detected    :",
        "YES" if fire_detected else "NO"
    )

    return {
        "label": label,
        "max_probability": max_probability,
        "mean_probability": mean_probability,
        "fire_pixels": fire_pixels,
        "fire_percentage": fire_percentage,
        "fire_detected": fire_detected,
    }


def main():

    print("=" * 70)
    print("DISASTERAI FOREST FIRE MODEL TEST")
    print("=" * 70)
    print()

    # Use tkinter file picker to select test images
    test_files = select_test_files()
    if not test_files:
        return

    results = []

    for model_path in MODEL_PATHS:
        if not os.path.isfile(model_path):
            print(f"Skipping missing model: {model_path}")
            continue

        try:
            model = load_model(model_path)
            for label, path in test_files.items():
                result = test_image(model, f"{label} [{os.path.basename(model_path)}]", path)
                if result:
                    results.append(result)
                print()
        except Exception as e:
            print(f"❌ Model evaluation failed for {model_path}: {e}")

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for result in results:

        print(
            f"{result['label']:>10} | "
            f"detected={str(result['fire_detected']):<5} | "
            f"max={result['max_probability']:.6f} | "
            f"fire={result['fire_percentage']:.3f}%"
        )

    # Gemini API Parameter Explanation
    try:
        from app.gemini_explainer import explain_test_parameters
        print("\n" + "=" * 70)
        print(" GEMINI PARAMETER EXPLANATION (gemini-3.6-flash)")
        print("=" * 70)
        explanation = explain_test_parameters("wildfire", {"threshold": THRESHOLD, "results": results}, model_name="gemini-3.6-flash")
        print(explanation)
        print("=" * 70)
    except Exception as e:
        print(f"⚠️ Could not generate Gemini explanation: {e}")


if __name__ == "__main__":
    main()