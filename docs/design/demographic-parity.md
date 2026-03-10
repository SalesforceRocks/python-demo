# Design: Demographic Parity Metric (Issue #3)

## Overview

Add a `compute_demographic_parity` function and CLI command to calculate demographic parity (statistical parity) across protected groups in binary classification predictions.

**Demographic parity** measures whether the proportion of positive predictions is equal across protected groups. It is defined as:

- P(Y_hat=1 | A=a) = P(Y_hat=1 | A=b) for all groups a, b
- Ratio version: min_rate / max_rate >= threshold (default 0.8, the "four-fifths rule")
- Only considers predictions, not actual outcomes.

## Approach

### New Module: `src/fairness_checker/metrics.py` (single file, not a subpackage)

This is a single file module, **not** a `metrics/` subpackage. If additional metrics are added later, it can be refactored into a subpackage at that time.

A single public function `compute_demographic_parity` that:

1. Accepts a `Dataset` and an optional `threshold` (default 0.8).
2. Validates threshold is in [0.0, 1.0]; raises `ValueError` if not.
3. Converts the Dataset to a DataFrame.
4. Groups by the `group` column, computes positive prediction rate per group.
5. (AC7 guard) Filters out groups with zero samples. **Note:** this guard is structurally unreachable — the `Dataset` validator ensures every `group_labels` entry is a non-empty list element, so every group label present in the data has at least one sample, and `pandas.groupby` never produces a group with zero rows. The guard is retained as defensive code but is dead by construction. See "AC7 Structural Guarantee" below for details.
6. If only one group remains, returns `overall_pass=True` (AC8).
7. Computes ratio = min_rate / max_rate, handling the case where max_rate is 0 (all groups have zero positive predictions -- ratio is 1.0 since all are equal, pass is True).
8. If max_rate > 0 and min_rate is 0, ratio is 0.0, pass is False (AC5).
9. Returns a `FairnessReport` with metric_name="demographic_parity", including the computed `ratio` value.

### CLI Command: `demographic-parity`

Registered under the existing `cli` click group in `src/fairness_checker/cli.py`:

```
fairness-checker demographic-parity --file data.csv [--threshold 0.8]
```

- `--file`: Required. `click.Path(exists=True)` -- click validates file existence automatically, producing a user-friendly error message and non-zero exit code for missing files. This satisfies AC10 without custom error handling.
- `--threshold`: Optional, default 0.8.
- Loads CSV via `Dataset.from_csv()`, calls `compute_demographic_parity()`, formats and prints the report.
- Exit code 0 when `overall_pass` is True, exit code 1 when False. Uses `sys.exit(1)` for failure (explicit import of `sys` required). For pass, the function returns normally (implicit exit code 0). `sys.exit()` is chosen over `ctx.exit()` because it is simpler and the CLI does not use Click context features.

### Report Formatting: `format_report` function

A public function in `metrics.py` (or a dedicated `report.py` -- keeping in `metrics.py` for simplicity since it is small) that takes a `FairnessReport` and returns a human-readable string.

The result line uses `report.ratio` directly (no recomputation). The comparison is `ratio >= threshold` (i.e., meeting the threshold exactly is a PASS).

FAIL format (ratio < threshold):
```
Demographic Parity Analysis
============================
Threshold: 0.80

Group Results (sorted):
  group_a: 0.7500 (n=100)
  group_b: 0.5000 (n=80)

Result: FAIL (ratio: 0.80 required, got 0.6667)
```

PASS format (ratio >= threshold):
```
Demographic Parity Analysis
============================
Threshold: 0.80

Group Results (sorted):
  group_a: 0.9000 (n=100)
  group_b: 0.8500 (n=80)

Result: PASS (ratio: 0.80 required, got 0.9444)
```

### Group Ordering (MINOR-2 fix)

Groups in the `FairnessReport.groups` list and in the formatted report output are sorted using Python's built-in `sorted()` on group name strings. This uses Unicode code point ordering (lexicographic). For ASCII group names (which is the expected case for this tool), this produces standard alphabetical ordering. Non-ASCII group names will sort by their Unicode code points, which is deterministic but may not match locale-specific collation expectations. This is acceptable for the current scope; locale-aware sorting can be added if needed in a future iteration.

### Group Name Handling

