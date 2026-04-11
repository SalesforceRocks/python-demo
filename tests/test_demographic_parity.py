"""Tests for demographic parity metric (Issue #3).

All tests are organized by acceptance criterion. Every AC maps to at least one test.
Tests are written FIRST (TDD) and verified to fail before implementation.
"""

from datetime import UTC

import pytest

from fairness_checker.metrics import compute_demographic_parity, format_report
from fairness_checker.models import Dataset, FairnessReport

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def two_group_dataset() -> Dataset:
    """Dataset with two groups: 'a' has 80% positive, 'b' has 100% positive.

    Ratio = 0.8 / 1.0 = 0.8, which exactly meets the default threshold of 0.8.
    """
    return Dataset(
        predictions=[1, 1, 1, 1, 0, 1, 1, 1, 1, 1],  # 4 for 'a', 6 for 'b'
        actuals=[0] * 10,
        group_labels=["a", "a", "a", "a", "a", "b", "b", "b", "b", "b"],
    )


@pytest.fixture
def two_group_fail_dataset() -> Dataset:
    """Dataset with two groups: 'a' has 60% positive, 'b' has 100% positive.

    Ratio = 0.6 / 1.0 = 0.6, which is below the default threshold of 0.8.
    """
    return Dataset(
        predictions=[1, 1, 1, 0, 0, 1, 1, 1, 1, 1],  # 3/5 for 'a', 5/5 for 'b'
        actuals=[0] * 10,
        group_labels=["a", "a", "a", "a", "a", "b", "b", "b", "b", "b"],
    )


@pytest.fixture
def three_group_dataset() -> Dataset:
    """Dataset with three groups: 'a'=0.9, 'b'=0.8, 'c'=0.85.

    min=0.8, max=0.9, ratio=0.8/0.9 ≈ 0.8889 (pass at 0.8 threshold).
    """
    predictions = (
        [1] * 9 + [0]  # 'a': 9/10 = 0.9
        + [1] * 8 + [0, 0]  # 'b': 8/10 = 0.8
        + [1] * 17 + [0] * 3  # 'c': 17/20 = 0.85
    )
    group_labels = ["a"] * 10 + ["b"] * 10 + ["c"] * 20
    return Dataset(
        predictions=predictions,
        actuals=[0] * 40,
        group_labels=group_labels,
    )


@pytest.fixture
def three_group_fail_dataset() -> Dataset:
    """Dataset with three groups where ratio < 0.8.

    'a'=0.9, 'b'=0.5, 'c'=0.8 => min=0.5, max=0.9, ratio≈0.556 (fail).
    """
    predictions = (
        [1] * 9 + [0]  # 'a': 9/10 = 0.9
        + [1] * 5 + [0] * 5  # 'b': 5/10 = 0.5
        + [1] * 8 + [0, 0]  # 'c': 8/10 = 0.8
    )
    group_labels = ["a"] * 10 + ["b"] * 10 + ["c"] * 10
    return Dataset(
        predictions=predictions,
        actuals=[0] * 30,
        group_labels=group_labels,
    )


@pytest.fixture
def single_group_dataset() -> Dataset:
    """Dataset with one distinct group label."""
    return Dataset(
        predictions=[1, 0, 1, 1, 0],
        actuals=[0] * 5,
        group_labels=["only"] * 5,
    )


@pytest.fixture
def zero_positives_dataset() -> Dataset:
    """Dataset where group 'a' has zero positive predictions."""
    return Dataset(
        predictions=[0, 0, 0, 1, 1, 1],
        actuals=[0] * 6,
        group_labels=["a", "a", "a", "b", "b", "b"],
    )


@pytest.fixture
def identical_rates_dataset() -> Dataset:
    """Dataset where both groups have identical prediction rates (0.5)."""
    return Dataset(
        predictions=[1, 0, 1, 0],
        actuals=[0] * 4,
        group_labels=["a", "a", "b", "b"],
    )


@pytest.fixture
def all_zero_positives_dataset() -> Dataset:
    """Dataset where ALL groups have zero positive predictions."""
    return Dataset(
        predictions=[0, 0, 0, 0],
        actuals=[0] * 4,
        group_labels=["a", "a", "b", "b"],
    )


# ---------------------------------------------------------------------------
# AC1: Compute demographic parity for two groups
# ---------------------------------------------------------------------------


def test_two_groups_pass_ac1(two_group_dataset: Dataset) -> None:
    """AC1: Two groups with ratio >= 0.8 should produce overall_pass=True."""
    report = compute_demographic_parity(two_group_dataset)
    assert report.overall_pass is True


def test_two_groups_fail_ac1(two_group_fail_dataset: Dataset) -> None:
    """AC1: Two groups with ratio < 0.8 should produce overall_pass=False."""
    report = compute_demographic_parity(two_group_fail_dataset)
    assert report.overall_pass is False


def test_two_groups_metric_name_ac1(two_group_dataset: Dataset) -> None:
    """AC1: metric_name must be 'demographic_parity'."""
    report = compute_demographic_parity(two_group_dataset)
    assert report.metric_name == "demographic_parity"


