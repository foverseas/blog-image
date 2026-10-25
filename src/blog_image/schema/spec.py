from dataclasses import dataclass, field
from pathlib import Path

from .format import Format


@dataclass
class Spec:
    title: str
    subtitle: str = ""
    eyebrow: str = ""
    footer: str = ""
    background: tuple[int, int, int] = (28, 28, 34)
    foreground: tuple[int, int, int] = (255, 255, 255)
    accent: tuple[int, int, int] = (0, 255, 153)
    font: object = None
    motif: str = "particles"
    formats: tuple[Format, ...] = ()
    name: str = "article"
    out: Path = field(default_factory=lambda: Path("."))
    seed: int = 0
    dot: bool = True
    max_lines: int = 4

    def path_for(self, fmt: Format) -> Path:
        return self.out / f"{self.name}-{fmt.key}.png"
