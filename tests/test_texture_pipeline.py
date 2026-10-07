import joblib

from preprocessing.texture_preprocess import (
    extract_image_features,
    extract_texture_feature_vector,
)


MODEL_PATH = (
    r"D:\Loov_Vision_Ai\models\texture"
    r"\texture_random_forest_v4.joblib"
)

FEATURES_PATH = (
    r"D:\Loov_Vision_Ai\models\texture"
    r"\texture_v4_features.joblib"
)

IMAGE_PATH = (
    r"D:\Loov_Vision_Ai\tests\test_image.png"
)


print("=" * 65)
print("TEXTURE ANALYSIS MODEL V4 TEST")
print("=" * 65)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

model = joblib.load(
    MODEL_PATH
)

print("Model loaded successfully.")

print(
    "Classes:",
    model.classes_
)


# ============================================================
# LOAD FEATURE NAMES
# ============================================================

print("\nLoading feature names...")

feature_names = joblib.load(
    FEATURES_PATH
)

if hasattr(
    feature_names,
    "feature_names"
):
    feature_names = (
        feature_names.feature_names
    )

feature_names = list(
    feature_names
)

print(
    "Expected feature count:",
    len(feature_names)
)


# ============================================================
# EXTRACT FEATURES
# ============================================================

print("\nExtracting Texture V4 features...")

features = extract_image_features(
    IMAGE_PATH
)

print(
    "Extracted feature count:",
    len(features)
)


# ============================================================
# CREATE FEATURE VECTOR
# ============================================================

X = extract_texture_feature_vector(
    IMAGE_PATH,
    FEATURES_PATH
)

print(
    "Feature vector shape:",
    X.shape
)


# ============================================================
# CHECK FEATURE COUNT
# ============================================================

if X.shape[1] != len(feature_names):

    raise ValueError(
        f"Feature mismatch: "
        f"{X.shape[1]} vs "
        f"{len(feature_names)}"
    )


# ============================================================
# SHOW FIRST FEATURES
# ============================================================

print("\nFirst 10 extracted features:")
print("-" * 50)

for name, value in list(
    features.items()
)[:10]:

    print(
        f"{name}: {value:.6f}"
    )


# ============================================================
# PREDICTION
# ============================================================

print("\nRunning prediction...")

prediction = model.predict(
    X
)


# ============================================================
# PROBABILITIES
# ============================================================

print("\nPrediction Probabilities:")
print("-" * 50)

probabilities = model.predict_proba(
    X
)

for class_name, probability in zip(
    model.classes_,
    probabilities[0]
):

    print(
        f"{class_name}: {probability:.4f}"
    )


# ============================================================
# FINAL RESULT
# ============================================================

class_mapping = {
    "c1": "Fresh",
    "c2": "Semi-degraded",
    "c3": "Fully-degraded",
}


print("\nFinal Prediction:")
print("-" * 50)

print(
    "Class :",
    prediction[0]
)

print(
    "Status:",
    class_mapping.get(
        prediction[0],
        prediction[0]
    )
)


print("\n" + "=" * 65)
print("TEXTURE MODEL TEST COMPLETED")
print("=" * 65)