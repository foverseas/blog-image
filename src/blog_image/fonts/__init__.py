"""Find the regular and bold faces of a family, wherever the machine keeps them.

The spec names a family ("JetBrains Mono"), a path template containing %s for
the weight, or an explicit pair of files. Nothing here downloads a font: if the
family is missing the error says where it looked, which is the only useful
thing to say.
"""

from __future__ import annotations

from .discovery import search_dirs
from .fontset import FontSet
from .resolve import resolve_fonts

__all__ = ["FontSet", "resolve_fonts", "search_dirs"]
