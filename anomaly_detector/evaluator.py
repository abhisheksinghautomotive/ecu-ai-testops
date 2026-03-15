"""Metrics evaluator for Anomaly Detector inference outputs.

Calculates precision and recall against the injected fault_labels in the parquet logs.
"""

from typing import Any

import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score


class Evaluator:
    """Calculates metrics for a given anomaly_report.json against signal logs."""

    def __init__(self, log_df: pd.DataFrame, report: dict[str, Any]) -> None:
        """Initialize the Evaluator.

        Args:
            log_df: The raw signal log DataFrame from Parquet containing the 'fault_label'.
            report: The generated report from the Detector containing flagged 'signal_id' anomalies.
        """
        self.df = log_df
        self.report = report

    def evaluate(self) -> dict[str, float]:
        """Calculate Precision, Recall, and F1-score.

        Returns:
            Dictionary mapping metric name to float value.
        """
        if "fault_label" not in self.df.columns:
            print("Warning: 'fault_label' column not found in log. Returning empty metrics.")
            return {}

        # Ground truth mapping: signal_id -> True/False
        # Assuming the fault label is uniformly true/false for all rows in a sequence
        grouped = self.df.groupby("signal_id")["fault_label"].first()

        # Build predicted anomalies list from the report
        predicted_anomaly_ids = {
            anomaly["signal_id"] for anomaly in self.report.get("anomalies", [])
        }

        # Align ground truth and predictions
        y_true = []
        y_pred = []

        for signal_id, is_fault in grouped.items():
            y_true.append(bool(is_fault))
            y_pred.append(str(signal_id) in predicted_anomaly_ids)

        if not y_true:
            return {}

        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        metrics = {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
        }

        print("--- Evaluation Metrics ---")
        for k, v in metrics.items():
            print(f"{k.capitalize()}: {v:.4f}")
        print("--------------------------")

        return metrics
