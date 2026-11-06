from tcp_congestion_analysis.metrics import jains_fairness_index, summarize_flows
from tcp_congestion_analysis.trace import event_list


def test_flow_metrics_use_receive_events_and_drop_events():
    events = event_list([
        "r 1.0 2 3 tcp 1000 ------- 1 0.0 3.0 1 1",
        "r 2.0 2 3 tcp 1000 ------- 1 0.0 3.0 2 2",
        "d 2.5 2 3 tcp 1000 ------- 1 0.0 3.0 3 3",
        "r 1.0 4 5 tcp 500 ------- 2 1.0 5.0 1 4",
    ])
    metrics = summarize_flows(events, simulation_duration_s=10.0)
    first, second = metrics
    assert first.flow_id == 1
    assert first.received_packets == 2
    assert first.received_bytes == 2000
    assert first.dropped_packets == 1
    assert first.average_throughput_mbps == 0.0016
    assert first.packet_delivery_ratio == 2 / 3
    assert second.flow_id == 2
    assert second.average_throughput_mbps == 0.0004


def test_jains_fairness_index():
    assert jains_fairness_index([10, 10]) == 1.0
    assert jains_fairness_index([10, 0]) == 0.5
    assert jains_fairness_index([0, 0]) is None
    assert jains_fairness_index([]) is None


def test_empty_flow_list_is_valid():
    assert summarize_flows([]) == []
