import sys
from pathlib import Path

# Add project root to path for standalone execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.efficientnet_inference import EfficientNetInference


MODEL_PATH = PROJECT_ROOT / "models" / "efficientnet" / "efficientnet_b3_optimized.onnx"
CLASS_NAMES_PATH = PROJECT_ROOT / "models" / "efficientnet" / "class_names.json"
IMAGE_PATH = PROJECT_ROOT / "tests" / "test_image.png"


if __name__ == "__main__":
    model = EfficientNetInference(
        model_path=str(MODEL_PATH),
        class_names_path=str(CLASS_NAMES_PATH)
    )

    result = model.predict(str(IMAGE_PATH))

    print("\n==============================")
    print("EfficientNet-B3 Result")
    print("==============================")
    print("Model:", result.model)
    print("Prediction:", result.prediction)
    print("Confidence:", result.confidence)

    print("\nProbabilities:")
    for class_name, probability in result.probabilities.items():
        print(f"{class_name}: {probability:.4f}")