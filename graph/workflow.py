from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from graph.state import LubricantState

from graph.nodes import (
    lubricant_gate_node,
    efficientnet_node,
    color_node,
    texture_node,
    combine_model_evidence_node,
    decision_llm_node,
    reject_non_lubricant_node,
)


# ============================================================
# ROUTING AFTER VISION GATE
# ============================================================

def route_after_gate(
    state: LubricantState
):
    """
    If lubricant:
        run EfficientNet, Color and Texture.

    If not lubricant:
        reject immediately.
    """

    if state.get(
        "is_lubricant",
        False
    ):

        # Returning multiple destinations causes the
        # three model branches to execute in parallel.

        return [
            "efficientnet",
            "color",
            "texture",
        ]

    return "reject_non_lubricant"


# ============================================================
# BUILD WORKFLOW
# ============================================================

def build_workflow():

    workflow = StateGraph(
        LubricantState
    )

    # ========================================================
    # NODES
    # ========================================================

    workflow.add_node(
        "lubricant_gate",
        lubricant_gate_node
    )

    workflow.add_node(
        "efficientnet",
        efficientnet_node
    )

    workflow.add_node(
        "color",
        color_node
    )

    workflow.add_node(
        "texture",
        texture_node
    )

    workflow.add_node(
        "combine_model_evidence",
        combine_model_evidence_node
    )

    workflow.add_node(
        "decision_llm",
        decision_llm_node
    )

    workflow.add_node(
        "reject_non_lubricant",
        reject_non_lubricant_node
    )

    # ========================================================
    # START -> GATE
    # ========================================================

    workflow.add_edge(
        START,
        "lubricant_gate"
    )

    # ========================================================
    # GATE -> THREE PARALLEL MODELS
    # ========================================================

    workflow.add_conditional_edges(
        "lubricant_gate",
        route_after_gate,
        {
            "efficientnet":
                "efficientnet",

            "color":
                "color",

            "texture":
                "texture",

            "reject_non_lubricant":
                "reject_non_lubricant",
        },
    )

    # ========================================================
    # THREE MODELS -> COMBINE
    #
    # LangGraph waits for the parallel branches before
    # continuing through the downstream join.
    # ========================================================

    workflow.add_edge(
        "efficientnet",
        "combine_model_evidence"
    )

    workflow.add_edge(
        "color",
        "combine_model_evidence"
    )

    workflow.add_edge(
        "texture",
        "combine_model_evidence"
    )

    # ========================================================
    # COMBINE -> DECISION LLM
    # ========================================================

    workflow.add_edge(
        "combine_model_evidence",
        "decision_llm"
    )

    # ========================================================
    # END PATHS
    # ========================================================

    workflow.add_edge(
        "decision_llm",
        END
    )

    workflow.add_edge(
        "reject_non_lubricant",
        END
    )

    # ========================================================
    # COMPILE
    # ========================================================

    return workflow.compile()
