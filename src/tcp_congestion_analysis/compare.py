"""Comparison helpers for separate Reno and BBR experiment traces."""

from __future__ import annotations

from pathlib import Path

from tcp_congestion_analysis.metrics import summarize_flows, summarize_to_dict
from tcp_congestion_analysis.trace import iter_events, iter_variables


def analyze_trace(path: str | Path, simulation_duration_s: float | None = None) -> dict[str, object]:
    """Analyze one NS-2 trace, including optional attached congestion-window/RTT series."""
    events = list(iter_events(path))
    metrics = summarize_flows(events, simulation_duration_s=simulation_duration_s)
    variables = list(iter_variables(path))
    variable_summary: dict[str, list[dict[str, float | str]]] = {}
    for variable in variables:
        variable_summary.setdefault(variable.name, []).append(
            {"time_s": variable.time, "agent_id": variable.agent_id, "value": variable.value}
        )
    return {
        "trace_file": Path(path).name,
        "event_count": len(events),
        "event_types": {
            event: sum(item.event == event for item in events)
            for event in ("+", "-", "r", "d", "h")
        },
        **summarize_to_dict(metrics),
        "trace_variables": variable_summary,
        "rtt_trace_available": bool(variable_summary.get("rtt_")),
        "cwnd_trace_available": bool(variable_summary.get("cwnd_")),
    }
