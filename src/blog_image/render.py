"""Draw one card.

Two things here are worth keeping when you read the code:

* Everything is drawn at SS times the final size and resampled down. That, not
  the rasteriser's own antialiasing, is what keeps hairlines and small type
  clean; the cost is memory for a moment and nothing else.
* Type is scaled from `unit`, not from the width. A 1:1 card is no wider than a
  4:3 one but has far more room, and sizing on width alone leaves it hollow.
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .motifs import draw_motif
from .schema import FontSet, Format, Spec

SS = 3

# Fractions of `unit`. Changing a card's proportions means changing these and
# nothing else.
PAD = 0.075
EYEBROW = 0.021
TITLE = 0.055
TITLE_FLOOR = 0.028
SUBTITLE = 0.026
SUBTITLE_FLOOR = 0.016
FOOTER = 0.019
GAP = 0.028

# Split on whitespace, except the spaces whose whole job is to forbid a break:
# French sets one before `?`, `!`, `;` and `:`, and str.split() would happily
# drop the mark onto a line of its own.
BREAKABLE = re.compile(r"[^\S\u00a0\u202f\u2007]+")
# Below this the band is a smear rather than a field, so the motif is dropped.
MIN_BAND = 0.035


def _rgba(colour: tuple[int, int, int], alpha: float) -> tuple[int, int, int, int]:
    return (*colour, max(0, min(255, int(alpha))))


def wrap(text: str, font: ImageFont.FreeTypeFont, max_width: float) -> list[str]:
    """Greedy wrap on the measured advance width of the actual face."""
    words = [word for word in BREAKABLE.split(text.strip()) if word]
    if not words:
        return []
    lines, current = [], words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.getlength(candidate) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def fit(text: str, loader, size: int, max_width: float, max_lines: int, floor: int):
    """Shrink until the text fits in `max_lines` of `max_width`, or hits the floor.

    The width is checked as well as the line count: a single word longer than
    the line wraps to one line and would otherwise never trigger a shrink, so a
    long compound or a URL in a title would run off the card.
    """
    size = max(size, floor)
    while True:
        font = loader(size)
        lines: list[str] = []
        for paragraph in text.split("\n"):
            lines.extend(wrap(paragraph, font, max_width) or [""])
        widest = max((font.getlength(line) for line in lines), default=0.0)
        if (len(lines) <= max_lines and widest <= max_width) or size <= floor:
            return font, lines, size
        size = max(floor, int(size * 0.94))


def tracked_width(text: str, font: ImageFont.FreeTypeFont, tracking: float) -> float:
    return sum(font.getlength(char) for char in text) + tracking * max(0, len(text) - 1)


def draw_tracked(draw, xy, text: str, font, fill, tracking: float) -> None:
    """Letter-spaced text; Pillow has no tracking of its own."""
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += font.getlength(char) + tracking


def render(spec: Spec, fonts: FontSet, fmt: Format, path: Path) -> Path:
    """Render one format of `spec` to `path` and return it."""
    width, height = fmt.width * SS, fmt.height * SS
    pad = round(width * PAD)
    inner = width - 2 * pad
    unit = width * (1 + max(0.0, height / width - 0.5625) * 0.34)

    canvas = Image.new("RGBA", (width, height), (*spec.background, 255))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    y = float(pad)

    if spec.eyebrow:
        font = fonts.bold(round(unit * EYEBROW))
        draw_tracked(draw, (pad, y), spec.eyebrow.upper(), font, _rgba(spec.accent, 255), font.size * 0.22)
        y += font.size * 2.6

    title_font, title_lines, title_size = fit(
        spec.title, fonts.bold, round(unit * TITLE), inner, spec.max_lines, round(unit * TITLE_FLOOR)
    )
    line_height = title_size * 1.26
    for index, line in enumerate(title_lines):
        draw.text((pad, y), line, font=title_font, fill=_rgba(spec.foreground, 255))
        if spec.dot and index == len(title_lines) - 1:
            draw.text((pad + title_font.getlength(line), y), ".", font=title_font, fill=_rgba(spec.accent, 255))
        y += line_height

    if spec.subtitle:
        y += title_size * 0.5
        sub_font, sub_lines, sub_size = fit(
            spec.subtitle, fonts.regular, round(unit * SUBTITLE), inner, 3, round(unit * SUBTITLE_FLOOR)
        )
        for line in sub_lines:
            draw.text((pad, y), line, font=sub_font, fill=_rgba(spec.foreground, 150))
            y += sub_size * 1.5

    content_bottom = y

    footer_font = fonts.regular(round(unit * FOOTER))
    footer_top = height - pad - footer_font.size * 1.4
    if spec.footer:
        radius = footer_font.size * 0.16
        centre = footer_top + footer_font.size * 0.62
        draw.ellipse((pad, centre - radius, pad + 2 * radius, centre + radius), fill=_rgba(spec.accent, 255))
        draw.text(
            (pad + 2 * radius + footer_font.size * 0.75, footer_top),
            spec.footer,
            font=footer_font,
            fill=_rgba(spec.foreground, 120),
        )

    band_top = content_bottom + unit * GAP
    band_bottom = footer_top - unit * GAP
    if band_bottom - band_top > unit * MIN_BAND:
        draw_motif(
            spec.motif,
            draw,
            (pad, band_top, width - pad, band_bottom),
            accent=spec.accent,
            foreground=spec.foreground,
            seed=spec.seed,
            scale=unit,
        )

    image = Image.alpha_composite(canvas, overlay).convert("RGB")
    image = image.resize((fmt.width, fmt.height), Image.Resampling.LANCZOS)
    # 256 colours is plenty for flat art and roughly halves the file.
    image = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)
    return path
