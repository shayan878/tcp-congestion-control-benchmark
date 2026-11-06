"""Parsers for classic NS-2 event traces and tracevar output."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

_EVENT_TYPES = {"+", "-", "r", "d", "h"}


@dataclass(frozen=True, slots=True)
class TraceEvent:
    """One classic NS-2 wired trace event."""

    event: str
    time: float
    source: str
    destination: str
    packet_type: str
    packet_size: int
    flags: str
    flow_id: int
    source_address: str
    destination_address: str
    sequence: int
    packet_id: int


@dataclass(frozen=True, slots=True)
class TraceVariable:
    """One line emitted by an NS-2 agent tracevar attachment."""

    time: float
    agent_id: str
    name: str
    value: float


def parse_event_line(line: str) -> TraceEvent | None:
    """Parse one classic NS-2 event line; return None for unrelated records."""
    fields = line.split()
    if len(fields) < 12 or fields[0] not in _EVENT_TYPES:
        return None
    try:
        return TraceEvent(
            event=fields[0],
            time=float(fields[1]),
            source=fields[2],
            destination=fields[3],
            packet_type=fields[4],
            packet_size=int(float(fields[5])),
            flags=fields[6],
            flow_id=int(fields[7]),
            source_address=fields[8],
            destination_address=fields[9],
            sequence=int(float(fields[10])),
            packet_id=int(fields[11]),
        )
    except (ValueError, IndexError):
        return None


def parse_variable_line(line: str, variable_names: set[str] | None = None) -> TraceVariable | None:
    """Parse an attached tracevar line when its variable name is present.

    NS-2 tracevar formatting depends on the traced object/version. This parser
    intentionally requires a recognizable variable token and numeric time/value.
    """
    names = variable_names or {"cwnd_", "ssthresh_", "ack_", "maxseq_", "rtt_"}
    fields = line.split()
    name = next((field for field in fields if field in names), None)
    if name is None or len(fields) < 3:
        return None
    try:
        time = float(fields[0])
        value = float(fields[-1])
    except ValueError:
        return None
    return TraceVariable(time=time, agent_id=fields[1], name=name, value=value)


def iter_events(path: str | Path) -> Iterator[TraceEvent]:
    """Yield valid classic NS-2 event records from a trace file."""
    with Path(path).open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            event = parse_event_line(line)
            if event is not None:
                yield event


def iter_variables(path: str | Path) -> Iterator[TraceVariable]:
    """Yield recognized tracevar records from a trace file."""
    with Path(path).open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            variable = parse_variable_line(line)
            if variable is not None:
                yield variable


def event_list(lines: Iterable[str]) -> list[TraceEvent]:
    """Convenience parser for in-memory trace fixtures."""
    return [event for line in lines if (event := parse_event_line(line)) is not None]