def test_two_groups_group_metrics_ac1(two_group_dataset: Dataset) -> None:
    """AC1: GroupMetric values match expected positive rates.

    Group 'a': 4 out of 5 positive = 0.8, n=5.
    Group 'b': 5 out of 5 positive = 1.0, n=5.
    """
    report = compute_demographic_parity(two_group_dataset)
    assert len(report.groups) == 2
    # Groups are sorted alphabetically; 'a' first, 'b' second
    group_a = report.groups[0]
    group_b = report.groups[1]
    assert group_a.group_name == "a"
    assert group_a.metric_value == pytest.approx(0.8)
    assert group_a.sample_size == 5
    assert group_b.group_name == "b"
    assert group_b.metric_value == pytest.approx(1.0)
    assert group_b.sample_size == 5


# ---------------------------------------------------------------------------
# AC2: Three or more groups
# ---------------------------------------------------------------------------


def test_three_groups_pass_ac2(three_group_dataset: Dataset) -> None:
    """AC2: Three groups with min/max ratio >= 0.8 should pass."""
    report = compute_demographic_parity(three_group_dataset)
    assert report.overall_pass is True


def test_three_groups_fail_ac2(three_group_fail_dataset: Dataset) -> None:
    """AC2: Three groups with min/max ratio < 0.8 should fail."""
    report = compute_demographic_parity(three_group_fail_dataset)
    assert report.overall_pass is False


def test_four_groups_ac2() -> None:
    """AC2: Four groups generalization — verifies min/max uses all groups."""
    # 'a'=1.0, 'b'=0.9, 'c'=0.85, 'd'=0.7
    # ratio = 0.7 / 1.0 = 0.7 < 0.8 => fail
    predictions = [1] * 10 + [1] * 9 + [0] + [1] * 17 + [0] * 3 + [1] * 7 + [0] * 3
    group_labels = ["a"] * 10 + ["b"] * 10 + ["c"] * 20 + ["d"] * 10
    dataset = Dataset(
        predictions=predictions,
        actuals=[0] * 50,
        group_labels=group_labels,
    )
    report = compute_demographic_parity(dataset)
    assert report.overall_pass is False
    assert len(report.groups) == 4


# ---------------------------------------------------------------------------
# AC3: Custom threshold support
# ---------------------------------------------------------------------------


def test_custom_threshold_pass_ac3() -> None:
    """AC3: Custom threshold=0.9 — ratio that meets 0.9 should pass."""
    # 'a'=0.95, 'b'=1.0 => ratio = 0.95/1.0 = 0.95 >= 0.9
    predictions = [1] * 19 + [0] + [1] * 10
    group_labels = ["a"] * 20 + ["b"] * 10
    dataset = Dataset(
        predictions=predictions, actuals=[0] * 30, group_labels=group_labels
    )
    report = compute_demographic_parity(dataset, threshold=0.9)
    assert report.overall_pass is True


def test_custom_threshold_fail_ac3() -> None:
    """AC3: Custom threshold=0.9 — ratio below 0.9 should fail."""
    # 'a'=0.8, 'b'=1.0 => ratio=0.8 < 0.9
    predictions = [1] * 8 + [0, 0] + [1] * 10
    group_labels = ["a"] * 10 + ["b"] * 10
    dataset = Dataset(
        predictions=predictions, actuals=[0] * 20, group_labels=group_labels
    )
    report = compute_demographic_parity(dataset, threshold=0.9)
    assert report.overall_pass is False


def test_custom_threshold_in_report_ac3() -> None:
    """AC3: FairnessReport.threshold must reflect the custom threshold value."""
    dataset = Dataset(predictions=[1, 0], actuals=[0, 0], group_labels=["a", "b"])
    report = compute_demographic_parity(dataset, threshold=0.9)
    assert report.threshold == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# AC4: Threshold validation
# ---------------------------------------------------------------------------


def test_threshold_below_zero_ac4() -> None:
    """AC4: threshold=-0.1 must raise ValueError."""
    dataset = Dataset(predictions=[1, 0], actuals=[0, 0], group_labels=["a", "b"])
    with pytest.raises(ValueError, match="threshold"):
        compute_demographic_parity(dataset, threshold=-0.1)


def test_threshold_above_one_ac4() -> None:
    """AC4: threshold=1.1 must raise ValueError."""
    dataset = Dataset(predictions=[1, 0], actuals=[0, 0], group_labels=["a", "b"])
    with pytest.raises(ValueError, match="threshold"):
        compute_demographic_parity(dataset, threshold=1.1)


def test_threshold_boundary_zero_ac4() -> None:
    """AC4: threshold=0.0 is a valid boundary value (no error raised)."""
    dataset = Dataset(predictions=[1, 0], actuals=[0, 0], group_labels=["a", "b"])
    # Should not raise
    report = compute_demographic_parity(dataset, threshold=0.0)
    assert isinstance(report, FairnessReport)


def test_threshold_boundary_one_ac4() -> None:
    """AC4: threshold=1.0 is a valid boundary value (no error raised)."""
    dataset = Dataset(predictions=[1, 1], actuals=[0, 0], group_labels=["a", "b"])
    # Should not raise; ratio=1.0 >= 1.0 => pass
    report = compute_demographic_parity(dataset, threshold=1.0)
    assert isinstance(report, FairnessReport)


