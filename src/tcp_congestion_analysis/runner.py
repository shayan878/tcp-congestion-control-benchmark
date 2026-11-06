"""Run the repository's paired NS-2 scenarios with a matched random seed."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run_scenarios(
    ns_executable: str = "ns",
    seed: int = 4,
    output_dir: str | Path = "results",
    repository_root: str | Path | None = None,
) -> dict[str, list[str]]:
    """Run Reno and BBR-inspired scenarios; fail immediately if NS-2 exits non-zero."""
    root = Path(repository_root) if repository_root else Path(__file__).resolve().parents[2]
    output = Path(output_dir).resolve()
    scenarios = {
        "reno": root / "simulator/ns2/scenarios/reno.tcl",
        "bbr-inspired": root / "simulator/ns2/scenarios/bbr-inspired.tcl",
    }
    generated: dict[str, list[str]] = {}
    for name, scenario in scenarios.items():
        if not scenario.is_file():
            raise FileNotFoundError(f"NS-2 scenario not found: {scenario}")
        destination = output / name
        destination.mkdir(parents=True, exist_ok=True)
        command = [ns_executable, str(scenario), str(destination), str(seed)]
        completed = subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"Scenario '{name}' failed with exit code {completed.returncode}. "
                f"stdout: {completed.stdout[-2000:]} stderr: {completed.stderr[-2000:]}"
            )
        generated[name] = [
            str(destination / ("reno.tr" if name == "reno" else "bbr-inspired.tr")),
            str(destination / ("reno.nam" if name == "reno" else "bbr-inspired.nam")),
        ]
    return generated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ns", default="ns", help="NS-2 executable")
    parser.add_argument("--seed", type=int, default=4)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args(argv)
    outputs = run_scenarios(args.ns, args.seed, args.output_dir)
    for scenario, paths in outputs.items():
        print(f"{scenario}:")
        for path in paths:
            print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
