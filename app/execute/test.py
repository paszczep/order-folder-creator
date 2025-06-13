from unittest import TestCase, skip
from datetime import timedelta, date
from logging import getLogger, INFO, info, StreamHandler
from sys import stderr
from shutil import rmtree
from pathlib import PurePosixPath, Path
from functools import cache
from app.project import ProjectFolder, ProjectGroup
from app.product import ProjectsProducts, Product, Label
from app.files import ProjectFiles, Directories
from app.document import DocsConfig
from app.external import Files, FILESERVER
from .project import NewProjects, NothingNew
from .execute import Execute


logger = getLogger()
logger.setLevel(INFO)
logger.addHandler(StreamHandler(stderr))


class _Data:
    ALL_TIME = timedelta(days=365)
    
    @staticmethod 
    @cache
    def projects(timeframe: timedelta = ALL_TIME) -> NewProjects:
        return NewProjects(timeframe=timeframe, test=True)
    
    @staticmethod
    @cache
    def products() -> ProjectsProducts:
        projects = _Data.projects()
        return ProjectsProducts(project_numbers=projects.project_numbers)
    
    @staticmethod
    def product_indexes() -> list[Product]:
        all_products = _Data.products()
        return [p for proj in all_products for p in proj.products]


@skip("temporarily disabled")
class TestData(TestCase):

    def test_no_projects(self):
        """Jeśli nie ma nowych projektów, program zatrzymuje działanie."""
        with self.assertRaises(NothingNew):
            _Data.projects(timeframe=timedelta(days=-1))
    
    def test_projects(self):
        
        all_projects = _Data.projects()
        """Test pobierania projektów."""
        info(f'Wszystkie projekty: {len(all_projects)}.')
        self.assertGreater(len(all_projects), 0)
        for project in all_projects:
            with self.subTest(project=project.number):
                self.assertIsInstance(project, ProjectFolder)
            
    def test_products(self):
        """Test pobierania produktów."""
        all_products = _Data.product_indexes()
        info(f'Wszystkie produkty: {len(all_products)}.')
        self.assertGreater(len(all_products), 0)
        for product in all_products:
            with self.subTest(product=product):
                self.assertIsInstance(product, Product)


class _Folders:
    @staticmethod
    @cache
    def existing() -> set[str]:
        """Foldery projektów w skonfigurowanej lokalizacji."""
        subdirs = [str(date.today().year - delta) for delta in (1, 0)]
        info(f'Pod-foldery na projekty: {', '.join(subdirs)}.')
        return ProjectFiles.existing_folders(
            subdirs=set(subdirs))

    @staticmethod
    def is_empty(folder: Path) -> bool:
        """Czy wskazany folder zawiera tylko i wyłącznie inne foldery?"""
        contents = [el for el in folder.rglob('*') if not el.is_dir()]
        return not any(contents)
    
    @staticmethod
    def contains_files(folder: Path) -> bool:
        """Czy wskazany folder zawiera pliki PDF?"""
        contents = [
            el for el in folder.rglob('*') if el.suffix.casefold() == ".pdf"
            ]
        return any(contents)
    
    @staticmethod
    def delete_test_directory():
        """Usuwanie testowej lokalizacji na foldery projektu."""
        test_dir = FILESERVER.test_directory
        if _Folders.is_empty(test_dir):
            rmtree(test_dir)
    

@skip("temporarily disabled")
class TestServer(TestCase):
    """Test folderu głównego na projekty."""
    
    def test_mount(self):
        self.assertTrue(FILESERVER.mount.is_dir())
    
    def test_folders(self):
        existing = _Folders.existing()
        info(f'Istniejące foldery: {len(existing)}.')
        self.assertGreater(len(existing), 0, "Nie znaleziono folderów projektu.")
        
    def test_projects(self):
        existing = _Folders.existing()
        projects = _Data.projects(timeframe=timedelta(days=365))
        info(f'Projekty w bazie danych: {(erp := len(projects))}.')
        missing = {p.number for p in projects} - existing
        if missing:
            preview = ", ".join(sorted(missing)[:5])
            more = " …" if len(missing) > 5 else ""
            self.fail(
                f"Brakuje {len(missing)} folderów z {erp} projektów: {preview}{more}"
            )


@skip("temporarily disabled")
class TestSvn(TestCase):
    config = DocsConfig()
    
    def test_config(self):
        """Obecność produktów w pliku konfiguracyjnym."""
        self.assertEqual(set(self.config.keys()), Label.values(), 'Niewłaściwe nazwy produktów.')
        
    def product_paths(self, product: Label) -> list[PurePosixPath]:
        """Ścieżki dostępu do dokumenacji, dla grupy produktowej."""
        base = Files.product_path(product)
        return [base / path for path in 
                self.config.product_paths(product=product)]
        
    def test_paths(self):
        """Test repozytoriów dokumentacji."""
        for product in Label:
            paths = self.product_paths(product)
            for path in paths:
                files = [f for f in Files(path)]
                with self.subTest(product=product, path=str(path)):
                    self.assertGreater(len(files), 0, 'Repozytorium powinno zawierać pliki.')

class _Projects:
    projects: NewProjects = _Data.projects()
    products: ProjectsProducts = _Data.products()
    @classmethod
    def product_projects(cls) -> set[str]:
        """Numery projektów obejmujących produkty."""
        return {
            cls.products.product_project(label) for label in Label
        }
        
    @classmethod
    def group_token(cls) -> set[ProjectFolder]:
        """Projekt dla każdej grupy projektów."""
        return {
            cls.projects.group_project(group) for group in ProjectGroup
            }
    
    @classmethod
    def product_token(cls) -> set[ProjectFolder]:
        """Projekty obejmujące produkty."""
        return {
            p for p in cls.projects if p.number in cls.product_projects()
        }
        
    @classmethod
    def project_products(cls, project_number: str) -> list[Product]:
        """Produkty należące do projektu."""
        return cls.products.project_products(project_number)


# @skip("temporarily disabled")
class TestExecute(TestCase):
    """Tworzenie projektów obejmujących każdą z grup produktowych i projektowych."""
    @classmethod
    def setUp(cls):
        cls.product = _Projects.product_token()
        cls.group = _Projects.group_token()
        cls.projects = cls.product | cls.group
    
    def test_app(self):
        for project in self.projects:
            Execute.create_project(
                folder=project,
                products=_Projects.project_products(project.number)
            )
            with self.subTest(project=project):
                project_path = project.full_path
                
                self.assertTrue(
                    project_path.is_dir(), 
                    'Folder projektu nie został utworzony.')
                
                if project in self.product:
                    self.assertTrue(
                        _Folders.contains_files(project_path), 
                        'Pliki nie zostały zapisane.')
                
    @classmethod
    def tearDownClass(cls):
        for project in cls.projects:
            Directories.delete(project=project)
        _Folders.delete_test_directory()
        