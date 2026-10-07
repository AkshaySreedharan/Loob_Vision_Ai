import json
from pathlib import Path

import numpy as np
import onnxruntime as ort

from inference.base import BaseModel
from preprocessing.efficientnet_preprocessing import preprocess_image
from schemas.model_result import ModelResult


class EfficientNetInference(BaseModel):

    def __init__(self, model_path, class_names_path):

        self.model_path = Path(model_path)
        self.class_names_path = Path(class_names_path)

        # --------------------------------------------------
        # LOAD ONNX MODEL
        # --------------------------------------------------

        self.session = ort.InferenceSession(
            str(self.model_path),
            providers=["CPUExecutionProvider"]
        )

        # Model input information
        input_info = self.session.get_inputs()[0]

        self.input_name = input_info.name
        self.input_shape = input_info.shape

        # Model output information
        output_info = self.session.get_outputs()[0]

        self.output_name = output_info.name
        self.output_shape = output_info.shape

        # --------------------------------------------------
        # LOAD CLASS NAMES
        # --------------------------------------------------

        with open(self.class_names_path, "r") as f:
            self.class_names = json.load(f)

        # --------------------------------------------------
        # VALIDATE MODEL
        # --------------------------------------------------

        if len(self.class_names) != 3:
            raise ValueError(
                f"Expected 3 classes, found {len(self.class_names)}"
            )

        print("=" * 60)
        print("EfficientNet-B3 ONNX Model Loaded")
        print("=" * 60)
        print("Model:", self.model_path)
        print("Input name:", self.input_name)
        print("Input shape:", self.input_shape)
        print("Output name:", self.output_name)
        print("Output shape:", self.output_shape)
        print("Classes:", self.class_names)
        print("=" * 60)

    def predict(self, image_path):

        # --------------------------------------------------
        # PREPROCESS IMAGE
        # --------------------------------------------------

        image = preprocess_image(image_path)

        # --------------------------------------------------
        # RUN ONNX INFERENCE
        # --------------------------------------------------

        outputs = self.session.run(
            [self.output_name],
            {
                self.input_name: image
            }
        )

        # Output shape:
        # (1, 3)
        probabilities = outputs[0][0]

        probabilities = np.asarray(
            probabilities,
            dtype=np.float32
        )

        # --------------------------------------------------
        # VALIDATE OUTPUT
        # --------------------------------------------------

        if len(probabilities) != len(self.class_names):
            raise ValueError(
                "Number of model outputs does not match "
                "number of class names."
            )

        # Your ONNX model already contains a softmax output.
        # Therefore, DO NOT apply softmax here.

        probability_sum = float(np.sum(probabilities))

        if not np.isclose(probability_sum, 1.0, atol=1e-3):
            print(
                f"Warning: probability sum = {probability_sum:.6f}"
            )

        # --------------------------------------------------
        # FIND PREDICTION
        # --------------------------------------------------

        predicted_index = int(
            np.argmax(probabilities)
        )

        predicted_class = self.class_names[
            predicted_index
        ].upper()

        confidence = float(
            probabilities[predicted_index]
        )

        # --------------------------------------------------
        # CREATE PROBABILITY DICTIONARY
        # --------------------------------------------------

        probability_dict = {
            self.class_names[i].upper():
            float(probabilities[i])
            for i in range(len(self.class_names))
        }

        # --------------------------------------------------
        # RETURN STANDARD MODEL RESULT
        # --------------------------------------------------

        return ModelResult(
            model="efficientnet_b3",
            prediction=predicted_class,
            probabilities=probability_dict,
            confidence=confidence
        )