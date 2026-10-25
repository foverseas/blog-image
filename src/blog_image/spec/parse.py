"""Parse the scalars a spec file is made of.

Each parser takes the raw YAML value and `where` -- the key to name in the
error -- because a message that says which key is wrong is the difference
between a fixable spec and a puzzle.
"""

from __future__ import annotations

import re
import unicodedata

from ..errors import SpecError
from ..schema import Format
from .vocabulary import PRESETS

_SIZE = re.compile(r"^(\d+)\s*[xX*×]\s*(\d+)$")
_SLUG = re.compile(r"[^a-z0-9]+")


def parse_colour(value: object, where: str) -> tuple[int, int, int]:
    """Accept #rgb, #rrggbb, or a three-number list."""
    if isinstance(value, (list, tuple)):
        if len(value) != 3 or not all(isinstance(n, int) for n in value):
            raise SpecError(f"{where}: expected three integers, got {value!r}")
        for n in value:
            if not 0 <= n <= 255:
                raise SpecError(f"{where}: {n} is outside 0-255")
        return tuple(value)  # type: ignore[return-value]
    if not isinstance(value, str):
        raise SpecError(f"{where}: expected a colour such as '#00ff99', got {value!r}")
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(c * 2 for c in text)
    if len(text) != 6 or not all(c in "0123456789abcdefABCDEF" for c in text):
        raise SpecError(f"{where}: '{value}' is not a hex colour such as '#00ff99'")
    return tuple(int(text[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def parse_format(token: object) -> Format:
    """'16x9' is a named ratio; '1600x900' is an explicit pixel size."""
    key = str(token).strip().lower()
    if key in PRESETS:
        return Format(key, *PRESETS[key])
    match = _SIZE.match(key)
    if not match:
        known = ", ".join(sorted(PRESETS))
        raise SpecError(f"formats: unknown format '{token}' (known: {known}, or WIDTHxHEIGHT in pixels)")
    width, height = int(match.group(1)), int(match.group(2))
    if not (16 <= width <= 8000 and 16 <= height <= 8000):
        raise SpecError(f"formats: '{token}' is outside 16-8000 pixels per side")
    return Format(f"{width}x{height}", width, height)


def slugify(text: str) -> str:
    """Accents fold to their base letter rather than becoming separators."""
    folded = unicodedata.normalize("NFKD", text)
    folded = "".join(char for char in folded if not unicodedata.combining(char))
    return _SLUG.sub("-", folded.lower()).strip("-") or "article"


def as_text(value: object, where: str) -> str:
    """A list is joined with newlines, which the renderer honours as hard breaks."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "\n".join(str(item) for item in value)
    return str(value)
