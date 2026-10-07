import joblib

from preprocessing.color_preprocess import (
    extract_color_features,
    extract_color_feature_vector,
)


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = r"D:\Loov_Vision_Ai\models\color\color_analysis_pipeline.joblib"
IMAGE_PATH = r"D:\Loov_Vision_Ai\tests\test_image.png"


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("COLOR ANALYSIS MODEL TEST")
print("=" * 60)

print("\nLoading model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")
print("Classes:", model.classes_)
print("Expected features:", model.feature_names)


# ============================================================
# EXTRACT FEATURES
# ============================================================

print("\nExtracting color features...")

features = extract_color_features(IMAGE_PATH)

print("\nExtracted Features:")
print("-" * 40)

for name, value in features.items():
    print(f"{name:15s}: {value:.6f}")


# ============================================================
# CREATE FEATURE VECTOR
# ============================================================

X = extract_color_feature_vector(IMAGE_PATH)

print("\nFeature Vector:")
print(X)


# ============================================================
# PREDICTION PROBABILITIES
# ============================================================

print("\nPrediction Probabilities:")
print("-" * 40)

probabilities = model.predict_proba(X)

for class_name, probability in zip(model.classes_[0], probabilities[0]):
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