Group names are used **as-is** from the input data. No sanitization, trimming, or normalization is applied. If the data contains problematic group names (empty strings, whitespace-only strings, etc.), they will appear in the report unchanged. Ensuring clean group names is the user's responsibility.

### Timestamp and Imports (MINOR-3 fix)

The `FairnessReport` requires a `timestamp` field. The exact import used:

```python
from datetime import UTC, datetime
```

Timestamp is set via `datetime.now(tz=UTC)`. This uses the `UTC` sentinel added in Python 3.11. The project targets Python 3.12+ (confirmed in `pyproject.toml`: `requires-python = ">=3.12"`), so this is safe.

### Module Exports / `__init__.py` (MINOR-6 fix)

The top-level `fairness_checker/__init__.py` will re-export `compute_demographic_parity` and `format_report`. Rationale: these are the primary public API entry points for programmatic usage. Users should be able to do:

```python
from fairness_checker import compute_demographic_parity
```

The `__init__.py` will be updated to:

```python
"""AI Fairness Checker - Analyze ML model predictions for bias."""

from fairness_checker.metrics import compute_demographic_parity, format_report

__all__ = ["compute_demographic_parity", "format_report"]
```

### Docstrings and Type Hints (MINOR-5 fix)

Per the Definition of Done requirements ("All public functions have docstrings" and "Type hints on all public function signatures"), the following public functions must have full type annotations on all parameters and return types, plus docstrings:

1. **`compute_demographic_parity(dataset: Dataset, threshold: float = 0.8) -> FairnessReport`**
   - Docstring: Describes the function, parameters (with constraints), return value, and raises clause for ValueError.

2. **`format_report(report: FairnessReport) -> str`**
   - Docstring: Describes formatting behavior and return value.

3. **CLI command function `demographic_parity(file: str, threshold: float) -> None`**
   - Docstring: Describes the CLI command behavior.
   - Note: Click decorators handle parameter types at the CLI boundary; the function signature uses the types that Click passes through (str for file path, float for threshold).
   - Note: The Python function name is `demographic_parity` (underscore). Click automatically converts this to the CLI command name `demographic-parity` (hyphen). This is standard Click behavior — no explicit `name=` parameter is needed on the `@cli.command()` decorator.

All internal/private helper functions should also have type hints but docstrings are optional for those.

## Data Flow

```
CSV file
  |
  v
Dataset.from_csv(path)  -->  Dataset (pydantic model, validates binary values + lengths)
  |
  v
compute_demographic_parity(dataset, threshold)
  |
  |--> Validate threshold in [0.0, 1.0]
  |--> dataset.to_dataframe()
  |--> df.groupby("group")["prediction"].agg(["mean", "count"])
  |--> Filter groups with count == 0 (AC7, defensive guard -- structurally unreachable)
  |--> Sort groups by name using sorted() (Unicode code point order)
  |--> Build GroupMetric per group (metric_value = mean, sample_size = count)
  |--> Compute ratio: min_rate / max_rate (handle edge cases)
  |--> Compute overall_pass: ratio >= threshold
  |--> Return FairnessReport(
  |        metric_name="demographic_parity",
  |        groups=[...sorted...],
  |        overall_pass=...,
  |        threshold=threshold,
  |        ratio=ratio,
  |        timestamp=datetime.now(tz=UTC)
  |    )
  v
format_report(report)  -->  Human-readable string
  |
  v
stdout (CLI prints, sets exit code)
```

## Pydantic Models

- `Dataset` -- already in `models.py`, validates binary predictions/actuals and length consistency. **No changes.**
- `GroupMetric` -- already in `models.py`, holds group_name, metric_value, sample_size. **No changes.**
- `FairnessReport` -- already in `models.py`. **MODIFIED: add `ratio: float` field.** The updated model holds: metric_name, groups, overall_pass, threshold, ratio, timestamp.

### FairnessReport Model Change

Add a `ratio` field to `FairnessReport` in `models.py`:

```python
class FairnessReport(BaseModel):
    """Complete fairness analysis report for one metric."""

    metric_name: str
    groups: list[GroupMetric]
    overall_pass: bool
    threshold: float
    ratio: float
    timestamp: datetime
```

The `ratio` field stores the computed min_rate / max_rate value. This avoids recomputation in `format_report()` — the formatter reads `report.ratio` directly.

