"""Set text into a measured box.

Everything here measures the real face rather than guessing from the character
count: a monospaced fallback and a proportional family wrap at wildly
different points, and a card whose title overflows is worse than one whose
title is a size smaller.
"""

from __future__ import annotations

import re

from PIL import ImageFont

# Split on whitespace, except the spaces whose whole job is to forbid a break:
# French sets one before `?`, `!`, `;` and `:`, and str.split() would happily
# drop the mark onto a line of its own.
BREAKABLE = re.compile(r"[^\S\u00a0\u202f\u2007]+")


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


# One step of the size search: small enough to stop near the largest size
# that fits, large enough to finish in a handful of measurements.
SHRINK = 0.94


def shrink_to_fit(loader, size: int, floor: int, fits) -> ImageFont.FreeTypeFont:
    """Walk the size down by SHRINK steps until `fits(font)`, or return the floor."""
    size = max(size, floor)
    while True:
        font = loader(size)
        if fits(font) or size <= floor:
            return font
        size = max(floor, int(size * SHRINK))


def fit(text: str, loader, size: int, max_width: float, max_lines: int, floor: int, tail: str = ""):
    """Shrink until the text fits in `max_lines` of `max_width`, or hits the floor.

    The width is checked as well as the line count: a single word longer than
    the line wraps to one line and would otherwise never trigger a shrink, so a
    long compound or a URL in a title would run off the card.

    `tail` is drawn after the last line (the title's accent dot) but never
    wrapped, so its advance is measured with that line here.
    """

    def lines_at(font) -> list[str]:
        lines: list[str] = []
        for paragraph in text.split("\n"):
            lines.extend(wrap(paragraph, font, max_width) or [""])
        return lines

    def fits(font) -> bool:
        lines = lines_at(font)
        widest = max((font.getlength(line) for line in lines), default=0.0)
        if len(lines) > max_lines or widest > max_width:
            return False
        return font.getlength(lines[-1]) + font.getlength(tail) <= max_width

    font = shrink_to_fit(loader, size, floor, fits)
    return font, lines_at(font), font.size


def tracked_width(text: str, font: ImageFont.FreeTypeFont, tracking: float) -> float:
    return sum(font.getlength(char) for char in text) + tracking * max(0, len(text) - 1)


def fit_tracked(text: str, loader, size: int, max_width: float, tracking: float, floor: int):
    """Shrink a letter-spaced line until it fits `max_width`; cut it at the floor.

    `fit` cannot do this job: it measures with `font.getlength`, which knows
    nothing of the tracking `draw_tracked` will add. And because the tracking
    is a fraction of the font size, it shrinks along with the face -- so the
    width has to be measured again at each step rather than scaled.

    Returns the font and the text to draw. A label too long even at the floor
    has no wrapping to fall back on, so it is cut on an ellipsis rather than
    handed back wider than the box it was measured for.
    """

    def fits(font) -> bool:
        return tracked_width(text, font, font.size * tracking) <= max_width

    font = shrink_to_fit(loader, size, floor, fits)
    if not fits(font):
        while text and tracked_width(text + "…", font, font.size * tracking) > max_width:
            text = text[:-1].rstrip()
        text += "…"
    return font, text


def draw_tracked(draw, xy, text: str, font, fill, tracking: float) -> None:
    """Letter-spaced text; Pillow has no tracking of its own."""
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += font.getlength(char) + tracking
