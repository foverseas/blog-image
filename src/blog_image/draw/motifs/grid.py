"""A dot lattice fading in from the left."""

from __future__ import annotations

from ..colour import Box, Colour, rgba


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
