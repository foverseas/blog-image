"""Turn the spec's `police` value into a FontSet.

Four forms are accepted, tried in this order: an explicit mapping of the
two weights, a path template containing %s, a single file serving both
weights, and a family name looked up among what is installed.
"""

from __future__ import annotations

from pathlib import Path

from ..errors import FontError
from .discovery import find_face, search_dirs
from .fontset import FontSet

# Families tried, in order, when the spec says nothing.
FALLBACKS = ("JetBrains Mono", "IBM Plex Mono", "DejaVu Sans Mono", "DejaVu Sans", "Arial")

REGULAR_SUFFIXES = ("regular", "book", "")
BOLD_SUFFIXES = ("bold", "semibold", "demibold", "medium")


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
        regular = find_face(str(family), REGULAR_SUFFIXES)
        bold = find_face(str(family), BOLD_SUFFIXES)
        if regular is not None:
            return FontSet(regular, bold or regular)

    looked = ", ".join(str(path) for path in search_dirs()) or "no font directory found"
    raise FontError(
        f"could not find a font for {', '.join(str(f) for f in families)}. Looked in: {looked}. "
        "Install the family, or set `police` to a path template such as "
        "'~/Library/Fonts/JetBrainsMono-%s.ttf'."
    )