# ---------------------------------------------------------------------------
# AC5: Group with zero positive predictions
# ---------------------------------------------------------------------------


def test_group_zero_positives_ac5(zero_positives_dataset: Dataset) -> None:
    """AC5: Group with all-zero predictions => rate=0.0, overall_pass=False."""
    report = compute_demographic_parity(zero_positives_dataset)
    # group 'a' has rate 0.0
    group_a = next(g for g in report.groups if g.group_name == "a")
    assert group_a.metric_value == pytest.approx(0.0)
    assert report.overall_pass is False


# ---------------------------------------------------------------------------
# AC6: All groups have identical prediction rates
# ---------------------------------------------------------------------------


def test_identical_rates_ac6(identical_rates_dataset: Dataset) -> None:
    """AC6: Identical rates across all groups => ratio=1.0, overall_pass=True."""
    report = compute_demographic_parity(identical_rates_dataset)
    assert report.ratio == pytest.approx(1.0)
    assert report.overall_pass is True


# ---------------------------------------------------------------------------
# AC7: Groups with zero samples (structural guarantee)
# ---------------------------------------------------------------------------


def test_all_groups_have_samples_ac7() -> None:
    """AC7: Structural guarantee — all groups in any report have sample_size >= 1.

    Zero-sample groups are impossible by construction (Dataset validation +
    pandas groupby). This test verifies that guarantee holds across various
    dataset configurations.
    """
    datasets = [
        Dataset(predictions=[1, 0], actuals=[0, 0], group_labels=["x", "y"]),
        Dataset(predictions=[1, 1, 0], actuals=[0, 0, 0], group_labels=["a", "b", "c"]),
        Dataset(
            predictions=[0, 0, 0, 0],
            actuals=[0, 0, 0, 0],
            group_labels=["p", "p", "q", "q"],
        ),
    ]
    for ds in datasets:
        report = compute_demographic_parity(ds)
        for group in report.groups:
            assert group.sample_size >= 1, (
                f"Group {group.group_name!r} has sample_size={group.sample_size}"
            )


# ---------------------------------------------------------------------------
# AC8: Single group
# ---------------------------------------------------------------------------


def test_single_group_ac8(single_group_dataset: Dataset) -> None:
    """AC8: Single group => overall_pass=True, one GroupMetric returned."""
    report = compute_demographic_parity(single_group_dataset)
    assert report.overall_pass is True
    assert len(report.groups) == 1


# ---------------------------------------------------------------------------
# AC9: format_report (unit test of the formatting function)
# ---------------------------------------------------------------------------


def test_format_report() -> None:
    """AC9: format_report returns a string with expected structure."""
    from datetime import datetime

    from fairness_checker.models import GroupMetric

    report = FairnessReport(
        metric_name="demographic_parity",
        groups=[
            GroupMetric(group_name="group_a", metric_value=0.75, sample_size=100),
            GroupMetric(group_name="group_b", metric_value=0.5, sample_size=80),
        ],
        overall_pass=False,
        threshold=0.8,
        ratio=0.6667,
        timestamp=datetime.now(tz=UTC),
    )
    output = format_report(report)
    assert "Demographic Parity Analysis" in output
    assert "Threshold: 0.80" in output
    assert "group_a" in output
    assert "group_b" in output
    assert "FAIL" in output
    assert "0.6667" in output


# ---------------------------------------------------------------------------
# Design: Group ordering (sorted alphabetically)
# ---------------------------------------------------------------------------


def test_groups_sorted_alphabetically() -> None:
    """Design: Groups in FairnessReport are sorted alphabetically by group_name."""
    predictions = [1, 0, 1, 0, 1]
    group_labels = ["charlie", "alpha", "bravo", "alpha", "charlie"]
    dataset = Dataset(
        predictions=predictions, actuals=[0] * 5, group_labels=group_labels
    )
    report = compute_demographic_parity(dataset)
    names = [g.group_name for g in report.groups]
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# Design: UTC timestamp (MINOR-3)
# ---------------------------------------------------------------------------


def test_report_has_utc_timestamp(two_group_dataset: Dataset) -> None:
    """Design: FairnessReport timestamp must be timezone-aware UTC."""
    report = compute_demographic_parity(two_group_dataset)
    assert report.timestamp.tzinfo is not None
    assert (
        report.timestamp.tzinfo == UTC
        or report.timestamp.utcoffset().total_seconds() == 0
    )


# ---------------------------------------------------------------------------
# Edge: All groups have zero positive predictions
# ---------------------------------------------------------------------------


def test_all_groups_zero_positives(all_zero_positives_dataset: Dataset) -> None:
    """Edge: All groups have zero positive predictions => ratio=1.0, overall_pass=True.

    When max_rate is 0, all groups are equal (all predict negative), so ratio
    is defined as 1.0 and overall_pass is True.
    """
    report = compute_demographic_parity(all_zero_positives_dataset)
    assert report.ratio == pytest.approx(1.0)
    assert report.overall_pass is True