## Edge Case Handling Summary

| Scenario | Behavior | AC |
|----------|----------|----|
| Two groups, rates differ within threshold | overall_pass=True | AC1 |
| Three+ groups | min/max across all groups | AC2 |
| Custom threshold | Used in comparison | AC3 |
| Threshold out of [0.0, 1.0] | ValueError raised | AC4 |
| One group has zero positives | rate=0.0, overall_pass=False | AC5 |
| All groups identical rates | ratio=1.0, overall_pass=True | AC6 |
| Group with zero samples | Structurally impossible (Dataset validates non-empty lists; groupby never yields empty groups). Defensive guard retained in code. Test verifies structural guarantee: all groups in any report have sample_size >= 1. | AC7 |
| Single group | overall_pass=True | AC8 |
| CLI happy path | Print report, exit 0 or 1 | AC9 |
| CLI file not found | click.Path(exists=True) handles it | AC10 |
| All groups have zero positives | All rates=0.0, ratio=1.0 (0/0 defined as equal), overall_pass=True | Edge |

## AC7 Structural Guarantee

AC7 requires that groups with zero samples are handled gracefully. In this design, zero-sample groups are **impossible by construction**:

1. **Dataset validation**: The `Dataset` model's `group_labels` field is `list[str]`. Pydantic validates it is a list. Each entry maps 1:1 to a prediction/actual row. Every group label that appears in `group_labels` therefore has at least one sample.
2. **pandas groupby**: `df.groupby("group")` only produces groups for values that exist in the column. It never produces an empty group.

Therefore, the defensive filter `count == 0` in `compute_demographic_parity` is dead code. It is retained as a safety net but cannot be triggered through any valid input path.

**Test approach for AC7**: Instead of testing an impossible code path, the test `test_all_groups_have_samples_ac7` verifies the structural guarantee by constructing datasets with various group configurations and asserting that every `GroupMetric` in the resulting `FairnessReport` has `sample_size >= 1`.

## Test Strategy

### Test File: `tests/test_demographic_parity.py`

All tests use pytest. Tests are organized by AC. Each test function name encodes the AC it validates.

### Test-to-AC Mapping (MINOR-4 fix)

| Test Function | AC | Description |
|---------------|-----|-------------|
| `test_two_groups_pass_ac1` | AC1 | Two groups, ratio >= 0.8, overall_pass=True |
| `test_two_groups_fail_ac1` | AC1 | Two groups, ratio < 0.8, overall_pass=False |
| `test_two_groups_metric_name_ac1` | AC1 | Verify metric_name is "demographic_parity" |
| `test_two_groups_group_metrics_ac1` | AC1 | Verify GroupMetric values match expected positive rates |
| `test_three_groups_pass_ac2` | AC2 | Three groups, min/max ratio >= 0.8 |
| `test_three_groups_fail_ac2` | AC2 | Three groups, min/max ratio < 0.8 |
| `test_four_groups_ac2` | AC2 | Four groups to verify generalization |
| `test_custom_threshold_pass_ac3` | AC3 | Custom threshold=0.9, ratio meets it |
| `test_custom_threshold_fail_ac3` | AC3 | Custom threshold=0.9, ratio does not meet it |
| `test_custom_threshold_in_report_ac3` | AC3 | FairnessReport.threshold reflects custom value |
| `test_threshold_below_zero_ac4` | AC4 | threshold=-0.1 raises ValueError |
| `test_threshold_above_one_ac4` | AC4 | threshold=1.1 raises ValueError |
| `test_threshold_boundary_zero_ac4` | AC4 | threshold=0.0 is valid (boundary) |
| `test_threshold_boundary_one_ac4` | AC4 | threshold=1.0 is valid (boundary) |
| `test_group_zero_positives_ac5` | AC5 | One group all 0s, rate=0.0, overall_pass=False |
| `test_identical_rates_ac6` | AC6 | All groups same rate, ratio=1.0, overall_pass=True |
| `test_all_groups_have_samples_ac7` | AC7 | Verify structural guarantee: all groups in any report have sample_size >= 1 |
| `test_single_group_ac8` | AC8 | One group, overall_pass=True |
| `test_cli_pass_exit_code_ac9` | AC9 | CLI exits 0 when pass |
| `test_cli_fail_exit_code_ac9` | AC9 | CLI exits 1 when fail |
| `test_cli_output_format_ac9` | AC9 | CLI prints human-readable report |
| `test_cli_file_not_found_ac10` | AC10 | CLI with nonexistent file, non-zero exit |
| `test_format_report` | AC9 | format_report returns expected string structure |
| `test_groups_sorted_alphabetically` | Design | Verify groups are sorted by name (MINOR-2) |
| `test_report_has_utc_timestamp` | Design | Verify timestamp is UTC (MINOR-3) |
| `test_all_groups_zero_positives` | Edge | All groups have zero positive predictions |

