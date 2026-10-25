"""Fine hatching climbing to the right."""

from __future__ import annotations

from ..colour import Box, Colour, rgba


def diagonals(draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    """Fine 45-degree strokes gaining ink to the right; the last ones accent."""
    x0, y0, x1, y1 = box
    span, height = x1 - x0, y1 - y0
    if span <= 0 or height <= 0:
        return

    step = scale * 0.024
    hairline = max(1, round(scale * 0.0012))
    count = int((span + height) // step)
    for index in range(count + 1):
        # The full stroke runs from (start, y1) up to (start + height, y0);
        # the parts outside the box are clipped here, before drawing.
        start = x0 - height + index * step
        t0 = max(0.0, (x0 - start) / height)
        t1 = min(1.0, (x1 - start) / height)
        if t0 >= t1:
            continue
        ax, ay = start + t0 * height, y1 - t0 * height
        bx, by = start + t1 * height, y1 - t1 * height
        share = ((ax + bx) / 2 - x0) / span
        colour = accent if share > 0.9 else foreground
        alpha = 130 if share > 0.9 else 22 + 80 * share
        draw.line((ax, ay, bx, by), fill=rgba(colour, alpha), width=hairline)
