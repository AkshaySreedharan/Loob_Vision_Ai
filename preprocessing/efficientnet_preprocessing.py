import cv2
import numpy as np


IMAGE_SIZE = (300, 300)


def preprocess_image(image_path):
    """
    Preprocess an image for EfficientNet-B3 ONNX inference.

    Training configuration:
        - Image size: 300 x 300
        - 3 channels
        - RGB image
        - No inference-time augmentation
    """

    # Load image
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    # OpenCV loads images as BGR.
    # Convert to RGB because the model was trained using RGB images.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize to training size
    image = cv2.resize(
        image,
        IMAGE_SIZE,
        interpolation=cv2.INTER_AREA
    )

    # Convert to float32
    image = image.astype(np.float32)

    # Add batch dimension
    # (300, 300, 3)
    #       ↓
    # (1, 300, 300, 3)
    image = np.expand_dims(image, axis=0)

    return image