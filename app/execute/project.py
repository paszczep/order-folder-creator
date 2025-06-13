from datetime import timedelta
from app.project import ProjectFolder, ErpProject, ProjectGroup
from app.files import ProjectFiles


class NothingNew(Exception):
    """Baza danych nie zwróciła nowych projektów, albo wszystkie posiadają już
    swoje foldery."""

    pass


class NewProjects(list[ProjectFolder]):
    """Nowe projekty, bez folderów."""

    def __init__(self, timeframe: timedelta = timedelta(days=1), test: bool = False):
        super().__init__()
        if not (erp := ErpProject.from_database(timeframe=timeframe)):
            raise NothingNew("No new projects in database.")
        if not (projects := ProjectFiles(erp_projects=erp, test=test).get()):
            raise NothingNew("No new projects to create.")
        self += projects

    @property
    def project_numbers(self) -> list[str]:
        """Numery tworzonych projektów."""
        return [project.number for project in self]

    def group_project(self, group: ProjectGroup) -> ProjectFolder:
        """Na potrzeby testu - projekt który obejmuje wskazany produkt."""
        return {project for project in self if project.group == group}.pop()
