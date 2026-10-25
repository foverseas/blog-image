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
