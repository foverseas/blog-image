"""Generate article cover images in several aspect ratios from a short YAML file."""

from .config import Format, Spec, load_spec
from .draw import render
from .fonts import FontSet, resolve_fonts

__version__ = "0.1.0"
__all__ = ["FontSet", "Format", "Spec", "load_spec", "render", "resolve_fonts"]
