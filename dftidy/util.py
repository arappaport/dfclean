# SPDX-License-Identifier: Unlicense
# This is free and unencumbered software released into the public domain.
# See UNLICENSE or <https://unlicense.org> for details.

import logging
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)


#Generated - easy.  Could also use humanize package
def _bytes_to_human(num_bytes: int) -> str:
    """Convert a byte count to a human-readable size string (e.g. 3.2 MB)."""
    if num_bytes < 0:
        raise ValueError(f"byte count cannot be negative: {num_bytes}")

    for unit in ("bytes", "kb", "MB", "GB", "TB", "PB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024

    return f"{num_bytes:.1f} EB"

def check_file(filepath: str | Path, logger:logging.Logger=None) -> str | None:
    """
    utility - help debug file load issues by checking for its existence.
    I reuse it enough - even though it does fit with packages purpose.

    returns error string or None - if no error

    Check for:
    * path to existence
    * path is a file
    * file is not empty

    The main purpose of this code - lots of logging to help debug file load issues.
    """
    logger = logger or LOGGER

    filepath = str(filepath).strip()
    if not filepath:
        msg = f" Empty filepath [{filepath}]"
        return msg

    path = Path(filepath)

    abs_path = (Path.cwd() / path).resolve()
    logger.debug("Checking existence of file [%s]", filepath)
    logger.debug("      cwd: [%s]", Path.cwd())
    logger.debug(" abs_path: [%s]", abs_path)

    msg = f" path exists: {path.exists()}"
    logger.debug(msg)
    if not path.exists():
        return msg

    msg = f" is_file: {path.is_file()}"
    logger.debug(msg)
    if not path.is_file():
        return msg

    size = path.stat().st_size
    msg = f" size:  bytes: {path.stat().st_size:,}.  readable:{_bytes_to_human(size)}"
    logger.debug(msg)
    if size <= 0:
        return msg

    return None


