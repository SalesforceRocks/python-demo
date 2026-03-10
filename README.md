# AI Fairness Checker

A Python CLI tool for analyzing ML model predictions for bias. It computes standard algorithmic fairness metrics (demographic parity, equalized odds, equal opportunity, predictive parity, calibration) across protected groups and reports whether thresholds are met.

This is a demo project for showcasing Claude Code workflows at a responsible AI consultancy.

## Quick Start

```bash
# Install
pip install -e .

# Usage
fairness-checker --help
```

## Development

```bash
# Install dev dependencies
pip install -e .
pip install pytest ruff

# Run tests
pytest tests/ -v

# Lint
ruff check src/
```
