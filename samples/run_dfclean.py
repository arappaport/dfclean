"""
dfclean-demo: Load data_cleaned_expected.csv and run dfclean pipeline.

dfclean public API (from arappaport/dfclean README):
  - run_pipeline(df, column)  → {"filtered": DataFrame, "stats": dict}
  - summary_stats(df, column) → dict of descriptive stats
  - describe_dataframe(df)    → dict of stats per numeric column
  - normalise_column(df, col) → DataFrame (min-max normalised)
  - filter_above_mean(df, col)→ DataFrame (rows > mean)

NOTE: dfclean.clean() is referenced in the README overview as config-driven
but is NOT exported in the public API. run_pipeline() is the canonical
entrypoint that chains normalise → filter → stats.
"""

from __future__ import annotations

import sys
from pathlib import Path
import logging
import yaml
import pandas as pd
import json
import dfclean

LOGGER = logging.getLogger(__name__)

CSV_ORIG_PATH              = Path("samples/data_sample.csv")
#PAth to where a csv of what we expect a cleaned dataframe to look at based on CSV_ORIG_PATH
CSV_EXPECTED_CLEANED_PATH = Path("samples/data_cleaned_expected.csv")
CSV_ACTUAL_CLEANED_PATH   = Path("samples/data_cleaned_actual.csv")  #write ti this file

CFG_YAML_PATH             = Path("samples/config_sample.yaml")


def load_csv(path: Path) -> pd.DataFrame:
    """Load CSV with basic validation."""
    msg = dfclean.check_file(path, logger=LOGGER)
    if msg is not None:
        LOGGER.error(msg)
        raise ValueError(msg)


    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path.resolve()}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("CSV loaded but DataFrame is empty.")
    return df



def load_yaml(filepath: str | Path) -> dict | None:
    """
    Safely load a YAML file. Returns parsed dict or None on any error.
    Logs all failures with enough context to debug.
    """
    path = Path(filepath)

    if not path.exists():
        LOGGER.error("File not found: %s", path.resolve())
        return None

    if not path.is_file():
        LOGGER.error("Path is not a file: %s", path.resolve())
        return None

    if path.stat().st_size == 0:
        LOGGER.error("File is empty: %s", path.resolve())
        return None

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except PermissionError:
        LOGGER.error("Permission denied: %s", path.resolve())
        return None
    except UnicodeDecodeError as exc:
        LOGGER.error("File is not valid UTF-8: %s — %s", path.resolve(), exc)
        return None
    except yaml.YAMLError as exc:
        LOGGER.error("YAML parse error in %s:\n  %s", path.resolve(), exc)
        return None

    if data is None:
        LOGGER.error("File parsed but is empty document: %s", path.resolve())
        return None

    if not isinstance(data, dict):
        LOGGER.error("Expected a YAML mapping, got %s in %s", type(data).__name__, path.resolve())
        return None

    LOGGER.debug("Loaded %s (%d keys)", path.name, len(data))
    return data



#simple - generated
def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> str | None:
    """
    Compare two DataFrames for structural and value equality.
    Returns None if identical, or an error string describing the first difference.
    """

    # shape
    if df1.shape != df2.shape:
        return f"Shape mismatch: {df1.shape} vs {df2.shape}"

    # columns — order matters
    if list(df1.columns) != list(df2.columns):
        return f"Column mismatch:\n  df1: {list(df1.columns)}\n  df2: {list(df2.columns)}"

    # dtypes
    if list(df1.dtypes) != list(df2.dtypes):
        return f"Dtype mismatch:\n{df1.dtypes.compare(df2.dtypes)}"

    # values — NaN-safe comparison
    if not df1.equals(df2):
        diff = df1.compare(df2)
        return f"Value mismatch in {len(diff)} row(s):\n{diff}"

    return None

def main() -> None:

    print(f"Using dfclean version: ", dfclean.__version__)

    print(f"Loading {CSV_ORIG_PATH} ...")
    df_orig = load_csv(CSV_ORIG_PATH)
    print(f"Pre-clean:: {df_orig.shape[0]} rows × {df_orig.shape[1]} cols\n")

    print(f"Loading {CFG_YAML_PATH} ...")
    cfg = load_yaml(CFG_YAML_PATH)

    msg = dfclean.validate_cfg(colcfg=cfg)
    if msg is not None:
        LOGGER.error(msg)
        exit(-1)
    print(json.dumps(cfg, indent=2))

    df_cleaned = dfclean.clean(df_orig, cfg=cfg, inplace=False)

    print("after dfcleaned")
    print(df_cleaned.head())

    df_expected = load_csv(CSV_EXPECTED_CLEANED_PATH)

    # standard — no index, utf-8
    df_cleaned.to_csv(CSV_ACTUAL_CLEANED_PATH, index=False)
    print(f" wrote cleaned dataframe to [{CSV_ACTUAL_CLEANED_PATH.resolve()}]")

    are_eq = df_cleaned.equals(df_expected)
    LOGGER.info("df_cleaned == df_expected: %s",are_eq)
    if are_eq:
        LOGGER.info("cleaned dataframe equals expected.  See [%s]", Path(CSV_EXPECTED_CLEANED_PATH).resolve())
    else:

        LOGGER.error("not equal.  Check expected file: [%s]", Path(CSV_EXPECTED_CLEANED_PATH).resolve())
        LOGGER.error("comparing cleaned to expected- using df_orig.compare()")
        LOGGER.error(df_cleaned.compare(df_expected))

        msg = compare_dataframes(df_cleaned, df_expected)
        LOGGER.error(msg)


    dbg = 12
if __name__ == "__main__":
    main()
