from inference.efficientnet_inference import EfficientNetInference


MODEL_PATH = "models/efficientnet/efficientnet_b3_optimized.onnx"
CLASS_NAMES_PATH = "models/efficientnet/class_names.json"

IMAGE_PATH = r"D:\Loov_Vision_Ai\tests\test_image.png"


model = EfficientNetInference(
    model_path=MODEL_PATH,
    class_names_path=CLASS_NAMES_PATH
)

result = model.predict(IMAGE_PATH)

print("\n==============================")
print("EfficientNet-B3 Result")
print("==============================")

print("Model:", result.model)
print("Prediction:", result.prediction)
print("Confidence:", result.confidence)

print("\nProbabilities:")

for class_name, probability in result.probabilities.items():
    print(f"{class_name}: {probability:.4f}")