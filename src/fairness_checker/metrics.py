"""Fairness metrics computation for the AI Fairness Checker."""

from datetime import UTC, datetime

from fairness_checker.models import Dataset, FairnessReport, GroupMetric


def compute_demographic_parity(
    dataset: Dataset,
    threshold: float = 0.8,
) -> FairnessReport:
    """Compute the demographic parity metric across protected groups.

    Demographic parity (statistical parity) measures whether the proportion of
    positive predictions is equal across protected groups. The ratio version is
    defined as min_rate / max_rate, where rates are the positive prediction rates
    per group.

    Args:
        dataset: A Dataset containing binary predictions and group labels.
                 Actuals are not used in this metric.
        threshold: The minimum acceptable ratio of min_rate / max_rate.
                   Must be in [0.0, 1.0]. Defaults to 0.8 (the four-fifths rule).

    Returns:
        A FairnessReport with metric_name="demographic_parity", one GroupMetric
        per group (sorted alphabetically by group name), the computed ratio,
        and overall_pass=True when ratio >= threshold.

    Raises:
        ValueError: If threshold is not in [0.0, 1.0].
    """
    if not (0.0 <= threshold <= 1.0):
        msg = f"threshold must be between 0.0 and 1.0 (inclusive), got {threshold}."
        raise ValueError(msg)

    df = dataset.to_dataframe()

    # Aggregate per group: mean (positive rate) and count (sample size)
    agg = df.groupby("group")["prediction"].agg(["mean", "count"])

    # Defensive guard: filter out any groups with zero samples.
    # This is structurally unreachable via Dataset validation + pandas groupby,
    # but is retained as a safety net.
    agg = agg[agg["count"] > 0]

    # Sort groups alphabetically (Unicode code point / lexicographic order)
    agg = agg.sort_index()

    group_metrics = [
        GroupMetric(
            group_name=str(group_name),
            metric_value=float(row["mean"]),
            sample_size=int(row["count"]),
        )
        for group_name, row in agg.iterrows()
    ]

    # Single group: no disparity possible
    if len(group_metrics) <= 1:
        ratio = 1.0
        overall_pass = True
    else:
        rates = [g.metric_value for g in group_metrics]
        max_rate = max(rates)
        min_rate = min(rates)

        if max_rate == 0.0:
            # All groups predict negative — all equal, by convention ratio=1.0
            ratio = 1.0
            overall_pass = True
        else:
            ratio = min_rate / max_rate
            overall_pass = ratio >= threshold

    return FairnessReport(
        metric_name="demographic_parity",
        groups=group_metrics,
        overall_pass=overall_pass,
        threshold=threshold,
        ratio=ratio,
        timestamp=datetime.now(tz=UTC),
    )


def format_report(report: FairnessReport) -> str:
    """Format a FairnessReport as a human-readable string.

    The report includes the threshold, per-group positive prediction rates,
    and an overall PASS/FAIL result based on the stored ratio value.

    Args:
        report: A FairnessReport produced by compute_demographic_parity.

    Returns:
        A formatted multi-line string suitable for printing to stdout.
    """
    lines = [
        "Demographic Parity Analysis",
        "============================",
        f"Threshold: {report.threshold:.2f}",
        "",
        "Group Results (sorted):",
    ]

    for group in report.groups:
        rate = f"{group.metric_value:.4f}"
        lines.append(f"  {group.group_name}: {rate} (n={group.sample_size})")

    result_label = "PASS" if report.overall_pass else "FAIL"
    required = f"{report.threshold:.2f}"
    got = f"{report.ratio:.4f}"
    lines.append(f"\nResult: {result_label} (ratio: {required} required, got {got})")

    return "\n".join(lines)
