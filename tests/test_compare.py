from tcp_congestion_analysis.compare import analyze_trace


def test_analyze_trace_reports_event_and_variable_metadata(tmp_path):
    path = tmp_path / "sample.tr"
    path.write_text(
        "r 1.0 2 3 tcp 1000 ------- 1 0.0 3.0 1 1\n"
        "r 2.0 2 3 tcp 1000 ------- 1 0.0 3.0 2 2\n"
        "2.0 0 0 cwnd_ 24\n",
        encoding="utf-8",
    )
    result = analyze_trace(path, simulation_duration_s=5.0)
    assert result["event_count"] == 2
    assert result["event_types"]["r"] == 2
    assert result["flows"][0]["average_throughput_mbps"] == 0.0032
    assert result["cwnd_trace_available"] is True
    assert result["rtt_trace_available"] is False
