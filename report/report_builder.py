import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from report.report_schema import (
    AnalysisReportData,
    ReportMetadata,
    ExecutiveSummary,
    ModelPredictionDetail,
    ModelAgreementDetail,
    EvidenceReasoning,
    RecommendationDetail
)


CLASS_LABELS = {
    "c1": "Fresh",
    "c2": "Semi-degraded",
    "c3": "Fully-degraded",
}

CLASS_URGENCY = {
    "c1": "Normal Operational Condition",
    "c2": "Caution / Preventative Servicing Required",
    "c3": "Critical / Immediate Changeout Required",
}

CLASS_HEADLINES = {
    "c1": "LUBRICANT IN OPTIMAL HEALTHY CONDITION (GRADE C1)",
    "c2": "TRANSITIONAL DEGRADATION DETECTED (GRADE C2)",
    "c3": "ADVANCED DEGRADATION DETECTED (GRADE C3)",
}


def build_analysis_report(
    state: Dict[str, Any],
    image_data_url: Optional[str] = None,
    report_id: Optional[str] = None
) -> AnalysisReportData:
    """
    Constructs a validated AnalysisReportData instance from the actual LangGraph
    execution state or API response dictionary.
    """
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    now_formatted = now.strftime("%Y-%m-%d %H:%M:%S UTC")

    if not report_id:
        short_id = uuid.uuid4().hex[:6].upper()
        date_str = now.strftime("%Y%m%d")
        report_id = f"LOOV-RPT-{date_str}-{short_id}"

    # Extract model evidence blocks
    ev = state.get("model_evidence", {})
    eff_data = state.get("efficientnet_evidence") or ev.get("efficientnet", {})
    col_data = state.get("color_evidence") or ev.get("color", {})
    tex_data = state.get("texture_evidence") or ev.get("texture", {})

    # Determine final class, confidence, and status
    raw_final_class = str(state.get("final_class", "")).lower()
    raw_confidence = state.get("confidence", 0.0)

    try:
        conf_float = float(raw_confidence)
    except (ValueError, TypeError):
        conf_float = 0.0

    # Fallback voting if final_class was not set by LLM
    if raw_final_class not in {"c1", "c2", "c3"}:
        eff_p = str(eff_data.get("prediction", "")).lower()
        col_p = str(col_data.get("prediction", "")).lower()
        tex_p = str(tex_data.get("prediction", "")).lower()

        scores = {"c1": 0.0, "c2": 0.0, "c3": 0.0}
        if eff_p in scores:
            scores[eff_p] += 0.55
        if col_p in scores:
            scores[col_p] += 0.15
        if tex_p in scores:
            scores[tex_p] += 0.30

        raw_final_class = max(scores, key=scores.get)
        conf_float = scores[raw_final_class] if conf_float <= 0.0 else conf_float

    final_class = raw_final_class

    # Safety Override Rule: c1 or c2 with confidence < 0.55 overrides to c3
    if final_class in {"c1", "c2"} and conf_float < 0.55:
        final_class = "c3"

    condition_label = CLASS_LABELS.get(final_class, "Analyzed")
    conf_pct = f"{conf_float * 100:.1f}%"

    # Build individual model details
    models_dict = {}

    # 1. EfficientNet-B3
    eff_pred = str(eff_data.get("prediction", "-")).lower()
    eff_probs = eff_data.get("probabilities", {"c1": 0.0, "c2": 0.0, "c3": 0.0})
    eff_top_prob = eff_probs.get(eff_pred, 0.0) if isinstance(eff_probs, dict) else 0.0
    eff_interp = (
        f"Deep convolutional feature extraction via EfficientNet-B3 indicates strong alignment "
        f"with class {CLASS_LABELS.get(eff_pred, eff_pred.upper())} ({eff_top_prob * 100:.1f}% probability). "
        f"As the primary optical backbone with 55% model weight, it provides the core visual baseline."
    )
    models_dict["efficientnet"] = ModelPredictionDetail(
        model_name="EfficientNet-B3 (Optimized ONNX)",
        weight=0.55,
        predicted_class=eff_pred,
        condition_label=CLASS_LABELS.get(eff_pred, eff_pred.upper()),
        probabilities={k: float(v) for k, v in eff_probs.items()} if isinstance(eff_probs, dict) else {},
        features=None,
        interpretation=eff_interp
    )

    # 2. Color Analysis
    col_pred = str(col_data.get("prediction", "-")).lower()
    col_probs = col_data.get("probabilities", {"c1": 0.0, "c2": 0.0, "c3": 0.0})
    col_features = col_data.get("features", {})
    if col_features:
        l_val = col_features.get("L_median", "N/A")
        v_val = col_features.get("V_median", "N/A")
        ng_val = col_features.get("NG_median", "N/A")
        col_interp = (
            f"Two-stage colorimetric pipeline extracted median optical markers: "
            f"Lightness L={l_val}, HSV Value V={v_val}, and Normalized Green NG={ng_val}. "
            f"Color features corroborate {CLASS_LABELS.get(col_pred, col_pred.upper())} classification."
        )
    else:
        col_interp = (
            f"Two-stage colorimetric pipeline classified sample as {CLASS_LABELS.get(col_pred, col_pred.upper())} "
            f"based on median chromaticity and luminance distributions."
        )
    models_dict["color"] = ModelPredictionDetail(
        model_name="Two-Stage Color Analysis Pipeline",
        weight=0.15,
        predicted_class=col_pred,
        condition_label=CLASS_LABELS.get(col_pred, col_pred.upper()),
        probabilities={k: float(v) for k, v in col_probs.items()} if isinstance(col_probs, dict) else {},
        features=col_features if isinstance(col_features, dict) else None,
        interpretation=col_interp
    )

    # 3. Texture Analysis
    tex_pred = str(tex_data.get("prediction", "-")).lower()
    tex_probs = tex_data.get("probabilities", {"c1": 0.0, "c2": 0.0, "c3": 0.0})
    tex_features = tex_data.get("features", {})
    if tex_features:
        contrast = tex_features.get("contrast", "N/A")
        homogeneity = tex_features.get("homogeneity", "N/A")
        energy = tex_features.get("energy", "N/A")
        tex_interp = (
            f"Random Forest texture classifier evaluated GLCM surface spatial matrices: "
            f"Contrast={contrast}, Homogeneity={homogeneity}, Energy={energy}. "
            f"Spatial co-occurrence characteristics indicate {CLASS_LABELS.get(tex_pred, tex_pred.upper())} condition."
        )
    else:
        tex_interp = (
            f"Random Forest texture classifier evaluated multi-scale spatial surface matrices, "
            f"identifying patterns characteristic of {CLASS_LABELS.get(tex_pred, tex_pred.upper())}."
        )
    models_dict["texture"] = ModelPredictionDetail(
        model_name="Texture Random Forest v4",
        weight=0.30,
        predicted_class=tex_pred,
        condition_label=CLASS_LABELS.get(tex_pred, tex_pred.upper()),
        probabilities={k: float(v) for k, v in tex_probs.items()} if isinstance(tex_probs, dict) else {},
        features=tex_features if isinstance(tex_features, dict) else None,
        interpretation=tex_interp
    )

    # Agreement analysis
    pred_list = [eff_pred, col_pred, tex_pred]
    valid_preds = [p for p in pred_list if p in {"c1", "c2", "c3"}]
    total_models = len(valid_preds) if valid_preds else 3

    counts = {"c1": pred_list.count("c1"), "c2": pred_list.count("c2"), "c3": pred_list.count("c3")}
    maj_class = max(counts, key=counts.get) if valid_preds else final_class
    maj_count = counts[maj_class] if valid_preds else 0
    is_unanimous = (maj_count == 3)

    if is_unanimous:
        consensus_status = "Unanimous Consensus (3/3 Models)"
        agreement_analysis = (
            f"All three independent machine learning models (EfficientNet-B3, Color Analysis, and Texture Analysis) "
            f"unanimously classified the sample as {CLASS_LABELS.get(maj_class, maj_class.upper())}. "
            f"This uniform agreement provides strong multi-modal confidence in the assessment."
        )
    elif maj_count == 2:
        consensus_status = "Majority Consensus (2/3 Models)"
        dissenting = [name for name, p in [("EfficientNet-B3", eff_pred), ("Color Analysis", col_pred), ("Texture Analysis", tex_pred)] if p != maj_class]
        dissent_str = ", ".join(dissenting)
        agreement_analysis = (
            f"Two of three models support {CLASS_LABELS.get(maj_class, maj_class.upper())}, while {dissent_str} "
            f"produced divergent output. Weighted evidence integration was applied to resolve the disagreement."
        )
    else:
        consensus_status = "Divergent Predictions (Split Evidence)"
        agreement_analysis = (
            "Each model indicated different condition characteristics across visual, colorimetric, and texture domains. "
            f"The final synthesized condition of {condition_label} was established by applying fixed weightings (55% / 15% / 30%) "
            "and risk-averse thresholding. Confirmatory laboratory testing is strongly advised."
        )

    agreement_detail = ModelAgreementDetail(
        majority_class=maj_class,
        majority_label=CLASS_LABELS.get(maj_class, maj_class.upper()),
        models_supporting=maj_count,
        total_models=total_models,
        is_unanimous=is_unanimous,
        consensus_status=consensus_status,
        agreement_analysis=agreement_analysis
    )

    # Executive summary & recommendations based on final_class
    if final_class == "c1":
        exec_text = (
            "The evaluated lubricant sample exhibits optical and physical surface characteristics representative "
            "of fresh, uncompromised lubricating oil. Colorimetry and luminance metrics show clear fluid transparency "
            "without evidence of soot accumulation, thermal oxidation, or particulate contamination."
        )
        primary_action = "Continue regular service interval; no corrective maintenance required."
        guidance = [
            "Maintain standard operating schedules and normal fluid monitoring frequency.",
            "Inspect seals and reservoir breathers during routine checks to prevent external particulate ingress.",
            "Record this baseline visual profile for future condition comparison."
        ]
    elif final_class == "c2":
        exec_text = (
            "The evaluated lubricant sample exhibits moderate degradation markers indicative of transitional fluid aging. "
            "Visual darkening and subtle texture irregularities suggest onset of additive depletion and particulate buildup. "
            "While still functioning, the fluid is nearing the end of its reliable operational lifecycle."
        )
        primary_action = "Schedule preventive lubricant replacement within the next operational maintenance cycle."
        guidance = [
            "Increase inspection and fluid sampling frequency to monitor degradation trajectory.",
            "Inspect filtration elements and clean magnetic plugs for particulate accumulation.",
            "Prepare fresh lubricant inventory to prevent unplanned machine downtime."
        ]
    else:  # c3
        exec_text = (
            "The evaluated lubricant sample demonstrates pronounced optical and surface characteristics associated "
            "with advanced degradation. Significant fluid darkening, high optical density, and textural particulate "
            "markers indicate severe oxidation, contamination, or additive failure."
        )
        primary_action = "Immediate fluid changeout recommended; avoid prolonged machine operation on this lubricant."
        guidance = [
            "Drain reservoir, flush lines, and install new replacement fluid meeting manufacturer viscosity specs.",
            "Replace oil filter elements and inspect for metal wear debris or sludge deposits.",
            "Perform root-cause evaluation if oil degraded prematurely (check operating temperature and seals)."
        ]

    exec_summary = ExecutiveSummary(
        final_class=final_class,
        condition_label=condition_label,
        confidence_score=round(conf_float, 4),
        confidence_pct=conf_pct,
        summary_headline=CLASS_HEADLINES.get(final_class, "LUBRICANT CONDITION REPORT"),
        summary_text=exec_text,
        operational_urgency=CLASS_URGENCY.get(final_class, "Operational Advisory")
    )

    # Reasoning narrative
    decision_reasoning_text = state.get("reasoning") or state.get("analysis_report") or (
        f"Final condition {condition_label} ({final_class.upper()}) was determined via multi-modal evidence synthesis. "
        f"EfficientNet-B3 (55% weight), Color Analysis (15% weight), and Texture Analysis (30% weight) were evaluated "
        f"alongside calculated probability distributions. Consensus level: {consensus_status}."
    )

    supporting_factors = [
        f"EfficientNet-B3 classified as {CLASS_LABELS.get(eff_pred, eff_pred.upper())} with 55% voting influence",
        f"Color Analysis classified as {CLASS_LABELS.get(col_pred, col_pred.upper())} with 15% voting influence",
        f"Texture Analysis classified as {CLASS_LABELS.get(tex_pred, tex_pred.upper())} with 30% voting influence",
        f"Combined confidence estimate: {conf_pct}",
    ]

    uncertainties = [
        "Visual inspection reflects surface optical properties; chemical parameters (TAN, TBN, metal ppm) are unmeasured.",
        "Ambient illumination and camera angle variations can introduce slight color temperature deviations.",
    ]
    if not is_unanimous:
        uncertainties.insert(0, f"Inter-model disagreement detected: {agreement_detail.agreement_analysis}")

    reasoning_detail = EvidenceReasoning(
        decision_narrative=decision_reasoning_text,
        supporting_factors=supporting_factors,
        uncertainties_or_caveats=uncertainties
    )

    recommendations_detail = RecommendationDetail(
        primary_action=primary_action,
        operational_guidance=guidance,
        laboratory_advisory=(
            "When high operational criticality or safety risks exist, complement automated visual screening "
            "with certified laboratory oil analysis (ASTM kinematic viscosity, FTIR spectroscopy, Karl Fischer moisture titration)."
        )
    )

    metadata = ReportMetadata(
        report_id=report_id,
        timestamp_iso=now_iso,
        timestamp_formatted=now_formatted,
        processing_latency_sec=round(float(state.get("total_latency", 0.0)), 3) if state.get("total_latency") else None
    )

    disclaimer = (
        "IMPORTANT NOTICE & LIMITATIONS: LOOV VISION AI provides automated multi-modal optical screening "
        "designed for rapid non-destructive lubricant monitoring. This automated assessment is derived solely "
        "from digital image analysis and does not constitute a certified laboratory lubricant test. "
        "It does not replace standardized chemical tests such as ASTM D445 kinematic viscosity, ASTM D664 acid number, "
        "or ICP elemental wear spectroscopy. Critical equipment decisions should be corroborated with approved industrial laboratory protocols."
    )

    return AnalysisReportData(
        metadata=metadata,
        executive_summary=exec_summary,
        models=models_dict,
        agreement=agreement_detail,
        reasoning=reasoning_detail,
        recommendations=recommendations_detail,
        disclaimer=disclaimer,
        image_base64=image_data_url
    )
