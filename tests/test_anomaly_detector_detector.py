from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from anomaly_detector.detector import Detector


@patch("anomaly_detector.detector.StorageClient")
def test_detect_anomalies(mock_client_class: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    # Mock models
    mock_uds_model = MagicMock()
    # Let uds model predict -1 for anomaly, 1 for normal
    mock_uds_model.predict.return_value = np.array([-1])
    mock_uds_model.score_samples.return_value = np.array([-0.8])

    mock_obd_model = MagicMock()
    mock_obd_model.predict.return_value = np.array([1])
    mock_obd_model.score_samples.return_value = np.array([-0.2])

    mock_models = {"UDS": mock_uds_model, "OBD": mock_obd_model}
    mock_client.load_model.return_value = mock_models

    # Run dataset
    df = pd.DataFrame([
        {
            "signal_id": "seq1",
            "timestamp": "2025-01-01T00:00:00Z",
            "value": "100.0",
            "signal_type": "UDS",
            "service_id": "0x22",
        },
        {
            "signal_id": "seq2",
            "timestamp": "2025-01-01T00:00:00Z",
            "value": "200.0",
            "signal_type": "OBD",
            "service_id": "0x0C",
        }
    ])

    detector = Detector(model_name="test_model.pkl")
    report = detector.detect_anomalies(df, "test_report.json")

    mock_client.save_report.assert_called_once()

    assert "metadata" in report
    assert "anomalies" in report

    # Ensure there's 1 anomaly (UDS flagged it)
    assert report["metadata"]["total_anomalies"] == 1
    assert len(report["anomalies"]) == 1
    assert report["anomalies"][0]["signal_id"] == "seq1"
    assert report["anomalies"][0]["anomaly_score"] == 0.8 # Output flipped the sign


def test_detect_anomalies_empty_df() -> None:
    detector = Detector()
    df = pd.DataFrame()
    report = detector.detect_anomalies(df, "empty.json")
    assert "error" in report
