from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from logging import info
from .settings import Implied, Configured

r"""

    `
        smbcacls (...) \
        --<option> ACL:<domain&group>:<type>/<flags>/<mask>
    `
        option: 
            "add" or "delete"
        type: 
            "ALLOWED" or "DENIED"
        flags:
            "OI|CI" - Object Inherit + Container Inherit
            "NP" - No Propagate Inherit
        mask:
            "READ" - Equivalent to 'RX' permissions
            "CHANGE" - Equivalent to 'RXWD' permissions
            "FULL" - Equivalent to 'RWXDPO' permissions
            "D" - Delete the object
            
"""

@dataclass(init=False)
class Security:
    """Interfejs pomiędzy konfigurowanym ustawieniem, a komendą smcacls.
    
    Argumenty:
        security    - skodyfikowane ustawienie, np. "ADD ALLOWED CHANGE",
        group       - grupa, beneficjent uprawnienia,
        path        - względna ścieżka dostępu,
        children    - czy zawartość dziedziczy ustawienie.
    
    Atrybuty:
        option      - dodaj, albo usuń uprawnienie
        allowed     - pozwól, albo zabroń 
        inherit     - czy uprawnienie dotyczy zawartości lokalizacji
        permission  - uprawnienie: pełne, odczyt, zmiana lub usuwanie
        group       - beneficjient uprawnienia
        path        - ścieżka do folderu, którego dotyczy uprawnienie.
    """
    option: Literal['add', 'delete']
    allowed: Literal['ALLOWED', 'DENIED']
    inherit: Literal["OI|CI", "NP"]
    permission: Literal['FULL', 'READ', 'CHANGE', 'D']
    group: str
    path: Path
    
    def __init__(self, security: str, group: str, path: Path, children: bool):
        option, allow, permission = security.split(' ')
        self.option = option.lower()
        self.allowed = allow.upper()
        self.permission = permission if not permission == 'DELETE' else 'D'
        self.inherit = "OI|CI" if children else "NP"
        self.group = group
        self.path = path
    
    @classmethod
    def implied(cls, setting: Implied) -> list["Security"]:
        """Zaimplikowane ustawienia dotyczą jedynie wskazanego folderu."""
        return [cls(
            security=setting.security, group=group, path=path, children=False) 
            for group in setting.receivers 
            for path in setting.directories]
            
    @classmethod
    def configured(cls, docs_folder: Path) -> list["Security"]:
        """Skonfigurowane ustawienia dotyczą folderu wraz z zawartością."""
        permissions = Configured.get_permissions(docs_folder.name)
        return [cls(
            security=security, group=group, path=docs_folder, children=True)
            for security, groups in permissions.items()
            for group in groups]