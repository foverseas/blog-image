"""Decoration for the empty band under the text.

A motif is handed an RGBA overlay, the box it may use, and `scale` — the same
typographic unit the text is sized from. Dots and strokes are measured from
`scale`, never from the box: a 16:9 card leaves a band a few hundred pixels
tall and a 1:1 card leaves one five times that, and anything sized from the
box vanishes in the first and overwhelms the second. Only how many marks fit
depends on the box.
"""

from __future__ import annotations

from ..colour import Box, Colour
from .diagonals import diagonals
from .grid import grid
from .halftone import halftone
from .particles import particles
from .protocol import Motif
from .rings import rings


def none(draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    """Leave the band empty."""


MOTIFS: dict[str, Motif] = {
    "particles": particles,
    "grid": grid,
    "diagonals": diagonals,
    "halftone": halftone,
    "rings": rings,
    "none": none,
}


def draw_motif(name: str, draw, box: Box, *, accent: Colour, foreground: Colour, seed: int, scale: float) -> None:
    MOTIFS[name](draw, box, accent=accent, foreground=foreground, seed=seed, scale=scale)


__all__ = ["MOTIFS", "Motif", "diagonals", "draw_motif", "grid", "halftone", "none", "particles", "rings"]
