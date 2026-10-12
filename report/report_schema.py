from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ModelPredictionDetail(BaseModel):
    """Detailed predictions, probabilities, and features for an individual model."""
    model_name: str
    weight: float
    predicted_class: str
    condition_label: str
    probabilities: Dict[str, float]
    features: Optional[Dict[str, float]] = None
    interpretation: str


class ModelAgreementDetail(BaseModel):
    """Analysis of inter-model agreement and consensus level."""
    majority_class: str
    majority_label: str
    models_supporting: int
    total_models: int
    is_unanimous: bool
    consensus_status: str
    agreement_analysis: str


class ExecutiveSummary(BaseModel):
    """High-level executive assessment of lubricant health."""
    final_class: str
    condition_label: str
    confidence_score: float
    confidence_pct: str
    summary_headline: str
    summary_text: str
    operational_urgency: str


class EvidenceReasoning(BaseModel):
    """Evidence synthesis and reasoning narrative."""
    decision_narrative: str
    supporting_factors: List[str]
    uncertainties_or_caveats: List[str]


class RecommendationDetail(BaseModel):
    """Actionable industrial operational recommendations."""
    primary_action: str
    operational_guidance: List[str]
    laboratory_advisory: str


class ReportMetadata(BaseModel):
    """Traceability and execution metadata."""
    report_id: str
    timestamp_iso: str
    timestamp_formatted: str
    system_version: str = "LOOV VISION AI v2.4 (Industrial Edition)"
    inspection_type: str = "Optical Multi-Model Lubricant Screening"
    image_format: Optional[str] = "PNG / JPEG"
    processing_latency_sec: Optional[float] = None


class AnalysisReportData(BaseModel):
    """Complete standardized analysis report data schema."""
    metadata: ReportMetadata
    executive_summary: ExecutiveSummary
    models: Dict[str, ModelPredictionDetail]
    agreement: ModelAgreementDetail
    reasoning: EvidenceReasoning
    recommendations: RecommendationDetail
    disclaimer: str
    image_base64: Optional[str] = None
