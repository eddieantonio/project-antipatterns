"""
Utilities for dealing with the Blackbox Mini directory structure.
"""

from pathlib import Path
from typing import Iterator

BLACKBOX_MINI_ROOT = Path("/data/mini/")


def slices():
    """
    Yields all slice directories from Blackbox Mini.
    """
    for entry in BLACKBOX_MINI_ROOT.glob("srcml-*"):
        assert entry.is_dir(), f"Not a slice directory: {entry}"
        yield entry


def projects(slice_path: Path) -> Iterator[Path]:
    """
    Yields all project paths in the given slice.
    """
    assert slice_path.match("srcml-*")
    for entry in slice_path.glob("project-*"):
        if not entry.is_dir():
            continue
        yield entry
