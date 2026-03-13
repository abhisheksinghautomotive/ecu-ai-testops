"""CLI entry point for the ECU Signal Simulator.

Usage::

    python -m simulator --n-uds 2500 --n-obd 2500 --fault-rate 0.1 \
                        --output ./data/signal_log.parquet
"""

from __future__ import annotations

import argparse
import sys

from simulator.dataset_writer import write_parquet
from simulator.fault_injector import inject_faults
from simulator.obd_simulator import generate_obd_sequences
from simulator.uds_simulator import generate_uds_sequences

DEFAULT_OUTPUT = "./data/signal_log.parquet"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic ECU signal data with fault injection.",
    )
    parser.add_argument(
        "--n-uds",
        type=int,
        default=2500,
        help="Number of UDS 0x22 sequences to generate (default: 2500).",
    )
    parser.add_argument(
        "--n-obd",
        type=int,
        default=2500,
        help="Number of OBD-II PID sequences to generate (default: 2500).",
    )
    parser.add_argument(
        "--fault-rate",
        type=float,
        default=0.1,
        help="Fraction of sequences to inject faults into (default: 0.1).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help=(
            "Output Parquet file path (default: ./data/signal_log.parquet). "
            "This must be a file path, not a directory."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Run the signal simulator pipeline."""
    args = parse_args(argv)

    print(f"Generating {args.n_uds} UDS sequences …")
    uds_sequences = generate_uds_sequences(n=args.n_uds, rng_seed=args.seed)

    print(f"Generating {args.n_obd} OBD-II sequences …")
    obd_sequences = generate_obd_sequences(n=args.n_obd, rng_seed=args.seed)

    all_sequences = uds_sequences + obd_sequences

    print(f"Injecting faults at {args.fault_rate:.0%} rate …")
    all_sequences = inject_faults(
        all_sequences,
        fault_rate=args.fault_rate,
        rng_seed=args.seed,
    )

    n_faults = sum(1 for s in all_sequences if s["fault_label"])
    print(f"Total sequences: {len(all_sequences)} | Faults: {n_faults}")

    output_file = write_parquet(all_sequences, output_path=args.output)
    print(f"Wrote signal log to: {output_file}")


if __name__ == "__main__":
    main(sys.argv[1:])
