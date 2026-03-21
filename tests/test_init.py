# SPDX-License-Identifier: Unlicense
# This is free and unencumbered software released into the public domain.
# See UNLICENSE or <https://unlicense.org> for details.

"""Verify the public API surface declared in dfclean/__init__.py.

Guards against two regression classes:
  1. A symbol is present in __all__ but no longer importable (broken re-export).
  2. __version__ drifts from the canonical value in pyproject.toml.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import dfclean


class TestPublicAPI:
    """__all__ exports must be importable; __version__ must stay in sync."""

    def test_all_exports_are_importable(self) -> None:
        for name in dfclean.__all__:
            assert hasattr(dfclean, name), (
                f"'{name}' is listed in __all__ but is not importable from dfclean"
            )

    def test_version_is_semver(self) -> None:
        assert re.fullmatch(r"\d+\.\d+\.\d+", dfclean.__version__), (
            f"__version__ '{dfclean.__version__}' does not match MAJOR.MINOR.PATCH"
        )

    def test_version_matches_pyproject(self) -> None:
        """Ensures __version__ and pyproject.toml stay in sync across releases."""
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib  # type: ignore[no-redef]

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with pyproject_path.open("rb") as fh:
            data = tomllib.load(fh)

        toml_version: str = data["tool"]["poetry"]["version"]
        assert dfclean.__version__ == toml_version, (
            f"dfclean.__version__ ({dfclean.__version__!r}) != "
            f"pyproject.toml version ({toml_version!r})"
        )
