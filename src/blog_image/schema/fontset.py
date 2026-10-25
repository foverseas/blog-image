from dataclasses import dataclass, field
from pathlib import Path

from PIL import ImageFont


@dataclass
class FontSet:
    """Two faces plus a size cache: a card loads the same face at a dozen sizes."""

    regular_path: Path
    bold_path: Path
    _cache: dict = field(default_factory=dict, repr=False)

    def regular(self, size: int) -> ImageFont.FreeTypeFont:
        return self._load(self.regular_path, size)

    def bold(self, size: int) -> ImageFont.FreeTypeFont:
        return self._load(self.bold_path, size)

    def _load(self, path: Path, size: int) -> ImageFont.FreeTypeFont:
        key = (path, max(1, int(size)))
        font = self._cache.get(key)
        if font is None:
            font = ImageFont.truetype(str(path), key[1])
            self._cache[key] = font
        return font
