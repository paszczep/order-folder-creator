from sys import exit
from logging import info
from app.project import ProjectFolder
from app.product import Product, ProjectsProducts
from app.permission import Permissions
from app.files import Directories, DirectoryError, Documents
from app.external import RepositoryError
from .project import NewProjects, NothingNew


class ExecuteError(Exception):
    """Błąd zbiorczy procesu."""

    pass


class Execute:
    """Pobierz projekty, właściwe im produkty, zapisz i udostępnij."""

    @staticmethod
    def new_projects() -> NewProjects:
        """Pobierz nowe, nieudokumentowane projekty."""
        try:
            return NewProjects()
        except NothingNew as e:
            info(e)
            exit(0)

    @staticmethod
    def create_project(folder: ProjectFolder, products: list[Product]):
        """Utwóż folder projektu, nadaj uprawnienia, zapisz pliki produktów."""
        info(f'Tworzenie projektu: {folder.number}.')
        try:
            Directories.create(folder)
            Permissions(folder).give()
            Documents.save(
                products=products,
                project_folder=folder,
            )
        except (DirectoryError, PermissionError, RepositoryError) as err:
            Directories.delete(folder)
            raise ExecuteError from err

    def __init__(self):
        """Wykonaj program."""
        projects: NewProjects = self.new_projects()
        all_products = ProjectsProducts(project_numbers=projects.project_numbers)
        for project in projects:
            self.create_project(
                folder=project,
                products=all_products.project_products(project.number),
            )
