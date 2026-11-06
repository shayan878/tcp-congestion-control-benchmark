# Implementation limitations

## The custom agent is a prototype

The original C++ source defines `Agent/TCP/Reno/BBR` as a subclass of the NS-2 Reno agent. It estimates a bandwidth-like quantity and minimum RTT, maintains simplified STARTUP/DRAIN/PROBE_BW/PROBE_RTT labels, and adjusts a Reno-derived congestion window.

This is not a faithful implementation of the BBR algorithm. In particular:

- The bandwidth estimate is based on differences in cumulative ACK numbers and elapsed time, not BBR's round-based maximum bandwidth filter.
- The source does not implement the complete BBR state machine or its reference-model gain cycling and ProbeRTT behavior.
- A pacing-rate variable is calculated, but it is not connected to an NS-2 packet pacing scheduler. It must not be described as actual packet pacing.
- The prototype inherits Reno retransmission and ACK processing.
- The exact compatibility of the C++ source depends on the NS-2 version and its TCP headers/build system. It has not been compiled or executed in CI.

The maintained source includes a conservative correction to the ACK byte counter and startup plateau detection, but these changes do not turn the prototype into reference BBR.

## Metrics limitations

- Classic NS-2 event traces vary by version and configuration. The parser targets the standard wired trace layout and ignores malformed/unrecognized lines.
- Average throughput is calculated from TCP packet receive events and the supplied simulation duration. For publication-grade goodput, confirm whether packet sizes include headers and use receiver-side application bytes if available.
- Packet-delivery ratio uses observed receive and drop events. It is not a unique-sequence-number delivery ratio and can be affected by retransmissions.
- RTT is not derived from the event trace by guessing. The report indicates whether a recognizable attached `rtt_` tracevar was found.
- Jain's index is calculated over the flow throughput values available in a single analyzed trace. It is a fairness summary, not a complete QoS metric.

## Claims and reporting

Do not label the current results as a benchmark of Google's BBR, production BBR, or a validated BBR-vs-Reno implementation. Use wording such as "Reno vs the repository's experimental BBR-inspired NS-2 agent." Include simulator version, exact commit, all scenario parameters, and seeds with any reported result.
