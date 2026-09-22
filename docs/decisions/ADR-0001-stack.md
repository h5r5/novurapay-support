# ADR-0001: Technology Stack and Environment Selection

## Status
Accepted

## Context
The project requires building an automated support pipeline for Iraqi Arabic customer tickets as part of the Agentic AI Challenge Iraq (Topic 06). Key requirements include batch processing reliability, deterministic validation, robust Arabic text handling, rapid iteration, comprehensive unit/integration testing, and seamless execution on Windows.

## Options Considered
1. **Python 3.14 with `uv` package manager (Chosen)**:
   - High performance, modern typing features, rapid virtual environment and lockfile management via `uv`.
   - Verified that modern binary wheels (`pydantic 2.13`, `numpy 2.5`, `pandas 3.0`, `scikit-learn 1.9`, `pytest 9.1`) compile and resolve cleanly in under 1 second.
   - Built-in support for pyproject.toml standards and seamless multi-platform execution (Windows and Linux CI).
2. **Node.js / TypeScript**:
   - Strong typing, but weaker ecosystem for offline evaluation metrics, confusion matrices, and Arabic text normalization packages compared to Python's data stack.
3. **Python 3.11/3.12 with Poetry or Pipenv**:
   - Slower dependency resolution and environment setup compared to `uv`.

## Decision
We adopt:
- **Runtime:** Python 3.14 (managed by `uv`).
- **Data Validation & Schemas:** Pydantic v2 (`pydantic>=2.10`, `pydantic-settings>=2.7`) for strict runtime type validation and schema enforcement.
- **Evaluation & Statistics:** `pandas`, `scikit-learn`, `numpy`, and `matplotlib`.
- **HTTP & Resilience:** `httpx` with explicit timeouts, `tenacity` for backoff retries.
- **Testing & Quality:** `pytest`, `pytest-cov`, `ruff` (linter/formatter), and `mypy` (static type checking).
- **Configuration & Taxonomy:** YAML (`pyyaml`) for category, routing, and prompt templates.

## Consequences
- Windows compatibility is preserved by enforcing `encoding="utf-8"` throughout, using `pathlib.Path`, and avoiding shell-specific invocations.
- Zero reliance on bloated agent frameworks (e.g. LangChain, AutoGen); all pipeline code is clean, auditable Python standard libraries and lightweight packages.
