from typing import Any
from app.product import Product
from .configured import DocsConfig

class _Size:
    """Skonfigurowane wielkości produktu."""

    def __init__(self, mapping: dict[str, Any]):
        """Mapowanie skonfigurowanych kluczy wielkości produktu na zakresy."""
        self._ranges = []
        for key, value in mapping.items():
            if "-" in key:
                start, end = map(int, key.split("-"))
                self._ranges.append(((start, end), value, key))
            else:
                n = int(key)
                self._ranges.append(((n, n), value, key))

    def get_value(self, number: int) -> str | dict:
        """Wartość dla wielkości produktu."""
        for (start, end), value, _ in self._ranges:
            if start <= number <= end:
                return value
        raise ValueError(f"{number} not in any defined range")

    def get_key(self, number: int) -> str:
        """Klucz dla wielkości produktu."""
        for (start, end), _, key_str in self._ranges:
            if start <= number <= end:
                return key_str


class Gauge:
    """Określenie wielkości produktu według skonfigurowanych wartości, lub zakresów."""

    config: DocsConfig = DocsConfig()

    @classmethod
    def configured_value(cls, product: Product) -> dict | str:
        """Wartość skonfigurowana dla nazwy produktu i jego ewentualnej wielkości."""
        _conf = cls.config.get(product.label)
        if product.size:
            _conf = _Size(_conf).get_value(product.size)
        return _conf

    @classmethod
    def size_key(cls, product: Product) -> str:
        """Skonfigurowany klucz odpowiadający wielkości produktu."""
        _conf = cls.config.get(product.label)
        return _Size(_conf).get_key(product.size)
    