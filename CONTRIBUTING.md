# Contributing

Thanks for considering a contribution.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,plots]"
pytest
ruff check .
```

## Contribution guidelines

- Keep parsing and metric calculations independently testable.
- Include small synthetic NS-2 trace fixtures for parser or metric changes.
- State units in metric names and documentation.
- Do not silently infer RTT, application goodput, or simulator metadata from incomplete traces.
- Keep experimental controller claims aligned with what the C++ implementation actually does.
- For scenario changes, document topology, link rates, delays, queue discipline, queue size, traffic start/stop times, and random seeds.
- Do not commit new large generated trace files unless they are required as reproducible fixtures; prefer compact fixtures under `tests/fixtures/`.

## Pull requests

Describe the motivation, methodology impact, test commands and results, and any NS-2 version-specific requirements. Separate measured results from expected or illustrative behavior.
