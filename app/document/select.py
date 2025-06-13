from pathlib import PurePosixPath
from dataclasses import dataclass
from typing import Optional
from app.product import Product
from app.external import Files
from .configured import Operator
from .check import Matching
from .product import Gauge

@dataclass
class Selection:
    """Wybór źródła i pików dla produktu, oraz znaczące elementy jego symbolu.
    
    _source  - ścieżka dostępu repozytorium plików produktu,
    _product - indeks produktu,
    entries  - pliki produktu z repozytorium,
    flags    - atrybuty produktu określające dokumentację.
    """
    _source: PurePosixPath
    _product: Product
    entries: Files
    flags: Optional[list[str]] = None

    def _type_product(self, mapping: dict[str, str]) -> str:
        """Sprawdź atrybuty produktu przez pryzmat konfiguracji i wybierz źródło."""
        for product_key, docs_path in mapping.items():
            if product_key == Operator.default:
                continue
            _check = Matching(
                setting=product_key, product=self._product.attributes
            ).check()
            if _check.ok:
                self.flags = _check.positives
                return docs_path
        return mapping.get(Operator.default)

    def _type_subdir(self) -> str | None:
        """Określ źródło pików na podstawie produktu."""
        _conf = Gauge.configured_value(self._product)
        if isinstance(_conf, str):
            return _conf
        elif isinstance(_conf, dict):
            return self._type_product(_conf)

    def __init__(self, product: Product):
        self._product = product
        self._source = PurePosixPath(product.label.with_prefix)
        if (sub_type := self._type_subdir()):
            self._source = self._source / sub_type
        self.entries = Files(self._source)
