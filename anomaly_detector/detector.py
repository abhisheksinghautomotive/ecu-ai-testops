"""Inference module for ECU signal anomalies.

Loads the Isolation Forest model from MinIO and scores new data.
"""

import datetime
from typing import Any

import numpy as np
import pandas as pd

from anomaly_detector.feature_extractor import extract_features
from anomaly_detector.storage_client import StorageClient


class Detector:
    """Loads a model from MinIO to score sequences and flag anomalies."""

    def __init__(self, model_name: str = "isolation_forest.pkl") -> None:
        """Initialize the detector and load the model.

        Args:
            model_name: The object key of the model in the MinIO bucket.
        """
        self.storage = StorageClient()
        self.model_name = model_name
        self.model = None

    def detect_anomalies(
        self, df: pd.DataFrame, report_name: str = "anomaly_report.json"
    ) -> dict[str, Any]:
        """Run inference on the feature set and generate a report.

        Args:
            df: The raw signal log DataFrame from Parquet.
            report_name: The object name to save the report as in the MinIO bucket.

        Returns:
            The generated report dictionary.
        """
        if self.model is None:
            print(f"Loading model '{self.model_name}' from MinIO...")
            self.model = self.storage.load_model(self.model_name)

        if df.empty:
            return {"error": "Empty dataframe provided."}

        features_df = extract_features(df)

        models = self.storage.load_model(self.model_name)

        drop_cols = ["signal_id"]
        if "fault_label" in features_df.columns:
            drop_cols.append("fault_label")

        uds_mask = features_df["is_uds"] == 1.0
        obd_mask = features_df["is_obd"] == 1.0

        drop_cols.extend(["is_uds", "is_obd"])

        X_uds = features_df[uds_mask].drop(columns=drop_cols)
        X_obd = features_df[obd_mask].drop(columns=drop_cols)

        # Initialize full prediction and score arrays
        predictions = np.ones(len(features_df)) # 1 is completely normal default
        scores = np.zeros(len(features_df))

        if not X_uds.empty and "UDS" in models:
            preds_uds = models["UDS"].predict(X_uds.values)
            predictions[uds_mask] = preds_uds
            # score_samples returns negative values where lower means more anomalous.
            # Convert to positive anomaly score (higher = more anomalous)
            raw_scores = models["UDS"].score_samples(X_uds.values)
            scores[uds_mask] = -raw_scores

        if not X_obd.empty and "OBD" in models:
            preds_obd = models["OBD"].predict(X_obd.values)
            predictions[obd_mask] = preds_obd
            raw_scores = models["OBD"].score_samples(X_obd.values)
            scores[obd_mask] = -raw_scores

        # Anomalies are marked as -1 by IsolationForest
        is_anomaly = predictions == -1
        anomaly_indices = np.where(is_anomaly)[0]
        print(f"Inference complete. Detected {len(anomaly_indices)} anomalies.")

        report: dict[str, Any] = {
            "metadata": {
                "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
                "total_sequences": len(features_df),
                "total_anomalies": int(is_anomaly.sum()),
                "anomaly_rate": float(is_anomaly.mean())
            },
            "anomalies": []
        }

        # Build detailed anomaly list
        anomaly_indices = is_anomaly.nonzero()[0]
        for idx in anomaly_indices:
            row = features_df.iloc[idx]
            signal_id = str(row["signal_id"])
            anomaly_info = {
                "signal_id": signal_id,
                "anomaly_score": float(scores[idx]),
                "features": {
                    "min": float(row["min"]),
                    "max": float(row["max"]),
                    "value_spread": float(row["value_spread"]),
                    "uds_spread": float(row["uds_spread"]),
                    "error_rate": float(row["error_rate"]),
                    "sequence_length": float(row["sequence_length"]),
                }
            }
            report["anomalies"].append(anomaly_info)

        print(f"Inference complete. Detected {report['metadata']['total_anomalies']} anomalies.")
        print(f"Saving report to MinIO bucket '{self.storage.report_bucket}/{report_name}'...")

        self.storage.save_report(report, report_name)
        print("Report saved successfully.")

        return report
