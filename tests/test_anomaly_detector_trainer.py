from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from anomaly_detector.trainer import Trainer


@patch("anomaly_detector.trainer.StorageClient")
def test_trainer_train_and_save(mock_client_class: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    trainer = Trainer(contamination=0.1)

    df = pd.DataFrame([
        {
            "signal_id": "seq1",
            "timestamp": "2025-01-01T00:00:00Z",
            "value": "100.0",
            "signal_type": "UDS",
            "service_id": "0x22",
            "fault_label": False
        },
         {
            "signal_id": "seq2",
            "timestamp": "2025-01-01T00:00:02Z",
            "value": "200.0",
            "signal_type": "OBD",
            "service_id": "0x0C",
            "fault_label": False
        }
    ])

    trainer.train_and_save(df, "test_model.pkl")

    # Verify save_model called once with dict of models
    mock_client.save_model.assert_called_once()
    args, kwargs = mock_client.save_model.call_args
    models_dict = args[0]

    assert "UDS" in models_dict
    assert "OBD" in models_dict


def test_trainer_empty_df() -> None:
    trainer = Trainer()
    with pytest.raises(ValueError, match="No features could be extracted"):
        trainer.train_and_save(pd.DataFrame(), "test.pkl")
