import sys
from pathlib import Path
import joblib

# Add project root to path for standalone execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.color_preprocess import (
    extract_color_features,
    extract_color_feature_vector,
)


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = PROJECT_ROOT / "models" / "color" / "color_analysis_pipeline.joblib"
IMAGE_PATH = PROJECT_ROOT / "tests" / "test_image.png"


if __name__ == "__main__":
    # ============================================================
    # LOAD MODEL
    # ============================================================

    print("=" * 60)
    print("COLOR ANALYSIS MODEL TEST")
    print("=" * 60)

    print("\nLoading model...")

    model = joblib.load(str(MODEL_PATH))

    print("Model loaded successfully.")
    print("Classes:", model.classes_)
    print("Expected features:", model.feature_names)


    # ============================================================
    # EXTRACT FEATURES
    # ============================================================

    print("\nExtracting color features...")

    features = extract_color_features(str(IMAGE_PATH))

    print("\nExtracted Features:")
    print("-" * 40)

    for name, value in features.items():
        print(f"{name:15s}: {value:.6f}")


    # ============================================================
    # CREATE FEATURE VECTOR
    # ============================================================

    X = extract_color_feature_vector(str(IMAGE_PATH))

    print("\nFeature Vector:")
    print(X)


    # ============================================================
    # PREDICTION PROBABILITIES
    # ============================================================

    print("\nPrediction Probabilities:")
    print("-" * 40)

    probabilities = model.predict_proba(X)

    for class_name, probability in zip(model.classes_, probabilities[0]):
        print(f"{class_name}: {probability:.4f}")


    # ============================================================
    # FINAL PREDICTION
    # ============================================================

    prediction = model.predict(X)

    print("\nFinal Prediction:")
    print("-" * 40)
    print(prediction[0])


    # ============================================================
    # RESULT
    # ============================================================

    class_mapping = {
        "c1": "Fresh",
        "c2": "Semi-degraded",
        "c3": "Fully-degraded",
    }

    predicted_class = prediction[0]

    print("\nResult:")
    print(f"Class : {predicted_class}")
    print(f"Status: {class_mapping.get(predicted_class, predicted_class)}")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)