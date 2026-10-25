"""Turn a validated Spec into an image file.

Nothing outside this package needs anything from it but `render`: the colour
conversion, the typesetting and the motifs are how a card is drawn, not part
of what a caller asks for.
"""

from __future__ import annotations

from .render import render

__all__ = ["render"]
