"""Generate article cover images in several aspect ratios from a short YAML file."""

from .draw import render
from .fonts import FontSet, resolve_fonts
from .schema import Format, Spec
from .spec import load_spec

__version__ = "0.1.0"
__all__ = ["FontSet", "Format", "Spec", "load_spec", "render", "resolve_fonts"]
