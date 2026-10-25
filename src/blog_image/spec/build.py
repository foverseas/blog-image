"""Assemble a validated Spec from the mapping YAML gave us.

An unrecognised key is an error rather than a silent no-op: a typo in a key
is otherwise invisible until you look at the finished card.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..errors import SpecError
from ..schema import Spec
from .parse import as_text, parse_colour, parse_format, slugify
from .vocabulary import ALIASES, DEFAULT_FORMATS, FIELDS, MOTIF_ALIASES, THEMES

# A title already ending in punctuation does not get the accent period.
_CLOSED = re.compile(r"[?!.:…»\"']$")


def spec_from_mapping(raw: dict, base: Path | None = None) -> Spec:
    """Turn the parsed YAML into a Spec. `base` resolves relative output paths."""
    if not isinstance(raw, dict):
        raise SpecError("the spec file must be a mapping of keys to values")

    data: dict[str, object] = {}
    for key, value in raw.items():
        canonical = ALIASES.get(str(key).strip().lower(), str(key).strip().lower())
        if canonical not in FIELDS:
            known = ", ".join(sorted(FIELDS | set(ALIASES)))
            raise SpecError(f"unknown key '{key}' (known keys: {known})")
        data[canonical] = value

    theme = data.pop("theme", None)
    if theme is not None:
        wanted = str(theme).strip().lower()
        if wanted not in THEMES:
            raise SpecError(f"theme: '{wanted}' is not one of {', '.join(sorted(THEMES))}")
        # A theme only fills the colours left unsaid: an explicit key wins.
        for colour_key, value in THEMES[wanted].items():
            data.setdefault(colour_key, value)

    title = as_text(data.get("title")).strip()
    if not title:
        raise SpecError("`titre` (or `title`) is required and must not be empty")

    formats = data.get("formats") or list(DEFAULT_FORMATS)
    if isinstance(formats, str):
        formats = [part for part in re.split(r"[,\s]+", formats) if part]
    if not isinstance(formats, (list, tuple)) or not formats:
        raise SpecError("formats: expected a non-empty list such as [16x9, 4x3, 1x1]")

    motif_key = str(data.get("motif", "particles")).strip().lower()
    if motif_key not in MOTIF_ALIASES:
        raise SpecError(f"motif: '{motif_key}' is not one of {', '.join(sorted(MOTIF_ALIASES))}")

    max_lines = int(data.get("max_lines", 4) or 4)
    if max_lines < 1:
        raise SpecError("lignes_max: must be at least 1")

    out = Path(str(data.get("out", ".")))
    if base is not None and not out.is_absolute():
        out = base / out

    return Spec(
        title=title,
        subtitle=as_text(data.get("subtitle")).strip(),
        # The kicker is set as one tracked line: hard breaks fold to spaces.
        eyebrow=as_text(data.get("eyebrow")).replace("\n", " ").strip(),
        footer=as_text(data.get("footer")).strip(),
        background=parse_colour(data.get("background", "#1c1c22"), "fond"),
        foreground=parse_colour(data.get("foreground", "#ffffff"), "texte"),
        accent=parse_colour(data.get("accent", "#00ff99"), "accent"),
        font=data.get("font"),
        motif=MOTIF_ALIASES[motif_key],
        formats=tuple(parse_format(token) for token in formats),
        name=slugify(str(data["name"])) if data.get("name") else "article",
        out=out,
        seed=int(data.get("seed", 0) or 0),
        dot=bool(data.get("dot", True)) and not _CLOSED.search(title),
        max_lines=max_lines,
    )
