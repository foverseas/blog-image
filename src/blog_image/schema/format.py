from dataclasses import dataclass


@dataclass(frozen=True)
class Format:
    """One output size."""

    key: str
    width: int
    height: int

    @property
    def ratio(self) -> float:
        return self.height / self.width
