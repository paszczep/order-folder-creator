from tomllib import load as load_toml
from pathlib import Path
from enum import StrEnum
from app.product import Label

class Operator(StrEnum):
    """Składnia pliku konfiguracyjnego.

    pair        - para elementów,
    negative    - element wykluczający,
    wildcard    - dowolny znak,
    conjunction - łączone warunki,
    default     - domyślne repozytorium.
    """

    pair = "-"
    negative = "!"
    wildcard = "?"
    default = "_"
    conjunction = "&"


class DocsConfig(dict[Label, dict | str]):
    """Skonfigurowane lokalizacje repozytorów według wielokości i atrybutów produktu."""

    @property
    def _config(self) -> dict[str, str]:
        """Plik konfiguracyjny."""
        _file = Path("config/svn.toml")
        with _file.open("rb") as _f:
            return load_toml(_f)

    def __init__(self):
        """Normalizacja wartości użytkownika."""

        def _normalize(value):
            if isinstance(value, str):
                return value.replace("\\", "/")
            if isinstance(value, dict):
                return {k: _normalize(v) for k, v in value.items()}
            return value

        normalized = {k.upper(): _normalize(v) for k, v in self._config.items()}
        super().__init__(normalized)

    def product_paths(self, product: Label) -> list[str]:
        """Ścieżki do repozytoriów związanych z produktem, na potrzeby testu."""
        paths: list[str] = []

        def walk(node):
            if isinstance(node, str):
                if node:
                    paths.append(node)
            elif isinstance(node, dict):
                for value in node.values():
                    walk(value)
                    
        for key, value in self.items():
            if key == product:
                walk(value)

        return paths
    