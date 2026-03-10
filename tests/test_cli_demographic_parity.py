"""CLI integration tests for the demographic-parity command (Issue #3).

Tests use Click's CliRunner for isolated testing without subprocess calls.
All tests are organized by acceptance criterion.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from fairness_checker.cli import cli
from fairness_checker.models import Dataset

# ---------------------------------------------------------------------------
# Fixture: tmp_csv_file factory
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_csv_file(tmp_path: Path):
    """Factory fixture: takes a Dataset, writes it to a temp CSV, returns Path.

    Usage:
        csv_path = tmp_csv_file(my_dataset)
    """

    def _factory(dataset: Dataset) -> Path:
        df = dataset.to_dataframe()
        path = tmp_path / "data.csv"
        df.to_csv(path, index=False)
        return path

    return _factory


# ---------------------------------------------------------------------------
# AC9: CLI integration — exit codes and output format
# ---------------------------------------------------------------------------


def test_cli_pass_exit_code_ac9(tmp_csv_file) -> None:
    """AC9: CLI exits with code 0 when overall_pass is True."""
    # 'a'=0.8, 'b'=1.0 => ratio=0.8 >= 0.8 => pass
    dataset = Dataset(
        predictions=[1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        actuals=[0] * 10,
        group_labels=["a", "a", "a", "a", "a", "b", "b", "b", "b", "b"],
    )
    csv_path = tmp_csv_file(dataset)
    runner = CliRunner()
    result = runner.invoke(cli, ["demographic-parity", "--file", str(csv_path)])
    assert result.exit_code == 0, (
        f"Expected exit 0, got {result.exit_code}.\nOutput:\n{result.output}"
    )


def test_cli_fail_exit_code_ac9(tmp_csv_file) -> None:
    """AC9: CLI exits with code 1 when overall_pass is False."""
    # 'a'=0.6, 'b'=1.0 => ratio=0.6 < 0.8 => fail
    dataset = Dataset(
        predictions=[1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        actuals=[0] * 10,
        group_labels=["a", "a", "a", "a", "a", "b", "b", "b", "b", "b"],
    )
    csv_path = tmp_csv_file(dataset)
    runner = CliRunner()
    result = runner.invoke(cli, ["demographic-parity", "--file", str(csv_path)])
    assert result.exit_code == 1, (
        f"Expected exit 1, got {result.exit_code}.\nOutput:\n{result.output}"
    )


def test_cli_output_format_ac9(tmp_csv_file) -> None:
    """AC9: CLI prints a human-readable report to stdout."""
    dataset = Dataset(
        predictions=[1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        actuals=[0] * 10,
        group_labels=["a", "a", "a", "a", "a", "b", "b", "b", "b", "b"],
    )
    csv_path = tmp_csv_file(dataset)
    runner = CliRunner()
    result = runner.invoke(cli, ["demographic-parity", "--file", str(csv_path)])
    assert "Demographic Parity Analysis" in result.output
    assert "Threshold:" in result.output
    assert "Group Results" in result.output
    assert "Result:" in result.output


# ---------------------------------------------------------------------------
# AC10: CLI error reporting — file not found
# ---------------------------------------------------------------------------


def test_cli_file_not_found_ac10() -> None:
    """AC10: CLI with nonexistent file produces error message and non-zero exit code."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["demographic-parity", "--file", "/nonexistent/path/data.csv"]
    )
    assert result.exit_code != 0
    assert "does not exist" in result.output or "Error" in result.output
