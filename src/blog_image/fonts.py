"""Find the regular and bold faces of a family, wherever the machine keeps them.

The spec names a family ("JetBrains Mono"), a path template containing %s for
the weight, or an explicit pair of files. Nothing here downloads a font: if the
family is missing the error says where it looked, which is the only useful
thing to say.
"""

from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path

from .schema import FontError, FontSet

_NORM = re.compile(r"[^a-z0-9]+")

# Families tried, in order, when the spec says nothing.
FALLBACKS = ("JetBrains Mono", "IBM Plex Mono", "DejaVu Sans Mono", "DejaVu Sans", "Arial")

REGULAR_SUFFIXES = ("regular", "book", "")
BOLD_SUFFIXES = ("bold", "semibold", "demibold", "medium")


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


def _find_face(family: str, suffixes: tuple[str, ...]) -> Path | None:
    slug = _NORM.sub("", family.lower())
    installed = _installed()
    for suffix in suffixes:
        hit = installed.get(slug + suffix)
        if hit is not None:
            return hit
    return None


def _expand(value: str) -> Path:
    return Path(value).expanduser()


def resolve_fonts(spec_font: object) -> FontSet:
    """Turn the spec's `police` value into a FontSet."""
    if isinstance(spec_font, dict):
        missing = {"regular", "bold"} - set(spec_font)
        if missing:
            raise FontError(
                f"police: a mapping needs both `regular` and `bold` (missing: {', '.join(sorted(missing))})"
            )
        regular, bold = _expand(str(spec_font["regular"])), _expand(str(spec_font["bold"]))
        for path in (regular, bold):
            if not path.is_file():
                raise FontError(f"police: no such font file: {path}")
        return FontSet(regular, bold)

    if isinstance(spec_font, str) and "%s" in spec_font:
        regular, bold = _expand(spec_font % "Regular"), _expand(spec_font % "Bold")
        for path in (regular, bold):
            if not path.is_file():
                raise FontError(f"police: the template produced a missing file: {path}")
        return FontSet(regular, bold)

    if isinstance(spec_font, str) and _expand(spec_font).is_file():
        path = _expand(spec_font)
        return FontSet(path, path)

    families = [spec_font] if isinstance(spec_font, str) and spec_font.strip() else list(FALLBACKS)
    for family in families:
        regular = _find_face(str(family), REGULAR_SUFFIXES)
        bold = _find_face(str(family), BOLD_SUFFIXES)
        if regular is not None:
            return FontSet(regular, bold or regular)

    looked = ", ".join(str(path) for path in search_dirs()) or "no font directory found"
    raise FontError(
        f"could not find a font for {', '.join(str(f) for f in families)}. Looked in: {looked}. "
        "Install the family, or set `police` to a path template such as "
        "'~/Library/Fonts/JetBrainsMono-%s.ttf'."
    )
