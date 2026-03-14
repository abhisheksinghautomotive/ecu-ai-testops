import pandas as pd

from anomaly_detector.feature_extractor import extract_features


def test_extract_features_numeric_obd() -> None:
    df = pd.DataFrame([
        {
            "signal_id": "seq1",
            "timestamp": "2025-01-01T00:00:00Z",
            "value": "100.0",
            "signal_type": "OBD",
            "service_id": "0x0C",
            "fault_label": False
        },
        {
            "signal_id": "seq1",
            "timestamp": "2025-01-01T00:00:01Z",
            "value": "110.0",
            "signal_type": "OBD",
            "service_id": "0x0C",
            "fault_label": False
        }
    ])

    features = extract_features(df)
    assert len(features) == 1
    seq = features.iloc[0]

    assert seq["min"] == 100.0
    assert seq["max"] == 110.0
    assert seq["value_spread"] == 10.0
    assert seq["is_obd"] == 1.0
    assert seq["is_uds"] == 0.0
    assert seq["uds_spread"] == 0.0
    assert seq["error_rate"] == 0.0
    assert seq["sequence_length"] == 2


def test_extract_features_uds_hex() -> None:
    df = pd.DataFrame([
        {
            "signal_id": "seq2",
            "timestamp": "2025-01-01T00:00:00Z",
            "value": "62F1A01A2B", # valid pos response
            "signal_type": "UDS",
            "service_id": "0x22",
            "fault_label": False
        },
        {
            "signal_id": "seq2",
            "timestamp": "2025-01-01T00:00:01Z",
            "value": "62F1A01A2C",
            "signal_type": "UDS",
            "service_id": "0x22",
            "fault_label": False
        }
    ])

    features = extract_features(df)
    assert len(features) == 1
    seq = features.iloc[0]

    val1 = int("62", 16) # 98
    val2 = int("62", 16) # 98

    assert seq["min"] == val1
    assert seq["max"] == val2
    assert seq["value_spread"] == 0.0
    assert seq["uds_spread"] == 0.0
    assert seq["is_obd"] == 0.0
    assert seq["is_uds"] == 1.0


def test_extract_features_timeout_and_nrc() -> None:
    df = pd.DataFrame([
        {
            "signal_id": "seq3",
            "timestamp": "2025-01-01T00:00:00Z",
            "value": "TIMEOUT",
            "signal_type": "UDS",
            "service_id": "0x22",
            "fault_label": True
        },
        {
            "signal_id": "seq3",
            "timestamp": "2025-01-01T00:00:01Z",
            "value": "7F2231", # NRC
            "signal_type": "UDS",
            "service_id": "0x22",
            "fault_label": True
        }
    ])

    features = extract_features(df)
    assert len(features) == 1
    seq = features.iloc[0]

    # First row is TIMEOUT -> NaN. Second row is 7F2231 -> '7F' -> 127.0
    # So min and max are both 127.0
    assert seq["min"] == 127.0
    assert seq["max"] == 127.0
    # 1 out of 2 is an error (TIMEOUT)
    assert seq["error_rate"] == 0.5
    assert seq["sequence_length"] == 2
