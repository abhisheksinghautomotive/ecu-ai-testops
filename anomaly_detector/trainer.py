"""Isolation forest training module.

Trains the model on normal signal sequence features and serializes
it to MinIO.
"""


import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from anomaly_detector.feature_extractor import extract_features
from anomaly_detector.storage_client import StorageClient


class Trainer:
    """Trains an Isolation Forest model for anomaly detection."""

    def __init__(self, contamination: float = 0.1, random_state: int = 42) -> None:
        """Initialize the trainer.

        Args:
            contamination: The proportion of outliers in the data set. Used when fitting
                to define the threshold on the scores of the samples.
            random_state: Seed usage by the random number generator.
        """
        self.contamination = contamination
        self.random_state = random_state
        self.storage = StorageClient()

    def _build_pipeline(self) -> Pipeline:
        return Pipeline([
            ("scaler", StandardScaler()),
            ("iso_forest", IsolationForest(
                contamination=self.contamination,
                n_estimators=100,
                max_samples="auto",
                random_state=self.random_state,
                n_jobs=-1
            ))
        ])

    def train_and_save(
        self, df: pd.DataFrame, model_name: str = "isolation_forest.pkl"
    ) -> None:
        """Extract features, train the model, and serialize it to MinIO.

        Args:
            df: The raw signal log DataFrame from Parquet.
            model_name: The object name to save the model as in the MinIO bucket.
        """
        features_df = extract_features(df)
        if features_df.empty:
            raise ValueError("No features could be extracted from the dataframe.")

        # In unsupervised ML, train on "normal" data or data with known contamination.
        # Isolation Forest is robust and handles the expected `contamination` rate well.
        # We drop non-feature columns
        drop_cols = ["signal_id"]
        # Train on the entire dataset (normal + anomaly)
        # so that the 0.1 contamination prior matches reality
        if "fault_label" in features_df.columns:
            drop_cols.append("fault_label")
        train_df = features_df.copy()

        # Separate data by protocol
        uds_mask = train_df["is_uds"] == 1.0
        obd_mask = train_df["is_obd"] == 1.0

        # We don't need the protocol flags anymore
        drop_cols.extend(["is_uds", "is_obd"])

        X_uds = train_df[uds_mask].drop(columns=drop_cols)
        X_obd = train_df[obd_mask].drop(columns=drop_cols)

        models = {}

        # Fit UDS model
        if not X_uds.empty:
            print(f"Training UDS Isolation Forest on {len(X_uds)} samples...")
            model_uds = self._build_pipeline()
            model_uds.fit(X_uds.values)
            models["UDS"] = model_uds

        # Fit OBD model
        if not X_obd.empty:
            print(f"Training OBD Isolation Forest on {len(X_obd)} samples...")
            model_obd = self._build_pipeline()
            model_obd.fit(X_obd.values)
            models["OBD"] = model_obd

        # Save to MinIO
        bucket = self.storage.model_bucket
        print(f"Saving combined model artifacts to MinIO bucket '{bucket}/{model_name}'...")
        self.storage.save_model(models, model_name)
        print("Model saved successfully.")
