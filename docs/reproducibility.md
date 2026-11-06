# Reproducibility and NS-2 integration

## Python environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,plots]"
pytest
```

## NS-2

Install NS-2 separately using the distribution and build instructions appropriate to your operating system. Check that `ns` is on PATH:

```bash
./scripts/check-ns2.sh
```

The Reno Tcl scenario can be run directly with a standard compatible NS-2 build:

```bash
ns simulator/ns2/scenarios/reno.tcl results/reno 4
```

## Custom C++ agent

The BBR-inspired scenario instantiates the Tcl class `Agent/TCP/Reno/BBR`. That class must be compiled into the NS-2 source tree and linked into the `ns` executable. The C++ file is provided at `simulator/ns2/agent/tcp-bbr.cc`.

NS-2 forks differ in their TCP class declarations, source file lists, and build configuration. Integrate the file using the build conventions of your exact NS-2 version; verify the required Reno header and method signatures before compiling. This repository intentionally does not claim that copying the file into an arbitrary NS-2 installation is sufficient.

After the class is registered, run:

```bash
ns simulator/ns2/scenarios/bbr-inspired.tcl results/bbr-inspired 4
```

## Run paired experiments

```bash
PYTHONPATH=src python -m tcp_congestion_analysis.runner --ns ns --seed 4 --output-dir results
```

This executes the Reno scenario and then the BBR-inspired scenario using the same seed argument. To aggregate multiple seeds, call the runner once per seed into a distinct output directory, then analyze each generated trace. Preserve all seed values and simulator build details alongside the results.

## Analyze generated traces

```bash
tcp-trace-analyze \
  --reno-trace results/reno/reno.tr \
  --bbr-trace results/bbr-inspired/bbr-inspired.tr \
  --duration 1000 \
  --output-dir results/analysis \
  --plot
```

## What CI does not do

Hosted CI validates Python linting, package installation, and unit tests. It does not install NS-2, compile the custom C++ agent, run the Tcl scenarios, or verify network simulation outputs. Those remain environment-specific integration steps.
