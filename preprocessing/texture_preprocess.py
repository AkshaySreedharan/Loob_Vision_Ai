import cv2
import numpy as np
import joblib
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern


IMAGE_SIZE = (300, 300)
GRID_SIZE = 3

GLCM_LEVELS = 32
GLCM_DISTANCES = [1, 2]
GLCM_ANGLES = [
    0,
    np.pi / 4,
    np.pi / 2,
    3 * np.pi / 4,
]

LBP_RADIUS = 3
LBP_POINTS = 24


def quantize_image(gray):
    quantized = (
        gray.astype(np.float32)
        / 256.0
        * GLCM_LEVELS
    ).astype(np.uint8)

    quantized[quantized >= GLCM_LEVELS] = GLCM_LEVELS - 1

    return quantized


def calculate_glcm_features(gray):

    quantized = quantize_image(gray)

    glcm = graycomatrix(
        quantized,
        distances=GLCM_DISTANCES,
        angles=GLCM_ANGLES,
        levels=GLCM_LEVELS,
        symmetric=True,
        normed=True
    )

    features = {}

    properties = [
        "contrast",
        "dissimilarity",
        "homogeneity",
        "energy",
        "correlation",
        "ASM"
    ]

    for prop in properties:

        values = graycoprops(
            glcm,
            prop
        )

        features[f"glcm_{prop.lower()}"] = float(
            np.mean(values)
        )

    return features


def calculate_lbp_features(gray):

    lbp = local_binary_pattern(
        gray,
        LBP_POINTS,
        LBP_RADIUS,
        method="uniform"
    )

    n_bins = LBP_POINTS + 2

    histogram, _ = np.histogram(
        lbp.ravel(),
        bins=np.arange(
            0,
            n_bins + 1
        ),
        range=(0, n_bins)
    )

    histogram = histogram.astype(np.float32)

    histogram /= (
        histogram.sum() + 1e-8
    )

    return histogram


def calculate_intensity_features(gray):

    values = gray.astype(
        np.float32
    ).ravel()

    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "median": float(np.median(values)),
        "p10": float(np.percentile(values, 10)),
        "p25": float(np.percentile(values, 25)),
        "p75": float(np.percentile(values, 75)),
        "p90": float(np.percentile(values, 90)),
        "range": float(
            np.max(values) - np.min(values)
        )
    }


def calculate_gradient_features(gray):

    gx = cv2.Sobel(
        gray,
        cv2.CV_32F,
        1,
        0,
        ksize=3
    )

    gy = cv2.Sobel(
        gray,
        cv2.CV_32F,
        0,
        1,
        ksize=3
    )

    magnitude = cv2.magnitude(
        gx,
        gy
    )

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    edge_density = np.mean(
        edges > 0
    )

    return {
        "gradient_mean": float(
            np.mean(magnitude)
        ),
        "gradient_std": float(
            np.std(magnitude)
        ),
        "gradient_max": float(
            np.max(magnitude)
        ),
        "edge_density": float(
            edge_density
        )
    }


def extract_patch_features(gray, prefix):

    features = {}

    # GLCM
    glcm_features = calculate_glcm_features(gray)

    for name, value in glcm_features.items():

        features[
            f"{prefix}_{name}"
        ] = value

    # LBP
    lbp_histogram = calculate_lbp_features(gray)

    for i, value in enumerate(lbp_histogram):

        features[
            f"{prefix}_lbp_{i}"
        ] = float(value)

    # Intensity
    intensity_features = calculate_intensity_features(gray)

    for name, value in intensity_features.items():

        features[
            f"{prefix}_intensity_{name}"
        ] = value

    # Gradient
    gradient_features = calculate_gradient_features(gray)

    for name, value in gradient_features.items():

        features[
            f"{prefix}_{name}"
        ] = value

    return features


def extract_image_features(image_path):

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    image = cv2.resize(
        image,
        IMAGE_SIZE,
        interpolation=cv2.INTER_AREA
    )

    features = {}

    # GLOBAL FEATURES
    global_features = extract_patch_features(
        image,
        "global"
    )

    features.update(
        global_features
    )

    # LOCAL 3 x 3 PATCHES
    height, width = image.shape

    patch_height = height // GRID_SIZE
    patch_width = width // GRID_SIZE

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            y1 = row * patch_height
            y2 = (row + 1) * patch_height

            x1 = col * patch_width
            x2 = (col + 1) * patch_width

            patch = image[
                y1:y2,
                x1:x2
            ]

            prefix = (
                f"patch_r{row + 1}"
                f"_c{col + 1}"
            )

            patch_features = extract_patch_features(
                patch,
                prefix
            )

            features.update(
                patch_features
            )

    # PATCH VARIATION FEATURES
    local_means = []
    local_stds = []
    local_edges = []

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            prefix = (
                f"patch_r{row + 1}"
                f"_c{col + 1}"
            )

            local_means.append(
                features[
                    f"{prefix}_intensity_mean"
                ]
            )

            local_stds.append(
                features[
                    f"{prefix}_intensity_std"
                ]
            )

            local_edges.append(
                features[
                    f"{prefix}_edge_density"
                ]
            )

    features[
        "local_mean_variation"
    ] = float(
        np.std(local_means)
    )

    features[
        "local_std_variation"
    ] = float(
        np.std(local_stds)
    )

    features[
        "local_edge_variation"
    ] = float(
        np.std(local_edges)
    )

    features[
        "local_mean_range"
    ] = float(
        np.max(local_means)
        -
        np.min(local_means)
    )

    features[
        "local_std_range"
    ] = float(
        np.max(local_stds)
        -
        np.min(local_stds)
    )

    if len(features) != 445:
        raise ValueError(
            f"Expected 445 features, got {len(features)}"
        )

    return features


def extract_texture_feature_vector(
    image_path,
    feature_names_path=None
):

    features = extract_image_features(
        image_path
    )

    if feature_names_path is not None:

        feature_names = joblib.load(
            feature_names_path
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

        if len(feature_names) != 445:
            raise ValueError(
                f"Expected 445 saved feature names, "
                f"got {len(feature_names)}"
            )

        missing = [
            name
            for name in feature_names
            if name not in features
        ]

        if missing:
            raise ValueError(
                f"Missing features: {missing[:10]}"
            )

    else:

        feature_names = list(
            features.keys()
        )

    X = np.array(
        [
            [
                features[name]
                for name in feature_names
            ]
        ],
        dtype=np.float32
    )

    return X