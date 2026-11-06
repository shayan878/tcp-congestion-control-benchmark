"""Optional visualization helpers for parsed NS-2 traces."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def plot_flow_throughput(
    summaries: dict[str, dict[str, Any]],
    output_path: str | Path,
) -> None:
    """Create a flow-level average-throughput comparison chart."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Install plotting dependencies with: pip install -e '.[plots]'") from exc

    labels: list[str] = []
    values: list[float] = []
    for algorithm, summary in summaries.items():
        for flow in summary["flows"]:
            throughput = flow["average_throughput_mbps"]
            if throughput is not None:
                labels.append(f"{algorithm} / flow {flow['flow_id']}")
                values.append(float(throughput))

    if not values:
        raise ValueError("No throughput values found; check that the trace has TCP receive events")

    figure, axis = plt.subplots(figsize=(9, 5))
    axis.bar(labels, values)
    axis.set_ylabel("Average throughput (Mbit/s)")
    axis.set_title("TCP flow throughput from NS-2 traces")
    axis.tick_params(axis="x", labelrotation=20)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
