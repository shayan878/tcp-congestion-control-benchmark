"""Command-line interface for NS-2 trace analysis."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from tcp_congestion_analysis.compare import analyze_trace
from tcp_congestion_analysis.plotting import plot_flow_throughput


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tcp-trace-analyze",
        description="Analyze NS-2 traces from TCP Reno and the experimental BBR-inspired agent.",
    )
    parser.add_argument("--reno-trace", type=Path, required=True)
    parser.add_argument("--bbr-trace", type=Path, required=True)
    parser.add_argument("--duration", type=float, help="Known simulation duration in seconds")
    parser.add_argument("--output-dir", type=Path, default=Path("results/analysis"))
    parser.add_argument("--plot", action="store_true", help="Create a throughput chart (requires matplotlib)")
    return parser


def _write_flow_csv(path: Path, summaries: dict[str, dict[str, Any]]) -> None:
    fields = [
        "algorithm", "flow_id", "received_packets", "received_bytes", "dropped_packets",
        "first_receive_time_s", "last_receive_time_s", "average_throughput_mbps",
        "packet_delivery_ratio",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for algorithm, summary in summaries.items():
            for flow in summary["flows"]:
                writer.writerow({"algorithm": algorithm, **flow})


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for path in (args.reno_trace, args.bbr_trace):
        if not path.is_file():
            raise SystemExit(f"Trace file does not exist: {path}")
    if args.duration is not None and args.duration <= 0:
        raise SystemExit("--duration must be positive")

    summaries = {
        "Reno": analyze_trace(args.reno_trace, args.duration),
        "BBR-inspired": analyze_trace(args.bbr_trace, args.duration),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summaries, indent=2) + "\n", encoding="utf-8"
    )
    _write_flow_csv(args.output_dir / "flow_metrics.csv", summaries)
    if args.plot:
        plot_flow_throughput(summaries, args.output_dir / "throughput.png")
    print(f"Analysis written to {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
