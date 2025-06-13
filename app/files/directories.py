from pathlib import Path
from shutil import rmtree
from logging import info
from dataclasses import dataclass
from app.project import ProjectFolder

class DirectoryError(Exception):
    """Błąd tworzenia folderu, lub zapisu pliku."""
    pass

def directory_safe(func):
    """Wychwyć błąd pliku wewnątrz funkcji."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OSError as exc:
            raise DirectoryError(exc) from exc
    return wrapper


@dataclass
class _Structure:
    """Struktura folderów na dokumentację projektu."""
    project: ProjectFolder
    
    def delete_project(self):
        """Usuń strukturę, jeśli jest folderem projektu."""
        project_path = self.project.full_path
        if ProjectFolder.is_project_folder(project_path):
            rmtree(project_path)
    
    @directory_safe
    @staticmethod
    def crate_directory(path: Path):
        """Utwórz foldery projektu, wraz z nadrzędnymi."""
        path.mkdir(parents=True, exist_ok=True)
 
    def _create_dir_structure(self, create_dir: Path, structure: dict):
        """Iteracyjne utwórz foldery projektu według skonfigurowanej strutury."""
        for folder, subfolders in structure.items():
            current_path = create_dir / folder
            self.crate_directory(current_path)
            if isinstance(subfolders, dict):
                self._create_dir_structure(current_path, subfolders)
                
    def create_project(self) -> ProjectFolder:
        """Utwórz foldery projektu."""
        self._create_dir_structure(
            create_dir=self.project.full_path,
            structure=self.project.directory_tree)
        return self.project



class Directories:
    
    @staticmethod
    def create(project: ProjectFolder) -> ProjectFolder:
        """Utwórz folder projektu."""
        info(f'Tworzenie folderu projektu: "{project.full_path.name}".')
        return _Structure(project).create_project()
    
    @staticmethod
    def delete(project: ProjectFolder):
        """Usuń foldery projektu, na wypadek błędu."""
        info(f'Usuwanie folderu projektu: "{project.full_path.name}".')
        _Structure(project).delete_project()
