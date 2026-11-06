"""Flow-level metrics derived from classic NS-2 event traces."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Iterable

from tcp_congestion_analysis.trace import TraceEvent


@dataclass(frozen=True, slots=True)
class FlowMetrics:
    """Aggregate metrics for one NS-2 flow ID."""

    flow_id: int
    received_packets: int
    received_bytes: int
    dropped_packets: int
    first_receive_time_s: float | None
    last_receive_time_s: float | None
    average_throughput_mbps: float | None
    packet_delivery_ratio: float | None


def jains_fairness_index(values: Iterable[float]) -> float | None:
    """Calculate Jain's fairness index; return None when values are empty/all zero."""
    samples = [max(float(value), 0.0) for value in values]
    denominator = len(samples) * sum(value * value for value in samples)
    if not samples or denominator == 0:
        return None
    return sum(samples) ** 2 / denominator


def summarize_flows(
    events: Iterable[TraceEvent],
    simulation_duration_s: float | None = None,
) -> list[FlowMetrics]:
    """Summarize received TCP payload bytes and drop events for each flow.

    Throughput uses bytes at receive ('r') events. If no explicit simulation
    duration is supplied, the active interval from first to last receive is used.
    This is an average over that interval, not a time-bin throughput curve.
    """
    received: dict[int, list[TraceEvent]] = defaultdict(list)
    dropped: dict[int, int] = defaultdict(int)
    for event in events:
        if event.packet_type.lower() != "tcp":
            continue
        if event.event == "r":
            received[event.flow_id].append(event)
        elif event.event == "d":
            dropped[event.flow_id] += 1

    flow_ids = sorted(set(received) | set(dropped))
    summaries: list[FlowMetrics] = []
    for flow_id in flow_ids:
        packets = received[flow_id]
        first = min((event.time for event in packets), default=None)
        last = max((event.time for event in packets), default=None)
        byte_count = sum(event.packet_size for event in packets)
        duration = simulation_duration_s
        if duration is None and first is not None and last is not None:
            duration = last - first
        throughput = (
            byte_count * 8 / duration / 1_000_000
            if duration is not None and duration > 0
            else None
        )
        rx_count = len(packets)
        drop_count = dropped[flow_id]
        total_observed = rx_count + drop_count
        delivery = rx_count / total_observed if total_observed else None
        summaries.append(
            FlowMetrics(
                flow_id=flow_id,
                received_packets=rx_count,
                received_bytes=byte_count,
                dropped_packets=drop_count,
                first_receive_time_s=first,
                last_receive_time_s=last,
                average_throughput_mbps=throughput,
                packet_delivery_ratio=delivery,
            )
        )
    return summaries


def summarize_to_dict(metrics: list[FlowMetrics]) -> dict[str, object]:
    """Serialize flow metrics and Jain fairness into JSON-compatible values."""
    throughput = [
        item.average_throughput_mbps
        for item in metrics
        if item.average_throughput_mbps is not None
    ]
    return {
        "flows": [asdict(item) for item in metrics],
        "jains_fairness_index": jains_fairness_index(throughput),
        "flow_count": len(metrics),
    }
