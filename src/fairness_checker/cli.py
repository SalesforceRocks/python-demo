"""CLI interface for AI Fairness Checker."""

import click


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Analyze ML model predictions for bias."""


if __name__ == "__main__":
    cli()
