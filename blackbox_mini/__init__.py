"""
Utilities for dealing with the Blackbox Mini directory structure.
"""

from pathlib import Path


BLACKBOX_MINI_ROOT = Path("/data/mini/")


def slices():
    """
    Yields all slice directories from Blackbox Mini.
    """
    for entry in BLACKBOX_MINI_ROOT.glob("srcml-*"):
        assert entry.is_dir(), f"Not a slice directory: {entry}"
        yield entry
