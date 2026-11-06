from tcp_congestion_analysis.trace import parse_event_line, parse_variable_line


def test_parse_classic_ns2_tcp_receive_event():
    event = parse_event_line("r 1.25 2 3 tcp 1000 ------- 1 0.0 3.0 42 7")
    assert event is not None
    assert event.event == "r"
    assert event.time == 1.25
    assert event.packet_type == "tcp"
    assert event.packet_size == 1000
    assert event.flow_id == 1
    assert event.sequence == 42


def test_parse_ignores_unrecognized_and_malformed_lines():
    assert parse_event_line("trace file header") is None
    assert parse_event_line("r not-a-time 2 3 tcp 1000 ------- 1 0.0 3.0 42 7") is None


def test_parse_attached_trace_variable():
    variable = parse_variable_line("2.5 0 0 cwnd_ 32")
    assert variable is not None
    assert variable.time == 2.5
    assert variable.agent_id == "0"
    assert variable.name == "cwnd_"
    assert variable.value == 32


def test_non_variable_line_is_not_misclassified():
    assert parse_variable_line("r 1.25 2 3 tcp 1000 ------- 1 0.0 3.0 42 7") is None
