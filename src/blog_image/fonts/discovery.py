"""Where the machine keeps its fonts, and what is installed there.

The directory list is the platform-specific part of this package: a new
operating system is a branch in `search_dirs` and nothing else.
"""

from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path

_NORM = re.compile(r"[^a-z0-9]+")


def search_dirs() -> list[Path]:
    home = Path.home()
    if sys.platform == "darwin":
        candidates = [home / "Library/Fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts")]
    elif sys.platform.startswith("win"):
        candidates = [Path("C:/Windows/Fonts"), home / "AppData/Local/Microsoft/Windows/Fonts"]
    else:
        candidates = [
            home / ".fonts",
            home / ".local/share/fonts",
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
        ]
    return [path for path in candidates if path.is_dir()]


@lru_cache(maxsize=1)
def _installed() -> dict[str, Path]:
    """Map every installed face to its normalised stem, first match winning."""
    found: dict[str, Path] = {}
    for directory in search_dirs():
        for pattern in ("*.ttf", "*.otf", "*.ttc"):
            for path in sorted(directory.rglob(pattern)):
                found.setdefault(_NORM.sub("", path.stem.lower()), path)
    return found


def find_face(family: str, suffixes: tuple[str, ...]) -> Path | None:
    slug = _NORM.sub("", family.lower())
    installed = _installed()
    for suffix in suffixes:
        hit = installed.get(slug + suffix)
        if hit is not None:
            return hit
    return None
