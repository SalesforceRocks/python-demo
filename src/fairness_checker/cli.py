"""CLI interface for AI Fairness Checker."""

import sys

import click

from fairness_checker.metrics import compute_demographic_parity, format_report
from fairness_checker.models import Dataset


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Analyze ML model predictions for bias."""


@cli.command()
@click.option(
    "--file",
    required=True,
    type=click.Path(exists=True),
    help="Path to the CSV file containing predictions, actuals, and group labels.",
)
@click.option(
    "--threshold",
    default=0.8,
    show_default=True,
    type=float,
    help="Minimum acceptable ratio of min_rate/max_rate. Must be in [0.0, 1.0].",
)
def demographic_parity(file: str, threshold: float) -> None:
    """Compute demographic parity across protected groups in a prediction dataset.

    Loads a CSV file, computes the demographic parity ratio (min_rate / max_rate),
    prints a formatted report to stdout, and exits with code 0 (PASS) or 1 (FAIL).
    """
    dataset = Dataset.from_csv(file)
    report = compute_demographic_parity(dataset, threshold=threshold)
    click.echo(format_report(report))
    if not report.overall_pass:
        sys.exit(1)


if __name__ == "__main__":
    cli()
