from pathlib import Path
from app.project import ProjectFolder, ErpProject
from app.external import FILESERVER


class ProjectFiles:
    """Foldery na dokumentację projektu na serwerze plikow."""

    main_dir: Path = FILESERVER.mount

    @staticmethod
    def _read_project_number(path: Path) -> str:
        """Numer projektu z początku nazwy folderu."""
        return path.name.split("_")[0]

    @classmethod
    def existing_folders(cls, subdirs: set[str]) -> set[str]:
        """Istniejące foldery projektów w zakresie lat pobranych projektów."""
        return {
            ProjectFiles._read_project_number(element)
            for directory in subdirs
            for element in (cls.main_dir / directory).glob("*/*")
            if ProjectFolder.is_project_folder(element)
        }

    def __init__(self, erp_projects: list[ErpProject], test: bool):
        """W normalnym trybie brane pod uwagę są jedynie projekty, dla których nie
        istnieją jeszcze foldery. Na potrzeby testu przetwarzane są wszystkie.
        """
        self._existing_numbers = self.existing_folders(
            subdirs=set(p.year for p in erp_projects)
        )
        self._erp_projects = (
            [p for p in erp_projects if p.number not in self._existing_numbers]
            if not test else erp_projects
        )

    def get(self) -> list[ProjectFolder]:
        """Pobrane projekty, które nie mają swojego folderu."""
        return [ProjectFolder(p) for p in self._erp_projects]
