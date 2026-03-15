"""CLI entry point for the Anomaly Detector pipeline.

Executes either the training or detection mode against a given signal parity log.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from anomaly_detector.detector import Detector
from anomaly_detector.evaluator import Evaluator
from anomaly_detector.trainer import Trainer


def _load_log(log_path: str) -> pd.DataFrame:
    path = Path(log_path)
    if not path.exists():
        print(f"Error: Signal log not found at {path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_parquet(path)
        return df
    except Exception as e:
        print(f"Error reading parquet file: {e}", file=sys.stderr)
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Isolation Forest Anomaly Detector Pipeline"
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["train", "detect"],
        required=True,
        help="Pipeline phase to execute.",
    )

    parser.add_argument(
        "--log",
        type=str,
        required=True,
        help="Path to the source Parquet signal log.",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="anomaly_report.json",
        help="Output filename for reports (only applies to 'detect' mode).",
    )

    parser.add_argument(
        "--contamination",
        type=float,
        default=0.1,
        help="Expected fault rate / contamination (only applies to 'train' mode). Default 0.1",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"Loading data from {args.log}...")
    df = _load_log(args.log)

    if args.mode == "train":
        print("Initializing Training Pipeline...")
        # Isolation Forest contamination parameter expects a known fault rate
        trainer = Trainer(contamination=args.contamination)
        trainer.train_and_save(df, model_name="isolation_forest.pkl")
        print("Training pipeline finished.")

    elif args.mode == "detect":
        print("Initializing Inference Pipeline...")
        detector = Detector(model_name="isolation_forest.pkl")

        # Inference
        report = detector.detect_anomalies(df, report_name=args.output)
        if "error" in report:
            print(f"Inference error: {report['error']}", file=sys.stderr)
            sys.exit(1)

        print("Evaluating Metrics...")
        evaluator = Evaluator(df, report)
        metrics = evaluator.evaluate()

        if metrics.get("precision", 0) < 0.75:
            print("WARNING: Precision fell below the 0.75 quality gate threshold.", file=sys.stderr)
            # In CI, we would probably exit 1 here if testing model adequacy.

        print("Inference pipeline finished.")


if __name__ == "__main__":
    main()
