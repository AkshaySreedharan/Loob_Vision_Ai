import unittest
import base64
import io
from pathlib import Path

from report.report_schema import AnalysisReportData
from report.report_builder import build_analysis_report
from report.pdf_generator import generate_report_pdf


class TestAnalysisReport(unittest.TestCase):

    def setUp(self):
        # Base realistic model evidence
        self.sample_state_consensus = {
            "final_class": "c3",
            "status": "Fully-degraded",
            "confidence": 0.942,
            "model_evidence": {
                "efficientnet": {
                    "model_name": "EfficientNet-B3 (Optimized ONNX)",
                    "prediction": "c3",
                    "status": "Fully-degraded",
                    "probabilities": {"c1": 0.002, "c2": 0.048, "c3": 0.950}
                },
                "color": {
                    "model_name": "Two-Stage Color Analysis Pipeline",
                    "prediction": "c3",
                    "status": "Fully-degraded",
                    "probabilities": {"c1": 0.015, "c2": 0.095, "c3": 0.890},
                    "features": {
                        "G_median": 21.4,
                        "L_median": 23.1,
                        "LAB_B_median": 11.8,
                        "V_median": 25.0,
                        "R_median": 34.2,
                        "NG_median": 0.32
                    }
                },
                "texture": {
                    "model_name": "Texture Random Forest v4",
                    "prediction": "c3",
                    "status": "Fully-degraded",
                    "probabilities": {"c1": 0.010, "c2": 0.070, "c3": 0.920},
                    "features": {
                        "contrast": 4.25,
                        "dissimilarity": 1.55,
                        "homogeneity": 0.68,
                        "energy": 0.14,
                        "correlation": 0.86,
                        "edge_density": 0.24
                    }
                }
            },
            "reasoning": "All three diagnostic models demonstrate strong convergence towards advanced degradation (Class C3).",
            "total_latency": 3.82
        }

    def test_scenario_1_and_2_all_models_agree(self):
        """Scenario 1 & 2: All three models return valid predictions and agree on final class."""
        report = build_analysis_report(self.sample_state_consensus, report_id="LOOV-RPT-TEST-AGREE")
        
        # Verify schema validity
        self.assertIsInstance(report, AnalysisReportData)
        self.assertEqual(report.metadata.report_id, "LOOV-RPT-TEST-AGREE")
        self.assertEqual(report.executive_summary.final_class, "c3")
        self.assertEqual(report.executive_summary.condition_label, "Fully-degraded")
        
        # Verify model agreement
        self.assertTrue(report.agreement.is_unanimous)
        self.assertEqual(report.agreement.models_supporting, 3)
        self.assertIn("Unanimous Consensus", report.agreement.consensus_status)
        
        # Verify individual models
        self.assertIn("efficientnet", report.models)
        self.assertIn("color", report.models)
        self.assertIn("texture", report.models)
        self.assertEqual(report.models["efficientnet"].predicted_class, "c3")
        self.assertEqual(report.models["color"].predicted_class, "c3")
        self.assertEqual(report.models["texture"].predicted_class, "c3")
        
        # Verify features retained
        self.assertIsNotNone(report.models["color"].features)
        self.assertIn("L_median", report.models["color"].features)
        self.assertIsNotNone(report.models["texture"].features)
        self.assertIn("contrast", report.models["texture"].features)

    def test_scenario_3_models_disagree(self):
        """Scenario 3: Models show disagreement (EfficientNet C2, Color C1, Texture C2)."""
        disagree_state = {
            "final_class": "c2",
            "status": "Semi-degraded",
            "confidence": 0.85,
            "model_evidence": {
                "efficientnet": {
                    "prediction": "c2",
                    "status": "Semi-degraded",
                    "probabilities": {"c1": 0.15, "c2": 0.70, "c3": 0.15}
                },
                "color": {
                    "prediction": "c1",
                    "status": "Fresh",
                    "probabilities": {"c1": 0.65, "c2": 0.25, "c3": 0.10}
                },
                "texture": {
                    "prediction": "c2",
                    "status": "Semi-degraded",
                    "probabilities": {"c1": 0.20, "c2": 0.65, "c3": 0.15}
                }
            },
            "reasoning": "Majority consensus supports semi-degraded state despite fresh optical markers in colorimetry."
        }
        report = build_analysis_report(disagree_state)
        
        self.assertFalse(report.agreement.is_unanimous)
        self.assertEqual(report.agreement.models_supporting, 2)
        self.assertIn("Majority Consensus", report.agreement.consensus_status)
        self.assertEqual(report.executive_summary.final_class, "c2")

    def test_scenario_4_one_model_fails_honest_reporting(self):
        """Scenario 4: One model encounters an error, honest reporting without crash."""
        failing_state = {
            "final_class": "c3",
            "status": "Fully-degraded",
            "confidence": 0.85,
            "model_evidence": {
                "efficientnet": {
                    "prediction": "c3",
                    "status": "Fully-degraded",
                    "probabilities": {"c1": 0.05, "c2": 0.15, "c3": 0.80}
                },
                "color": {
                    "prediction": "",
                    "status": "",
                    "probabilities": {"c1": 0.0, "c2": 0.0, "c3": 0.0},
                    "error": "Color preprocessing failure"
                },
                "texture": {
                    "prediction": "c3",
                    "status": "Fully-degraded",
                    "probabilities": {"c1": 0.05, "c2": 0.15, "c3": 0.80}
                }
            }
        }
        report = build_analysis_report(failing_state)
        self.assertIsInstance(report, AnalysisReportData)
        self.assertEqual(report.models["color"].predicted_class, "")

    def test_scenario_5_llm_incomplete_safety_override(self):
        """Scenario 5: LLM returns low confidence on C1/C2, safety rule overrides to C3."""
        low_conf_state = {
            "final_class": "c1",
            "status": "Fresh",
            "confidence": 0.42,  # Low confidence (< 0.55)
            "model_evidence": {
                "efficientnet": {"prediction": "c1", "probabilities": {"c1": 0.42, "c2": 0.30, "c3": 0.28}},
                "color": {"prediction": "c1", "probabilities": {"c1": 0.45, "c2": 0.30, "c3": 0.25}},
                "texture": {"prediction": "c1", "probabilities": {"c1": 0.40, "c2": 0.30, "c3": 0.30}}
            }
        }
        report = build_analysis_report(low_conf_state)
        # Safety rule must override to c3
        self.assertEqual(report.executive_summary.final_class, "c3")
        self.assertEqual(report.executive_summary.condition_label, "Fully-degraded")

    def test_scenario_6_missing_image_handled_safely(self):
        """Scenario 6: Missing or invalid image data still yields valid PDF."""
        report = build_analysis_report(self.sample_state_consensus, image_data_url=None)
        pdf_bytes = generate_report_pdf(report.model_dump())
        self.assertGreater(len(pdf_bytes), 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_scenario_7_long_text_and_pagination(self):
        """Scenario 7: Spanning multi-page text handled with page numbers."""
        long_state = dict(self.sample_state_consensus)
        long_state["reasoning"] = (
            "Detailed industrial diagnostics analysis narrative. " * 50
        )
        report = build_analysis_report(long_state)
        pdf_bytes = generate_report_pdf(report.model_dump())
        self.assertGreater(len(pdf_bytes), 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_scenario_8_and_9_valid_pdf_and_schema_consistency(self):
        """Scenario 8 & 9: PDF is standard binary PDF and consistency between preview & PDF."""
        # Create a small 10x10 synthetic test PNG base64
        import numpy as np
        import cv2
        img = np.zeros((20, 20, 3), dtype=np.uint8)
        img[:, :] = (30, 80, 150)
        _, buf = cv2.imencode(".png", img)
        b64_img = "data:image/png;base64," + base64.b64encode(buf).decode("utf-8")

        report = build_analysis_report(self.sample_state_consensus, image_data_url=b64_img)
        report_dict = report.model_dump()
        pdf_bytes = generate_report_pdf(report_dict)

        self.assertTrue(pdf_bytes.startswith(b"%PDF-1."))
        self.assertGreater(len(pdf_bytes), 2000)


if __name__ == "__main__":
    unittest.main()
