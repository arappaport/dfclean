"""dfclean public API.

Import from here rather than sub-modules to get a stable interface.
Sub-module names and internal structure are implementation details
that may change between releases without a semver bump.
"""

from __future__ import annotations

#TODO - these 2 are old
from dfclean.stats import describe_dataframe, summary_stats
from dfclean.transform import filter_above_mean, normalise_column


from dfclean.clean import clean
from dfclean.process_removes import process_removes
from dfclean.load_cfg_file import load_cfg_file

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "describe_dataframe",
    "filter_above_mean",
    "normalise_column",
    "summary_stats",
	
	"clean", "process_removes", "validate_cfg"
]
