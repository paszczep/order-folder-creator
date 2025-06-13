from dataclasses import dataclass
from typing import Optional
from re import search, UNICODE
from .designation import Operator, Flag


@dataclass(slots=True)
class Result:
    """Rezultat parowania ustawienia z produktem, wraz z
    ewentualnymi oznaczeniami znalezionymi w symbolu."""

    ok: bool
    positives: list[str]


@dataclass
class Matching:
    """Weryfikacja parowania produktu należącego do projektu, 
    z ustawieniem w konfiguracji źródła plików."""

    setting: str
    product: str

    def _contains(self, flag: str) -> Optional[str]:
        """Znajdź oznaczenie w symbolu produktu."""
        if Operator.wildcard in flag:
            match = search(
                pattern=flag.replace(Operator.wildcard, "."),
                string=self.product,
                flags=UNICODE,
            )
            return match.group(0) if match else None
        else:
            return flag if flag in self.product else None

    def check(self) -> Result:
        """Sprawdź elementy ustawień, zwróć oznaczenia znalezione w produkcie."""
        positives: list[str] = []
        passes: list[bool] = []

        for flag in Flag.parse(self.setting):
            if flag.is_negative:
                matched = self._contains(flag.positive)
                passes.append(matched is None)
            else:
                matched = self._contains(flag)
                passes.append(matched is not None)
                if matched:
                    positives.append(str(matched))
        return Result(ok=all(passes), positives=positives)
