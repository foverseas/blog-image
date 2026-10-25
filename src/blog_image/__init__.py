"""Generate article cover images in several aspect ratios from a short YAML file."""

from .draw import render
from .errors import FontError, SpecError
from .fonts import FontSet, resolve_fonts
from .schema import Format, Spec
from .spec import load_spec

__version__ = "0.2.0"
__all__ = ["FontError", "FontSet", "Format", "Spec", "SpecError", "load_spec", "render", "resolve_fonts"]
