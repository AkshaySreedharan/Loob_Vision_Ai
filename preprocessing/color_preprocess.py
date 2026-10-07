import cv2
import numpy as np


# ============================================================
# COLOR MODEL FEATURE ORDER
# ============================================================

FEATURE_NAMES = [
    "G_median",
    "L_median",
    "LAB_B_median",
    "V_median",
    "R_median",
    "NG_median",
]


# ============================================================
# IMAGE → COLOR FEATURES
# ============================================================

def extract_color_features(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    # OpenCV loads image as BGR
    bgr = image

    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb = cv2.cvtColor(
        bgr,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------------
    # Convert RGB → HSV
    # --------------------------------------------------------

    hsv = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2HSV
    )

    # --------------------------------------------------------
    # Convert RGB → LAB
    # --------------------------------------------------------

    lab = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2LAB
    )

    # ========================================================
    # RGB CHANNELS
    # ========================================================

    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)

    # ========================================================
    # HSV V CHANNEL
    # ========================================================

    v = hsv[:, :, 2].astype(np.float32)

    # ========================================================
    # LAB CHANNELS
    # ========================================================

    l_channel = lab[:, :, 0].astype(np.float32)

    lab_b = lab[:, :, 2].astype(np.float32)

    # ========================================================
    # NORMALIZED GREEN
    # ========================================================

    rgb_sum = r + g + b + 1e-6

    ng = g / rgb_sum

    # ========================================================
    # SIX COLOR FEATURES
    # ========================================================

    features = {

        "G_median":
            float(np.median(g)),

        "L_median":
            float(np.median(l_channel)),

        "LAB_B_median":
            float(np.median(lab_b)),

        "V_median":
            float(np.median(v)),

        "R_median":
            float(np.median(r)),

        "NG_median":
            float(np.median(ng)),
    }

    return features


# ============================================================
# IMAGE → MODEL INPUT VECTOR
# ============================================================

def extract_color_feature_vector(image_path):

    features = extract_color_features(
        image_path
    )

    feature_vector = np.array(
        [[
            features["G_median"],
            features["L_median"],
            features["LAB_B_median"],
            features["V_median"],
            features["R_median"],
            features["NG_median"],
        ]],
        dtype=np.float32
    )

    return feature_vector