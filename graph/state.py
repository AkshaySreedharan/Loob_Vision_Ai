from typing import TypedDict, Dict, Any, Optional


class LubricantState(TypedDict, total=False):

    # ============================================================
    # INPUT
    # ============================================================

    image_path: str

    # ============================================================
    # VISION LLM GATE
    # ============================================================

    is_lubricant: bool
    gate_confidence: float
    gate_reasoning: str

    # ============================================================
    # INDIVIDUAL MODEL EVIDENCE
    # ============================================================

    efficientnet_evidence: Dict[str, Any]
    color_evidence: Dict[str, Any]
    texture_evidence: Dict[str, Any]

    # ============================================================
    # COMBINED EVIDENCE
    # ============================================================

    model_evidence: Dict[str, Any]

    # ============================================================
    # FINAL DECISION
    # ============================================================

    final_class: str
    status: str
    confidence: float
    model_weights: Dict[str, float]
    reasoning: str
    analysis_report: str

    # ============================================================
    # LATENCY
    # ============================================================

    gate_latency: float
    efficientnet_latency: float
    color_latency: float
    texture_latency: float
    model_stage_latency: float
    decision_latency: float
    total_latency: float

    # ============================================================
    # ERROR
    # ============================================================

    error: Optional[str]
