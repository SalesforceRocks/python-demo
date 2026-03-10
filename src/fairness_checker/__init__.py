"""AI Fairness Checker - Analyze ML model predictions for bias."""

from fairness_checker.metrics import compute_demographic_parity, format_report

__all__ = ["compute_demographic_parity", "format_report"]
