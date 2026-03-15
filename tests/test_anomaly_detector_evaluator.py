import pandas as pd
from pytest import CaptureFixture

from anomaly_detector.evaluator import Evaluator


def test_evaluate_predictions(capsys: CaptureFixture) -> None:
    # Setup dummy data with 1 anomaly and 1 normal
    log_df = pd.DataFrame([
        {
            "signal_id": "seq1",
            "fault_label": False,
        },
        {
            "signal_id": "seq2",
            "fault_label": True,
        },
        {
            "signal_id": "seq3",
            "fault_label": False,
        }
    ])

    report = {
        "anomalies": [
            {"signal_id": "seq2"},
            {"signal_id": "seq3"}
        ]
    }

    evaluator = Evaluator(log_df, report)
    metrics = evaluator.evaluate()

    # Truth: 1 Pos (seq2), 2 Neg (seq1, seq3)
    # Preds: 2 Pos (seq2, seq3), 1 Neg (seq1)
    # TP: 1 (seq2)
    # FP: 1 (seq3)
    # FN: 0
    # Precision: 1 / (1 + 1) = 0.5
    # Recall: 1 / (1 + 0) = 1.0
    # F1: 2 * (0.5 * 1.0) / (0.5 + 1.0) = 1.0 / 1.5 = 0.666...

    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 1.0
    assert abs(metrics["f1"] - 0.6666) < 0.001

    # Check output prints
    captured = capsys.readouterr()
    assert "Precision: 0.5000" in captured.out


def test_evaluate_predictions_perfect(capsys: CaptureFixture) -> None:
    log_df = pd.DataFrame([
        {"signal_id": "seq1", "fault_label": False},
        {"signal_id": "seq2", "fault_label": True}
    ])

    report = {
        "anomalies": [
            {"signal_id": "seq2"}
        ]
    }

    evaluator = Evaluator(log_df, report)
    metrics = evaluator.evaluate()

    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0

    captured = capsys.readouterr()
    assert "Precision: 1.0000" in captured.out
    assert "WARNING:" not in captured.out
