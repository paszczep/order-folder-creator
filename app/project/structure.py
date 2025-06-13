from pathlib import Path, PurePosixPath
from yaml import safe_load
from app.product import Label
from .erp import ProjectGroup


class TreeConfig:
    """Skonfigurowane struktury folderów dla grup projektów."""
    _file = Path("config/structure.yaml")
    _structures: dict[ProjectGroup, dict] = safe_load(_file.read_text())

    @classmethod
    def project_structure(cls, group: ProjectGroup) -> dict:
        """Struktura folderów dla grupy projektu."""
        _s = cls._structures
        return _s.get(group, _s.get(ProjectGroup.INNE))

    @classmethod
    def product_location(cls, group: ProjectGroup, product: Label) -> PurePosixPath:
        """Skonfigurowana lokalizacja dokumentacji określonego produktu."""

        def _dfs(node: str | dict, parts: list[str]) -> PurePosixPath | None:
            if isinstance(node, dict):
                for k, v in node.items():
                    hit = _dfs(v, parts + [k])
                    if hit is not None:
                        return hit
            return PurePosixPath(*parts) if node == product else None

        tree = cls.project_structure(group)
        return _dfs(tree, [])
