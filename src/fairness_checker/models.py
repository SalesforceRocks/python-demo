"""Pydantic data models for the AI Fairness Checker."""

from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator


class Dataset(BaseModel):
    """Encapsulates prediction data with group labels for fairness analysis."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    predictions: list[int]
    actuals: list[int]
    group_labels: list[str]

    @field_validator("predictions", "actuals")
    @classmethod
    def validate_binary(cls, v: list[int]) -> list[int]:
        if not all(val in (0, 1) for val in v):
            msg = "Values must be binary (0 or 1)."
            raise ValueError(msg)
        return v

    @field_validator("actuals")
    @classmethod
    def validate_same_length(cls, v: list[int], info) -> list[int]:  # noqa: N805
        predictions = info.data.get("predictions")
        if predictions is not None and len(v) != len(predictions):
            msg = "actuals and predictions must have the same length."
            raise ValueError(msg)
        return v

    @field_validator("group_labels")
    @classmethod
    def validate_group_labels_length(cls, v: list[str], info) -> list[str]:  # noqa: N805
        predictions = info.data.get("predictions")
        if predictions is not None and len(v) != len(predictions):
            msg = "group_labels must have the same length as predictions."
            raise ValueError(msg)
        return v

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return pd.DataFrame(
            {
                "prediction": self.predictions,
                "actual": self.actuals,
                "group": self.group_labels,
            }
        )

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        prediction_col: str = "prediction",
        actual_col: str = "actual",
        group_col: str = "group",
    ) -> "Dataset":
        """Create a Dataset from a pandas DataFrame."""
        return cls(
            predictions=df[prediction_col].tolist(),
            actuals=df[actual_col].tolist(),
            group_labels=df[group_col].tolist(),
        )

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        prediction_col: str = "prediction",
        actual_col: str = "actual",
        group_col: str = "group",
    ) -> "Dataset":
        """Load a Dataset from a CSV file."""
        df = pd.read_csv(path)
        return cls.from_dataframe(df, prediction_col, actual_col, group_col)


class GroupMetric(BaseModel):
    """Fairness metric result for a single group."""

    group_name: str
    metric_value: float
    sample_size: int


class FairnessReport(BaseModel):
    """Complete fairness analysis report for one metric."""

    metric_name: str
    groups: list[GroupMetric]
    overall_pass: bool
    threshold: float
    ratio: float
    timestamp: datetime
