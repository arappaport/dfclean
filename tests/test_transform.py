"""Unit tests for dfclean.transform."""

from __future__ import annotations

import pandas as pd
import pytest

from dfclean.transform import normalise_column


class TestNormaliseColumn:
    """normalise_column: range correctness, immutability, and error contracts."""

    def test_output_range_is_zero_to_one(self, sample_df: pd.DataFrame) -> None:
        result = normalise_column(sample_df, "value")
        assert result["value"].min() == pytest.approx(0.0)
        assert result["value"].max() == pytest.approx(1.0)

    def test_known_values(self, sample_df: pd.DataFrame) -> None:
        # value=[10,20,30,40,50], range=40 → step size 0.25
        result = normalise_column(sample_df, "value")
        assert list(result["value"]) == pytest.approx([0.0, 0.25, 0.50, 0.75, 1.0])

    def test_input_dataframe_not_mutated(self, sample_df: pd.DataFrame) -> None:
        original = sample_df["value"].tolist()
        normalise_column(sample_df, "value")
        assert sample_df["value"].tolist() == original

    def test_non_target_columns_unchanged(self, sample_df: pd.DataFrame) -> None:
        result = normalise_column(sample_df, "value")
        pd.testing.assert_series_equal(result["score"], sample_df["score"])

    @pytest.mark.parametrize("bad_col", ["nonexistent", "", "VALUE"])
    def test_missing_column_raises_key_error(
        self, sample_df: pd.DataFrame, bad_col: str
    ) -> None:
        with pytest.raises(KeyError):
            normalise_column(sample_df, bad_col)

    @pytest.mark.parametrize(
        "values",
        [
            [5.0, 5.0, 5.0],
            [0.0],
            [1e9, 1e9, 1e9],
        ],
    )
    def test_zero_variance_raises_value_error(self, values: list[float]) -> None:
        df = pd.DataFrame({"value": values})
        with pytest.raises(ValueError, match="zero variance"):
            normalise_column(df, "value")

