from dataclasses import dataclass
from logging import info
from app.external import Database
from app.product import Product, Label


@dataclass
class _Project:
    """Projekt i jego produkty."""

    project_number: str
    products: list[Product]


class ProjectsProducts(list[_Project]):

    def _fetch_from_database(self, project_numbers: list[str]) -> list[_Project]:
        """Pobierz z bazy danych produkty należące do wskazanych projektów."""
        info(f"fetching products belonging to {len(project_numbers)} project(s).")
        db = Database("products").query(
            product_labels=Label.values_for_sql_query(),
            project_numbers=", ".join([f"'{p}'" for p in project_numbers]),
            product_prefix=Label.product_prefix(),
        )
        return [
            _Project(project_number=project, products=Product.parse(products))
            for project, products in db.get_values(keys=False)
        ]

    def __init__(self, project_numbers: list[str]):
        super().__init__()
        self += self._fetch_from_database(project_numbers)

    def project_products(self, project_number: str) -> list[Product]:
        """Produkty należące do wskazanego projektu."""
        return [
            product
            for project in self
            for product in project.products
            if project.project_number == project_number
        ]

    def product_project(self, label: Label) -> str:
        """Na potrzeby testu - projekt który obejmuje wskazany produkt."""
        return {
            project.project_number
            for project in self
            if any(product.label == label for product in project.products)
        }.pop()
