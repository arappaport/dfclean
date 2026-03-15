import yaml
import logging
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def load_cfg_file(filepath: str | Path) -> dict | None:
    """
    Safely loads dfclean style samples file from local YAML file. Throws errors on any file issues.
    Returns the parsed data.

    Main purpose of this code - lots of logging to help debug samples issues.
    """
    path = Path(filepath)

    # --- File-level checks ---

    if not path.exists():
        msg = f" Path[{path} exists: {path.exists()}"
        log.error(msg)
        raise FileNotFoundError(msg)

    if not path.is_file():
        log.error("Path is not a file: %s", path)
        return None

    if path.stat().st_size == 0:
        log.error("File is empty: %s", path)
        return None

    if path.suffix.lower() not in {".yaml", ".yml"}:
        log.warning("Unexpected file extension '%s' — proceeding anyway.", path.suffix)

    # --- Parse ---
    try:
        with path.open("r", encoding="utf-8") as fh:
            # safe_load prevents arbitrary Python object instantiation
            data = yaml.safe_load(fh)
    except FileNotFoundError:
        log.error("File disappeared before it could be opened: %s", path)
        return None
    except PermissionError:
        log.error("Permission denied reading file: %s", path)
        return None
    except UnicodeDecodeError as exc:
        log.error("File is not valid UTF-8: %s — %s", path, exc)
        return None
    except yaml.scanner.ScannerError as exc:
        log.error("YAML syntax error in %s:\n  %s", path, exc)
        return None
    except yaml.parser.ParserError as exc:
        log.error("YAML parse error in %s:\n  %s", path, exc)
        return None
    except yaml.YAMLError as exc:
        # Catch-all for any other YAML-level error
        log.error("YAML error in %s:\n  %s", path, exc)
        return None

    # --- Post-parse checks ---
    if data is None:
        log.error("File parsed but produced no data (empty document): %s", path)
        return None

    if not isinstance(data, dict):
        log.error(
            "Expected a YAML mapping at the top level, got %s in %s",
            type(data).__name__, path,
        )
        return None

    return data


def validate_columns(data: dict) -> list[Any] | None:
    """
    Extract and validate the 'columns' key from parsed YAML data.
    Returns the columns list or None on failure.
    """
    if "columns" not in data:
        log.error("Required key 'columns' is missing from the YAML document.")
        return None

    columns = data["columns"]

    if not isinstance(columns, list):
        log.error(
            "'columns' must be a list, got %s instead.", type(columns).__name__
        )
        return None

    if len(columns) == 0:
        log.warning("'columns' is present but empty.")
        return columns

    log.info("Loaded %d column(s) successfully.", len(columns))

    # --- Inspect each entry ---
    for i, col in enumerate(columns):
        _inspect_column(i, col)

    return columns


def _inspect_column(index: int, col: Any) -> None:
    """Log a summary of each column entry for debugging."""
    if col is None:
        log.debug("  [%d] null value", index)
    elif isinstance(col, dict):
        name = col.get("name", "<unnamed>")
        dtype = col.get("type", "<no type>")
        log.debug("  [%d] dict  — name=%-20s type=%s", index, name, dtype)
    elif isinstance(col, list):
        log.debug("  [%d] list  — %d item(s): %s", index, len(col), col)
    else:
        log.debug("  [%d] scalar — %r (%s)", index, col, type(col).__name__)


def main():
    filepath = "sample.yaml"  # ← change to your file path

    log.info("Loading '%s' ...", filepath)
    data = load_yaml_file(filepath)
    if data is None:
        log.error("Aborting — could not load YAML file.")
        return

    columns = validate_columns(data)
    if columns is None:
        log.error("Aborting — 'columns' validation failed.")
        return

    # ---- Your application logic starts here ----
    print(f"\nSuccessfully loaded {len(columns)} column(s):\n")
    for i, col in enumerate(columns):
        print(f"  [{i:02d}] {col}")

