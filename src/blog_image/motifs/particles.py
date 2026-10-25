"""A field of linked points, thickening towards the right."""

from __future__ import annotations

import math
import random

from ..colour import Box, Colour, rgba


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
