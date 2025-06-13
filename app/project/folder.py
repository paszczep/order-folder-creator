from pathlib import Path
from app.external import FILESERVER, APP_MODE
from .structure import TreeConfig
from .erp import ErpProject

class ProjectFolder:
    """Folder na dokumentację projektu."""

    _dir_config = TreeConfig
    _mount_dir: Path = FILESERVER.mount

    def __init__(self, erp_project: ErpProject):
        _p = erp_project
        self.group: str = _p.group
        self.number: str = _p.number
        parent = APP_MODE.consider_test_dir(_p.year)
        self._relative_path = Path(parent) / _p.group / f"{_p.number}_{_p.partner}"

    @property
    def directory_tree(self) -> dict:
        """Struktura folderów dla grupy projektu."""
        return self._dir_config.project_structure(self.group)

    @property
    def full_path(self) -> Path:
        """Pełna ścieżka dostępu folderu."""
        return self._mount_dir / self._relative_path
    
    @staticmethod
    def is_project_folder(path: Path) -> bool:
        """Czy wskazana lokalizacja to folder projektu?"""
        return path.is_dir() and path.name.startswith('510-')

    def __repr__(self) -> str:
        return f'Project - {self.group} - {self.number}'
    