"""Read the spec file off disk."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..schema import Spec, SpecError
from .build import spec_from_mapping


def load_spec(path: Path) -> Spec:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SpecError(f"no such spec file: {path}") from None
    except yaml.YAMLError as error:
        raise SpecError(f"{path}: invalid YAML ({error})") from None
    if raw is None:
        raise SpecError(f"{path} is empty")
    return spec_from_mapping(raw, base=path.parent)
