from .configured import Operator


class Flag(str):
    """Oznaczenie produktu wewnątrz konfiguracji, określające źródło dokumentacji."""

    def __new__(cls, flag: str) -> "Flag":
        return super().__new__(cls, flag)

    @property
    def is_pair(self) -> bool:
        """Czy oznaczenie produktu jest parą elementów?"""
        return Operator.pair in self

    @property
    def is_negative(self) -> bool:
        """Czy oznaczenie jest negatywne?"""
        return self.startswith(Operator.negative)

    @property
    def positive(self) -> str:
        """Pozytywny odpowiednik negatywnego oznaczenia."""
        return self.lstrip(Operator.negative)

    @classmethod
    def _split_pair(cls, flag: str) -> tuple["Flag", "Flag"]:
        """Rozdziel parowane elementy."""
        left, right = flag.split(Operator.pair, 1)
        return cls(left), cls(right)

    @classmethod
    def _join_pair(cls, left: "Flag", right: "Flag") -> tuple["Flag", ...]:
        """Rozpatrz mieszane pary i połącz parowane elementy."""
        if right.is_negative:
            compound = Operator.negative + left + Operator.pair + right.positive
            return left, cls(compound)
        else:
            return (cls(f"{left}{Operator.pair}{right}"),)

    @classmethod
    def parse(cls, setting: str) -> list["Flag"]:
        """Przetwórz skonfigurowane oznaczenie produktu."""
        parts = (token.strip() for token in setting.split(Operator.conjunction))
        base  = [cls(p) for p in parts if p]
        flags = [f for f in base if not f.is_pair]
        pairs = [cls._split_pair(f) for f in base if f.is_pair]
        for left, right in pairs:
            flags.extend(cls._join_pair(left, right))
        return flags
