from pathlib import PurePosixPath, Path
from dataclasses import dataclass, field
from logging import info
from functools import cached_property
from typing import Iterable
from app.project import ProjectFolder, TreeConfig
from app.document import Selection, Gauge
from app.product import Product
from app.external import Files
from .directories import DirectoryError, directory_safe


@dataclass
class Documents:
    """Pliki produktu wewnątrz projektu."""
    product: Product
    project: ProjectFolder
    documents: Selection = field(init=False)
    
    @cached_property
    def folder_name(self) -> str:
        """Nazwa folderu produktu to jego nazwa handlowa, oraz ewentualne 
        oznaczenie wielkości i elementy symbolu pozytywnie określające źródło dokumentów.
        """
        name_elements = [self.product.label.with_prefix]
        if self.product.size:
            name_elements.append(Gauge.size_key(self.product))
        if self.documents.flags:
            name_elements += self.documents.flags
        return '-'.join(name_elements)
    
    @property
    def relative_path(self) -> PurePosixPath:
        """Skonfigurowana względna ścieżka folderu produktu."""
        return TreeConfig.product_location(
            group=self.project.group,
            product=self.product.label)
        
    @property
    def product_folder(self) -> Path:
        """Pełna ścieżka folderu produktu."""
        return self.project.full_path / self.relative_path / self.folder_name
    
    @directory_safe
    def save_product(self, files: Iterable[PurePosixPath]):
        """"Pobierz i zapisz pliki produktu."""
        count = 0
        for file in files:
            file_path = self.product_folder / file.name
            file_data = Files.download(file)
            file_path.write_bytes(file_data)
            count += 1
            
        info(f'Zapisano {count} plik(i).')
            
    def __post_init__(self):
        """Utwórz nieistniejący folder produktu, zapisz jego pliki."""
        self.documents = Selection(self.product)
        info(f'Zapisywanie produktu: {self.folder_name}.')
        try:
            self.product_folder.mkdir()
        except FileExistsError:
            info('Folder już istnieje.')
            pass
        except OSError as ex:
            raise DirectoryError from ex
        else:
            self.save_product(self.documents.entries)
                
    @classmethod
    def save(cls, products: list[Product], project_folder: ProjectFolder):
        """Foldery produktów projektu."""
        info(f'Produkty projektu {project_folder.number}: {len(products)}')
        return [cls(product, project_folder) for product in products]
        
