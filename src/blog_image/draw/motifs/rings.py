"""Concentric arcs around the bottom-right corner."""

from __future__ import annotations

import math

from ..colour import Box, Colour, rgba


def rings(draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    """Quarter rings radiating from the corner, fading as they grow; the innermost accent."""
    x0, y0, x1, y1 = box
    span, height = x1 - x0, y1 - y0
    if span <= 0 or height <= 0:
        return

    step = scale * 0.024
    hairline = max(1, round(scale * 0.0012))
    # Far from the corner a ring taller than the band reads as a straight
    # tick, not a curve, so the field stops where the curvature still shows.
    reach = min(math.hypot(span, height), height * 3.5)
    count = min(22, int(reach // step))
    for index in range(1, count + 1):
        radius = index * step
        # The arc is clipped to the box by its angles. In Pillow's clockwise,
        # y-down convention, 180-270 degrees is the quarter climbing up and
        # left from the corner; each side the ring outgrows trims it further.
        start = 360 - math.degrees(math.acos(-span / radius)) if radius > span else 180.0
        end = 180 + math.degrees(math.asin(height / radius)) if radius > height else 270.0
        if start >= end:
            continue
        share = radius / reach
        colour = accent if index <= 2 else foreground
        alpha = 160 if index <= 2 else 150 - 120 * share
        bbox = (x1 - radius, y1 - radius, x1 + radius, y1 + radius)
        draw.arc(bbox, start=start, end=end, fill=rgba(colour, alpha), width=hairline)
