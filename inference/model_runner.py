from pathlib import Path
from collections import Counter
import json

import numpy as np
import pandas as pd
import joblib

from inference.efficientnet_inference import EfficientNetInference
from preprocessing.color_preprocess import extract_color_feature_vector, extract_color_features
from preprocessing.texture_preprocess import extract_image_features


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]


# ============================================================
# MODEL PATHS
# ============================================================

EFFICIENTNET_MODEL = (
    BASE_DIR
    / "models"
    / "efficientnet"
    / "efficientnet_b3_optimized.onnx"
)

EFFICIENTNET_CLASSES = (
    BASE_DIR
    / "models"
    / "efficientnet"
    / "class_names.json"
)

COLOR_MODEL = (
    BASE_DIR
    / "models"
    / "color"
    / "color_analysis_pipeline.joblib"
)

TEXTURE_MODEL = (
    BASE_DIR
    / "models"
    / "texture"
    / "texture_random_forest_v4.joblib"
)

TEXTURE_FEATURES = (
    BASE_DIR
    / "models"
    / "texture"
    / "texture_v4_features.joblib"
)


# ============================================================
# CLASS STATUS
# ============================================================

STATUS_NAMES = {
    "c1": "Fresh",
    "c2": "Semi-degraded",
    "c3": "Fully-degraded",
}


# ============================================================
# LUBRICANT MODEL RUNNER
# ============================================================

