
import sys
import os
import json
import time


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


# ============================================================
# IMPORT WORKFLOW
# ============================================================

from graph.workflow import build_workflow


# ============================================================
# TEST IMAGE
# ============================================================

IMAGE_PATH = (
    r"D:\Loov_Vision_Ai\tests\test_image.png"
)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 75)
    print("LOOB VISION - LANGGRAPH LATENCY TEST")
    print("=" * 75)

    print(
        f"\nImage:\n{IMAGE_PATH}"
    )

    # ========================================================
    # BUILD GRAPH
    # ========================================================

    print(
        "\nBuilding LangGraph workflow..."
    )

    app = build_workflow()

    print(
        "LangGraph workflow compiled successfully."
    )

    # ========================================================
    # INITIAL STATE
    # ========================================================

    initial_state = {
        "image_path": IMAGE_PATH
    }

    # ========================================================
    # START TOTAL TIMER
    # ========================================================

    total_start = time.perf_counter()

    # ========================================================
    # RUN WORKFLOW
    # ========================================================

    result = app.invoke(
        initial_state
    )

    # ========================================================
    # TOTAL TIME
    # ========================================================

    total_latency = (
        time.perf_counter()
        - total_start
    )

    # ========================================================
    # FINAL DECISION
    # ========================================================

    print()
    print("=" * 75)
    print("FINAL DECISION")
    print("=" * 75)

    print(
        f"Class       : "
        f"{result.get('final_class')}"
    )

    print(
        f"Status      : "
        f"{result.get('status')}"
    )

    print(
        f"Confidence  : "
        f"{result.get('confidence')}"
    )

    # ========================================================
    # MODEL WEIGHTS
    # ========================================================

    print()
    print("=" * 75)
    print("MODEL WEIGHTS")
    print("=" * 75)

    weights = result.get(
        "model_weights",
        {}
    )

    print(
        f"EfficientNet : "
        f"{weights.get('efficientnet')}"
    )

    print(
        f"Color        : "
        f"{weights.get('color')}"
    )

    print(
        f"Texture      : "
        f"{weights.get('texture')}"
    )

    # ========================================================
    # LATENCY
    # ========================================================

    print()
    print("=" * 75)
    print("LATENCY ANALYSIS")
    print("=" * 75)

    gate_time = result.get(
        "gate_latency",
        0.0
    )

    efficientnet_time = result.get(
        "efficientnet_latency",
        0.0
    )

    color_time = result.get(
        "color_latency",
        0.0
    )

    texture_time = result.get(
        "texture_latency",
        0.0
    )

    model_stage_time = result.get(
        "model_stage_latency",
        0.0
    )

    decision_time = result.get(
        "decision_latency",
        0.0
    )

    print(
        f"Vision LLM Gate : "
        f"{gate_time:.3f} sec"
    )

    print(
        f"EfficientNet    : "
        f"{efficientnet_time:.3f} sec"
    )

    print(
        f"Color Analysis  : "
        f"{color_time:.3f} sec"
    )

    print(
        f"Texture Analysis: "
        f"{texture_time:.3f} sec"
    )

    print(
        "-" * 75
    )

    print(
        f"Parallel ML Stage: "
        f"{model_stage_time:.3f} sec"
    )

    print(
        f"Decision LLM     : "
        f"{decision_time:.3f} sec"
    )

    print(
        "-" * 75
    )

    print(
        f"TOTAL WORKFLOW   : "
        f"{total_latency:.3f} sec"
    )

    # ========================================================
    # REASONING
    # ========================================================

    print()
    print("=" * 75)
    print("REASONING")
    print("=" * 75)

    print(
        result.get(
            "reasoning",
            ""
        )
    )

    # ========================================================
    # REPORT
    # ========================================================

    print()
    print("=" * 75)
    print("ANALYSIS REPORT")
    print("=" * 75)

    print(
        result.get(
            "analysis_report",
            ""
        )
    )

    # ========================================================
    # COMPLETE RESULT
    # ========================================================

    print()
    print("=" * 75)
    print("COMPLETE WORKFLOW STATE")
    print("=" * 75)

    print(
        json.dumps(
            result,
            indent=4,
            default=str
        )
    )

    print()
    print("=" * 75)
    print("TEST COMPLETED")
    print("=" * 75)
