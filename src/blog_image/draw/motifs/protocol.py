"""The contract every motif honours.

Naming it buys two things a repeated signature does not: a type checker can
tell you a new motif is wrong before it is ever called, and the registry can
say what it holds rather than `dict[str, object]`.
"""

from __future__ import annotations

from typing import Protocol

from ..colour import Box, Colour


class Motif(Protocol):
    """Fill `box` with decoration measured from `scale`, drawing onto `draw`.

    Nothing is returned, and nothing outside `box` is touched. `seed` is what
    makes a random motif reproducible from one run to the next; a motif with
    nothing random in it ignores the argument rather than refusing it.
    """

    def __call__(
        self,
        draw,
        box: Box,
        *,
        accent: Colour,
        foreground: Colour,
        seed: int,
        scale: float,
    ) -> None: ...