class LubricantModelRunner:

    def __init__(self):

        print("Loading lubricant models...")

        # ====================================================
        # EFFICIENTNET
        # ====================================================
        #
        # IMPORTANT:
        # We use the existing EfficientNetInference class.
        #
        # This means model_runner uses the EXACT same
        # preprocessing and inference pipeline as the
        # independently tested EfficientNet model.
        #
        # ====================================================

        self.efficientnet = EfficientNetInference(
            str(EFFICIENTNET_MODEL),
            str(EFFICIENTNET_CLASSES)
        )

        # ====================================================
        # COLOR ANALYSIS MODEL
        # ====================================================

        self.color_model = joblib.load(
            COLOR_MODEL
        )

        # ====================================================
        # TEXTURE ANALYSIS MODEL
        # ====================================================

        self.texture_model = joblib.load(
            TEXTURE_MODEL
        )

        self.texture_feature_names = joblib.load(
            TEXTURE_FEATURES
        )

        print("All models loaded successfully.")

    # ========================================================
    # HELPER
    # ========================================================

    @staticmethod
    def probabilities_to_dict(
        classes,
        probabilities
    ):

        return {
            str(class_name): round(
                float(probability),
                6
            )
            for class_name, probability
            in zip(
                classes,
                probabilities
            )
        }

    # ========================================================
    # HELPER
    # ========================================================

    @staticmethod
    def get_prediction(
        classes,
        probabilities
    ):

        index = int(
            np.argmax(probabilities)
        )

        return str(
            classes[index]
        )

    # ========================================================
    # EFFICIENTNET PREDICTION
    # ========================================================

    def predict_efficientnet(
        self,
        image_path
    ):

        image_path = Path(
            image_path
        )

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # ----------------------------------------------------
        # IMPORTANT
        #
        # Do NOT preprocess the image manually here.
        #
        # The existing EfficientNetInference class already
        # contains the verified preprocessing pipeline.
        # ----------------------------------------------------

        result = self.efficientnet.predict(
            str(image_path)
        )

        # ----------------------------------------------------
        # ModelResult is a Pydantic object.
        #
        # Therefore use:
        #
        #     result.prediction
        #
        # instead of:
        #
        #     result.get("prediction")
        # ----------------------------------------------------

        prediction = str(
            result.prediction
        ).lower()

        # ----------------------------------------------------
        # Get probabilities
        # ----------------------------------------------------

        probabilities = result.probabilities

        # ----------------------------------------------------
        # If probabilities are returned as a dictionary
        # ----------------------------------------------------

        if isinstance(
            probabilities,
            dict
        ):

            probability_dict = {

                str(key).lower():
                    round(
                        float(value),
                        6
                    )

                for key, value
                in probabilities.items()
            }

        # ----------------------------------------------------
        # If probabilities are returned as a list/array
        # ----------------------------------------------------

        else:

            probabilities = np.asarray(
                probabilities,
                dtype=np.float32
            )

            classes = [
                "c1",
                "c2",
                "c3"
            ]

            probability_dict = (
                self.probabilities_to_dict(
                    classes,
                    probabilities
                )
            )

        # ----------------------------------------------------
        # Return standardized result
        # ----------------------------------------------------

        return {

            "model_name":
                "EfficientNet-B3 (Optimized ONNX)",

            "prediction":
                prediction,

            "status":
                STATUS_NAMES.get(
                    prediction,
                    prediction
                ),

            "probabilities":
                probability_dict
        }

    # ========================================================
    # COLOR ANALYSIS PREDICTION
    # ========================================================

    def predict_color(
        self,
        image_path
    ):

        # ----------------------------------------------------
        # Extract the EXACT color features used during
        # training.
        # ----------------------------------------------------

        color_feature_dict = extract_color_features(
            image_path
        )

        features = np.array(
            [[
                color_feature_dict["G_median"],
                color_feature_dict["L_median"],
                color_feature_dict["LAB_B_median"],
                color_feature_dict["V_median"],
                color_feature_dict["R_median"],
                color_feature_dict["NG_median"],
            ]],
            dtype=np.float32
        )

        # ----------------------------------------------------
        # Probability prediction
        # ----------------------------------------------------

        probabilities = (
            self.color_model
            .predict_proba(
                features
            )[0]
        )

        # ----------------------------------------------------
        # Model classes
        # ----------------------------------------------------

        classes = list(
            self.color_model.classes_
        )

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction = self.get_prediction(
            classes,
            probabilities
        )

        # ----------------------------------------------------
        # Return standardized result
        # ----------------------------------------------------

        return {

            "model_name":
                "Two-Stage Color Analysis Pipeline",

            "prediction":
                prediction,

            "status":
                STATUS_NAMES.get(
                    prediction,
                    prediction
                ),

            "probabilities":
                self.probabilities_to_dict(
                    classes,
                    probabilities
                ),

            "features": {
                k: round(float(v), 4)
                for k, v in color_feature_dict.items()
            }
        }

    # ========================================================
    # TEXTURE ANALYSIS PREDICTION
    # ========================================================

    def predict_texture(
        self,
        image_path
    ):

        # ----------------------------------------------------
        # Extract exact texture features
        # ----------------------------------------------------

        features = extract_image_features(
            image_path
        )

        # ----------------------------------------------------
        # Preserve the EXACT feature order used during training.
        # ----------------------------------------------------

        feature_vector = [
            features[name]
            for name
            in self.texture_feature_names
        ]

        # ----------------------------------------------------
        # Create DataFrame using the original feature names.
        # ----------------------------------------------------

        X = pd.DataFrame(
            [feature_vector],
            columns=self.texture_feature_names
        )

        # ----------------------------------------------------
        # Prediction probabilities
        # ----------------------------------------------------

        probabilities = (
            self.texture_model
            .predict_proba(
                X
            )[0]
        )

        # ----------------------------------------------------
        # Classes
        # ----------------------------------------------------

        classes = list(
            self.texture_model.classes_
        )

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction = self.get_prediction(
            classes,
            probabilities
        )

        # ----------------------------------------------------
        # Key summary texture metrics for reporting
        # ----------------------------------------------------

        key_texture_metrics = {
            "contrast": round(float(features.get("contrast", 0.0)), 4),
            "dissimilarity": round(float(features.get("dissimilarity", 0.0)), 4),
            "homogeneity": round(float(features.get("homogeneity", 0.0)), 4),
            "energy": round(float(features.get("energy", 0.0)), 4),
            "correlation": round(float(features.get("correlation", 0.0)), 4),
            "edge_density": round(float(features.get("edge_density", 0.0)), 4),
        }

        # ----------------------------------------------------
        # Return standardized result
        # ----------------------------------------------------

        return {

            "model_name":
                "Texture Random Forest v4",

            "prediction":
                prediction,

            "status":
                STATUS_NAMES.get(
                    prediction,
                    prediction
                ),

            "probabilities":
                self.probabilities_to_dict(
                    classes,
                    probabilities
                ),

            "features":
                key_texture_metrics
        }

    # ========================================================
    # RUN ALL MODELS
    # ========================================================

    def predict_all(
        self,
        image_path
    ):

        image_path = Path(
            image_path
        )

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # ====================================================
        # EFFICIENTNET
        # ====================================================

        print(
            "\nRunning EfficientNet..."
        )

        efficientnet_result = (
            self.predict_efficientnet(
                image_path
            )
        )

        # ====================================================
        # COLOR ANALYSIS
        # ====================================================

        print(
            "Running Color Analysis..."
        )

        color_result = (
            self.predict_color(
                image_path
            )
        )

        # ====================================================
        # TEXTURE ANALYSIS
        # ====================================================

        print(
            "Running Texture Analysis..."
        )

        texture_result = (
            self.predict_texture(
                image_path
            )
        )

        # ====================================================
        # COLLECT MODEL PREDICTIONS
        # ====================================================

        predictions = [

            efficientnet_result[
                "prediction"
            ],

            color_result[
                "prediction"
            ],

            texture_result[
                "prediction"
            ]
        ]

        # ====================================================
        # MAJORITY INFORMATION
        # ====================================================
        #
        # This is ONLY model evidence.
        #
        # It is NOT the final decision.
        #
        # The future LLM layer will analyze:
        #
        # - probabilities
        # - confidence
        # - agreement
        # - disagreement
        # - model reliability
        #
        # and dynamically determine evidence weights.
        #
        # ====================================================

        counts = Counter(
            predictions
        )

        majority_class, majority_count = (
            counts.most_common(1)[0]
        )

        # ====================================================
        # COMPLETE MODEL EVIDENCE
        # ====================================================

        evidence = {

            "image":
                str(image_path),

            "models": {

                "efficientnet":
                    efficientnet_result,

                "color":
                    color_result,

                "texture":
                    texture_result
            },

            "agreement": {

                "majority_class":
                    majority_class,

                "models_supporting":
                    majority_count,

                "total_models":
                    3
            }
        }

        return evidence


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Test image
    # --------------------------------------------------------

    test_image = (
        BASE_DIR
        / "tests"
        / "test_image.png"
    )

    # --------------------------------------------------------
    # Load models
    # --------------------------------------------------------

    runner = LubricantModelRunner()

    # --------------------------------------------------------
    # Run all models
    # --------------------------------------------------------

    result = runner.predict_all(
        test_image
    )

    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("MODEL EVIDENCE")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=4
        )
    )