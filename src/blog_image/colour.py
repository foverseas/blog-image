"""The colour and box primitives the renderer and the motifs both measure in.

Nothing here imports from the rest of the package: both the card and its
decoration need these, and a shared leaf is cheaper than passing the
conversion down through the drawing calls.
"""

from __future__ import annotations

# The box a motif may draw in: left, top, right, bottom, in device pixels.
Box = tuple[float, float, float, float]
Colour = tuple[int, int, int]


def rgba(colour: Colour, alpha: float) -> tuple[int, int, int, int]:
    """Attach an alpha to an RGB triple. Pillow wants an int; callers compute floats."""
    return (*colour, max(0, min(255, int(alpha))))
