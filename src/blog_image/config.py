"""Read and validate the YAML spec.

Keys may be written in French or English; both spellings land on the same
field. Anything unrecognised is an error rather than a silent no-op, because a
typo in a key is otherwise invisible until you look at the finished card.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml

from .schema import Format, Spec, SpecError

# Pixel sizes for the ratios people actually ask for. 16x9 covers Open Graph
# and most blog headers, 4x3 the Google Discover slot, 1x1 the social avatar
# crop. A size written as WxH in pixels is accepted too.
PRESETS: dict[str, tuple[int, int]] = {
    "16x9": (1600, 900),
    "4x3": (1600, 1200),
    "1x1": (1200, 1200),
    "3x2": (1600, 1067),
    "2x1": (1600, 800),
    "4x5": (1080, 1350),
    "9x16": (1080, 1920),
}

DEFAULT_FORMATS = ("16x9", "4x3", "1x1")

ALIASES = {
    "titre": "title",
    "sous-titre": "subtitle",
    "sous_titre": "subtitle",
    "soustitre": "subtitle",
    "chapeau": "eyebrow",
    "surtitre": "eyebrow",
    "pied": "footer",
    "fond": "background",
    "texte": "foreground",
    "police": "font",
    "nom": "name",
    "sortie": "out",
    "graine": "seed",
    "point": "dot",
    "lignes-max": "max_lines",
    "lignes_max": "max_lines",
}

FIELDS = {
    "title",
    "subtitle",
    "eyebrow",
    "footer",
    "background",
    "foreground",
    "accent",
    "font",
    "motif",
    "formats",
    "name",
    "out",
    "seed",
    "dot",
    "max_lines",
}

MOTIF_ALIASES = {
    "particules": "particles",
    "particles": "particles",
    "grille": "grid",
    "grid": "grid",
    "aucun": "none",
    "none": "none",
}

_SIZE = re.compile(r"^(\d+)\s*[xX*×]\s*(\d+)$")
_SLUG = re.compile(r"[^a-z0-9]+")
# A title already ending in punctuation does not get the accent period.
_CLOSED = re.compile(r"[?!.:…»\"']$")


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


def _as_text(value: object, where: str) -> str:
    """A list is joined with newlines, which the renderer honours as hard breaks."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "\n".join(str(item) for item in value)
    return str(value)


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

    title = _as_text(data.get("title"), "title").strip()
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
        subtitle=_as_text(data.get("subtitle"), "subtitle").strip(),
        eyebrow=_as_text(data.get("eyebrow"), "eyebrow").strip(),
        footer=_as_text(data.get("footer"), "footer").strip(),
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


def load_spec(path: Path) -> Spec:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SpecError(f"no such spec file: {path}") from None
    except yaml.YAMLError as error:
        raise SpecError(f"{path}: invalid YAML ({error})") from None
    if raw is None:
        raise SpecError(f"{path} is empty")
    return spec_from_mapping(raw, base=path.parent)
