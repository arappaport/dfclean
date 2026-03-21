# SPDX-License-Identifier: Unlicense
# This is free and unencumbered software released into the public domain.
# See UNLICENSE or <https://unlicense.org> for details.

"""dfclean public API.
"""

from __future__ import annotations

from dfclean.clean import clean
from dfclean.process_removes import process_removes
from dfclean.validate_cfg import validate_cfg
from dfclean.util import check_file

__version__ = "0.1.2"

__all__ = [
    "__version__",
	"clean",
    "process_removes",
    "validate_cfg"
]
