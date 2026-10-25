"""Read a spec file and validate it into a Spec."""

from __future__ import annotations

from ..errors import SpecError
from .build import spec_from_mapping
from .load import load_spec
from .parse import parse_colour, parse_format, slugify

__all__ = ["SpecError", "load_spec", "parse_colour", "parse_format", "slugify", "spec_from_mapping"]