Total: 26 tests covering all 10 ACs plus design requirements and edge cases.

### CLI Tests

CLI tests use Click's `CliRunner` for isolated testing:

- `CliRunner.invoke()` with `--file` pointing to a temp CSV.
- Assert exit code (0 for pass, 1 for fail).
- Assert output contains expected report elements.
- For AC10: invoke with nonexistent path, assert non-zero exit code and error message in output.

### Test Fixtures

- `two_group_dataset`: Dataset with two groups, known rates.
- `three_group_dataset`: Dataset with three groups.
- `single_group_dataset`: Dataset with one group.
- `zero_positives_dataset`: Dataset where one group has all-zero predictions.
- `tmp_csv_file`: Fixture factory pattern using pytest `tmp_path`. Takes a `Dataset` as argument, writes it to a CSV file via `dataset.to_dataframe().to_csv(path, index=False)`, and returns the `Path` to the CSV file. Usage: `csv_path = tmp_csv_file(my_dataset)`. Implemented as a fixture returning a callable (factory pattern).

## File Changes Summary

| File | Change |
|------|--------|
| `src/fairness_checker/models.py` | MODIFY -- add `ratio: float` field to `FairnessReport` |
| `src/fairness_checker/metrics.py` | NEW -- `compute_demographic_parity()`, `format_report()` |
| `src/fairness_checker/cli.py` | MODIFY -- add `demographic-parity` command; new imports: `import sys`, `from fairness_checker.metrics import compute_demographic_parity, format_report`, `from fairness_checker.models import Dataset` |
| `src/fairness_checker/__init__.py` | MODIFY -- re-export `compute_demographic_parity`, `format_report` |
| `tests/test_demographic_parity.py` | NEW -- all tests |

## Decisions Log

| Decision | Rationale |
|----------|-----------|
| `click.Path(exists=True)` for `--file` | Click handles file-not-found automatically with clear error message and non-zero exit. No custom error handling needed. (MINOR-1 confirmed) |
| `sorted()` for group ordering | Python default Unicode code point ordering. Deterministic, standard alphabetical for ASCII names. (MINOR-2) |
| `from datetime import UTC, datetime` | Python 3.11+ feature, project targets 3.12+. (MINOR-3) |
| Full test-to-AC matrix with 26 tests | Every AC has at least one test, most have multiple. (MINOR-4) |
| Docstrings + type hints on all public functions | DoD requirement. Three public functions identified. (MINOR-5) |
| Re-export from `__init__.py` | Clean public API for programmatic users. (MINOR-6) |
| `ratio: float` field on `FairnessReport` | Avoids recomputation in `format_report()`. Stored once at compute time. (MAJOR-2) |
| AC7 satisfied by construction | Dataset validation + pandas groupby structurally prevent zero-sample groups. Defensive guard retained. Test verifies the guarantee. (MAJOR-1) |
| `sys.exit()` for non-zero exit codes | Simpler than `ctx.exit()`. No Click context features needed. (MINOR-4 of review round 2) |
| `metrics.py` is a single file | Not a subpackage. Can be refactored later if more metrics are added. (MINOR-1 of review round 2) |
| Group names used as-is | No sanitization or trimming. User's responsibility. (MINOR-2 of review round 2) |
| `demographic_parity` function name | Click auto-converts underscore to hyphen for CLI command name. Standard behavior. (MINOR-3 of review round 2) |
| `tmp_csv_file` fixture | Factory pattern using `tmp_path`. Takes a Dataset, returns a Path. (MINOR-5 of review round 2) |
| cli.py imports listed explicitly | `import sys`, metric and model imports. (MINOR-6 of review round 2) |
