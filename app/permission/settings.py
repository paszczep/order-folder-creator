from pathlib import Path
from yaml import safe_load
from dataclasses import dataclass
from logging import info


class Configured:
    """Konfigurowane w pliku uprawnienia."""
    _file = Path('config/permissions.yaml')
    _config: dict = safe_load(_file.read_text())
    
    @classmethod
    def configured_names(cls) -> set[str]:
        """Foldery grup dokumentacji."""
        return list(cls._config.keys())
    
    @classmethod
    def get_permissions(cls, docs_group: str) -> dict[str, list]:
        """Uprawnienia dla folderu grupy dokumentacji."""
        return cls._config.get(docs_group)


@dataclass(init=False)
class Project:
    """Folder projektu.
        path        - ścieżka dostępu do folderu projektu,
        docs_groups - skonfigurowane grupy dokumentacji,
        all_folders - wszystkie foldery projektu.
    """
    path: Path
    docs_groups: set[Path]
    all_folders: set[Path]
    
    def __init__(self, path: Path):
        self.path = path
        self.docs_groups = {
            dir for dir in self.path.iterdir() 
            if dir.name in Configured.configured_names()}
        self.all_folders = {
            el for el in self.path.rglob('*') if el.is_dir()
            }
        

@dataclass
class Implied:
    """Uprawnienia zaimplikowane:
        - czytający i edytorzy widzą folder projektu, 
        - edytorzy nie mogą usuwać tworzonych folderów.
    """
    security: str
    receivers: set[str]
    directories: set[Path]
    
    @classmethod
    def settings(
        cls, readers: list[str], changers: list[str], project: Project
            ) -> list["Implied"]:
        CONSTANTS = [
            ("ADD ALLOWED READ", readers + changers, [project.path]),
            ("ADD DENIED DELETE", changers, project.all_folders)]
        return [cls(
            security=_s, receivers=set(_r), directories=set(_d)) 
            for _s, _r, _d in CONSTANTS]
        