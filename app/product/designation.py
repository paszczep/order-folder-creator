from dataclasses import dataclass
from enum import StrEnum, auto
from re import match
from typing import Optional


class Label(StrEnum):
    """Nazwy produktów wymagających dokumentacji."""

    SPAM = "SPAM"
    BACON = "BACON"
    
    @staticmethod
    def product_prefix() -> str:
        return "e2"

    @property
    def with_prefix(self) -> str:
        return f"{self.product_prefix()}{self}"

    @classmethod
    def values_with_prefix(cls) -> list[str]:
        return [val.with_prefix for val in cls]

    @classmethod
    def values_for_sql_query(cls) -> str:
        return ", ".join([f"'{val.with_prefix}%'" for val in cls])
    
    @classmethod
    def values(cls) -> set[str]:
        return set(val for val in cls)


class _Symbol(str):
    """Symbol produktu: nazwa handlowa oraz ewentualne wielkość wyrażona liczbą
    i atrybuty określone alfanumerycznymi symbolami rozdzialanymi myślnikiem.
    """

    def __new__(cls, product_symbol: str) -> "_Symbol":
        return super().__new__(cls, product_symbol)

    @property
    def product_name(self) -> Label:
        """Nazwa handlowa produktu w jego symbolu."""
        return next(p for p in Label if self.upper().startswith(p))

    @staticmethod
    def _char_cleanup(_str: str) -> str:
        """Normalizacja wartości z zewnątrz."""
        replacements = {" / ": "/", "–": "-"}
        for old, new in replacements.items():
            _str = _str.replace(old, new)
        return _str.lstrip("-").lstrip(" ")

    def symbol_body(self, product: Label) -> str:
        """Korpus symbolu produktu, zawierający jego atrybuty."""
        _str = self[len(product):]
        return self._char_cleanup(_str)

    @staticmethod
    def match_numbers(body: str) -> str | None:
        """Znajdź wielkość produktu w jego symbolu."""
        if numbers := match(r"\d+", body):
            return numbers.group()


@dataclass(init=False)
class Product:
    """Produkt: nazwa, wielkość i atrybuty."""

    label: Label
    size: Optional[int] = None
    attributes: Optional[str] = None

    def __init__(self, product_index: str):
        """Przetwórz indeks produktu na wartości identyfikujące."""
        symbol = _Symbol(product_index)
        self.label = symbol.product_name
        if body := symbol.symbol_body(self.label):
            if _nrs := symbol.match_numbers(body):
                self.size = int(_nrs)
                body = body.lstrip(_nrs)
            self.attributes = body.lstrip("-")

    @classmethod
    def parse(cls, product_symbols: list[str]) -> list["Product"]:
        """Przetwórz indeksy produktów."""
        return [cls(symbol) for symbol in product_symbols]

    @property
    def identifier(self) -> str:
        """Nazwa handlowa i jego ewentualne wielkość i atrybuty."""
        parts = (self.label, self.size, self.attributes)
        return "-".join([str(x) for x in parts if x is not None])
