"""Decoration for the empty band under the text.

A motif is handed an RGBA overlay, the box it may use, and `scale` — the same
typographic unit the text is sized from. Dots and strokes are measured from
`scale`, never from the box: a 16:9 card leaves a band a few hundred pixels
tall and a 1:1 card leaves one five times that, and anything sized from the
box vanishes in the first and overwhelms the second. Only how many marks fit
depends on the box.
"""

from __future__ import annotations

import math
import random

from .colour import Box, Colour, rgba


def particles(draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    """A field of linked points, thickening towards the right."""
    x0, y0, x1, y1 = box
    span, height = x1 - x0, y1 - y0
    if span <= 0 or height <= 0:
        return

    rng = random.Random(seed)
    count = max(20, min(72, round(span * height / (scale * 0.085) ** 2)))
    # The exponent biases x towards the right edge: the field reads as building
    # up rather than as uniform noise.
    points = [(x0 + span * rng.random() ** 0.55, y0 + height * rng.random()) for _ in range(count)]

    # Link anything closer than about one and a half nearest-neighbour spacings,
    # so the mesh stays equally open whatever shape the band happens to be.
    reach = 1.6 * math.sqrt(span * height / count)
    hairline = max(1, round(scale * 0.0008))
    for index, (ax, ay) in enumerate(points):
        for bx, by in points[index + 1 :]:
            distance = math.hypot(ax - bx, ay - by)
            if distance >= reach:
                continue
            nearness = 1 - distance / reach
            rightness = 0.3 + 0.7 * ((ax + bx) / 2 - x0) / span
            draw.line((ax, ay, bx, by), fill=rgba(foreground, 72 * nearness * rightness), width=hairline)

    radius = max(1.5, scale * 0.0022)
    for x, y in points:
        alpha = 80 + 130 * ((x - x0) / span)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(accent, alpha))


def grid(draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    """A dot lattice fading in from the left; the last column picks up the accent."""
    x0, y0, x1, y1 = box
    span, height = x1 - x0, y1 - y0
    if span <= 0 or height <= 0:
        return

    step = max(scale * 0.030, min(scale * 0.055, height / 3))
    columns = max(1, int(span // step))
    rows = max(1, int(height // step))
    radius = max(1.0, step * 0.05)
    for column in range(columns + 1):
        x = x0 + column * step
        if x > x1:
            break
        share = column / columns
        for row in range(rows + 1):
            y = y0 + row * step
            if y > y1:
                break
            colour = accent if share > 0.86 else foreground
            alpha = (120 if share > 0.86 else 26 + 90 * share)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(colour, alpha))


def none(draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    """Leave the band empty."""


MOTIFS = {"particles": particles, "grid": grid, "none": none}


def draw_motif(name: str, draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    MOTIFS[name](draw, box, accent=accent, foreground=foreground, seed=seed, scale=scale)
