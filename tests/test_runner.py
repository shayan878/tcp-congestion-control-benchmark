import pytest

from tcp_congestion_analysis.runner import run_scenarios


def test_runner_fails_when_scenario_does_not_exist(tmp_path):
    with pytest.raises(FileNotFoundError, match="scenario not found"):
        run_scenarios(repository_root=tmp_path)


def test_runner_builds_expected_scenario_paths(tmp_path, monkeypatch):
    scenarios = tmp_path / "simulator/ns2/scenarios"
    scenarios.mkdir(parents=True)
    (scenarios / "reno.tcl").write_text("# fixture", encoding="utf-8")
    (scenarios / "bbr-inspired.tcl").write_text("# fixture", encoding="utf-8")

    calls = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Result()

    monkeypatch.setattr("tcp_congestion_analysis.runner.subprocess.run", fake_run)
    result = run_scenarios(
        ns_executable="ns-test",
        seed=19,
        output_dir=tmp_path / "out",
        repository_root=tmp_path,
    )
    assert len(calls) == 2
    assert calls[0][0][0] == "ns-test"
    assert calls[0][0][-1] == "19"
    assert result["reno"][0].endswith("reno/reno.tr")
    assert result["bbr-inspired"][0].endswith("bbr-inspired/bbr-inspired.tr")
