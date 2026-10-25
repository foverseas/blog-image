"""A print-style halftone ramp: dots growing towards the right."""

from __future__ import annotations

from ..colour import Box, Colour, rgba


def halftone(draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    """A staggered lattice whose dots grow to the right; the densest pick up the accent.

    Where `grid` ramps the ink and keeps the dot, halftone keeps the ink and
    ramps the dot, the way a printed tint does.
    """
    x0, y0, x1, y1 = box
    span, height = x1 - x0, y1 - y0
    if span <= 0 or height <= 0:
        return

    step = max(scale * 0.026, min(scale * 0.048, height / 3))
    radius_max = step * 0.30
    rows = max(1, int(height // step))
    for row in range(rows + 1):
        y = y0 + row * step
        if y > y1:
            break
        # Every other row shifts by half a step: the classic 45-degree screen.
        offset = (row % 2) * step / 2
        column = 0
        while (x := x0 + offset + column * step) <= x1:
            column += 1
            share = (x - x0) / span
            radius = radius_max * share**1.4
            if radius < 0.55:
                continue
            colour = accent if share > 0.92 else foreground
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(colour, 100))
