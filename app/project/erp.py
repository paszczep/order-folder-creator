from dataclasses import dataclass
from enum import StrEnum
from datetime import date, timedelta
from re import sub
from logging import info
from app.external import Database



class ProjectGroup(StrEnum):
    """Grupy projektów, które wymagają folderu na dokumenty.
    
    Wartości stanowią etykiety projektów pobieranych z bazy, grupy projektów 
    w dokumentacji, oraz klucze przy wyborze skonfigurowanej struktury 
    folderów projektu."""
    
    OTHER = "OTHER"
    MATERIAL_KITS = "MATERIAL KITS"
    UPGRADES_GRI = "UPGRADES_GRI"
    SWITCHGEARS = "SWITCHGEARS"
    CIRCUIT_BREAKERS = "CIRCUIT BREAKERS"
    PROTECTIONS = "PROTECTIONS"
    SERVICE = "SERVICE"

    @classmethod
    def values_for_sql_query(cls) -> str:
        return ", ".join([f"'{e}'" for e in cls])


@dataclass
class ErpProject:
    """Projekt pobierany z bazy danych."""

    year: str
    group: ProjectGroup
    number: str
    partner: str

    def __post_init__(self):
        """Zamień na myślniki znaki nieprawidłowe dla nazwy folderu."""
        _p = sub(r"[^a-zA-Z0-9\s\-]", " ", self.partner)
        self.partner = sub(r"\s+", "-", _p)

    @classmethod
    def from_database(cls, timeframe: timedelta) -> list["ErpProject"]:
        """Pobierz z bazy danych projekty powstałe nie później niż."""
        info(f'Pobieranie projektów utworzonych w ciągu {timeframe.days} dni.')
        since_date = date.today() - timeframe
        db = Database("projects").query(
            project_groups=ProjectGroup.values_for_sql_query(),
            since_date=f"'{since_date.isoformat()}'",
        )
        return [cls(**o) for o in db.get_values(keys=True)]
    