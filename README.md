# TCP Congestion Control: Reno vs BBR-inspired

[![CI](https://github.com/shayan878/TCP-Congestion-Control-BBR-vs-Reno-NS2-/actions/workflows/ci.yml/badge.svg)](https://github.com/shayan878/TCP-Congestion-Control-BBR-vs-Reno-NS2-/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A reproducible NS-2 study scaffold for examining TCP Reno and an **experimental BBR-inspired agent**, with a tested Python toolkit for parsing simulator traces and calculating flow-level metrics.

> **Research scope:** the custom C++ agent in this repository is a simplified BBR-inspired prototype. It is not Google's reference BBR implementation and does not currently implement actual packet pacing. Results must be described as Reno vs this repository's BBR-inspired prototype, not as a general benchmark of production BBR.

## What is included

- NS-2 Tcl scenarios for two Reno flows sharing a bottleneck and two instances of the custom BBR-inspired agent sharing the same topology.
- C++ source for the experimental NS-2 agent.
- A modular Python package for trace parsing, per-flow throughput and delivery metrics, Jain's fairness index, JSON/CSV export, and optional charts.
- A runner that launches both scenarios with the same seed.
- Unit tests and CI for the Python analysis package.
- Historical trace files retained under `OTCL code and files/` for reference.

## Repository layout

```text
.
├── .github/workflows/ci.yml
├── docs/
│   ├── experiment-design.md
│   ├── implementation-limitations.md
│   └── reproducibility.md
├── simulator/ns2/
│   ├── agent/tcp-bbr.cc
│   └── scenarios/
│       ├── bbr-inspired.tcl
│       └── reno.tcl
├── src/tcp_congestion_analysis/
│   ├── cli.py
│   ├── compare.py
│   ├── metrics.py
│   ├── plotting.py
│   ├── runner.py
│   └── trace.py
├── tests/
├── scripts/check-ns2.sh
├── OTCL code and files/       # historical raw traces
└── pyproject.toml
```

## Quick start: Python analysis

Requires Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,plots]"
pytest
```

Analyze existing trace files:

```bash
tcp-trace-analyze \
  --reno-trace "OTCL code and files/projectTrace_reno.tr" \
  --bbr-trace "OTCL code and files/project_trace_BBR.tr" \
  --output-dir results/analysis
```

Add `--plot` to create a throughput comparison chart. The command writes:
- `summary.json`: per-algorithm flow metrics and trace metadata.
- `flow_metrics.csv`: one row per observed flow.
- `throughput.png`: optional chart, when `--plot` is selected.

The original raw traces are large and retained as historical artifacts; the default analysis uses them directly without copying them into the package.

## Run new NS-2 experiments

NS-2 is an external dependency and is not installed by the Python package. Install a compatible NS-2 build first. The Reno scenario runs with a standard NS-2 build:

```bash
ns simulator/ns2/scenarios/reno.tcl results/reno 4
```

The BBR-inspired scenario requires the custom C++ agent to be compiled into your NS-2 build and registered as `Agent/TCP/Reno/BBR`. See [NS-2 integration notes](docs/reproducibility.md). Once integrated, run:

```bash
ns simulator/ns2/scenarios/bbr-inspired.tcl results/bbr-inspired 4
```

Or run both scenarios with a matched seed:

```bash
PYTHONPATH=src python -m tcp_congestion_analysis.runner --seed 4 --output-dir results
```

The runner stops and reports an error if either simulator process fails. It does not silently treat missing or failed runs as valid experiments.

## Metrics and interpretation

| Metric | Definition used here | Interpretation |
|---|---|---|
| Received bytes | Sum of TCP packet sizes at receive events | Delivered traffic volume |
| Average throughput | Received bits divided by the supplied simulation duration | Flow goodput estimate over the chosen interval |
| Drop count | Number of TCP drop events per flow | Observed packet drops |
| Packet delivery ratio | Receives / (receives + observed drops) | Trace-event ratio, not a retransmission-aware delivery guarantee |
| Jain's fairness | ((\sum x_i)^2 / (n\sum x_i^2)) over available flow throughput values | Equality of measured flow rates |

Pass `--duration` when you need a fixed, common measurement interval, for example `--duration 1000`. Without it, throughput uses the first-to-last receive interval for each flow. The parser does not infer one-way delay or RTT from arbitrary trace records; RTT/cwnd are included only when recognizable tracevar records are present.

## Important interpretation notes

- The two supplied scenarios are separate homogeneous runs. They compare Reno-vs-Reno and prototype-vs-prototype, not Reno and BBR competing simultaneously in the same bottleneck.
- Use identical topology, offered load, queue configuration, duration, and matched random seeds when making comparisons.
- The old trace files are retained as legacy data and may have been generated with different script versions or random seeds. Their exact provenance is not independently verified here.
- A passing Python CI run validates the parser and metric calculations on synthetic fixtures. It does **not** validate an NS-2 build, compile the C++ agent, or establish any network-performance result.

## Documentation

- [Experiment design and methodology](docs/experiment-design.md)
- [Implementation limitations](docs/implementation-limitations.md)
- [Reproducibility and NS-2 setup](docs/reproducibility.md)

## Citation

If you use this repository, cite the repository URL and include the exact commit hash, simulator version, scenario parameters, and random seeds used for your experiment. Do not cite the prototype as an implementation of the full BBR algorithm.

## Contributing

Bug reports, reproducible test cases, methodology improvements, and carefully documented extensions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
