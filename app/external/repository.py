
from svn.remote import RemoteClient
from svn.exception import SvnException
from dataclasses import dataclass
from typing import Iterator, Iterable
from pathlib import PurePosixPath
from app.product import Label
from .environment import Environment

@dataclass
class _Svn:
    """Repozytorium plików dokumentacji produktu."""
    url: str
    user: str
    password: str

    @classmethod
    def _read_config(cls) -> "_Svn":
        return cls(**Environment.variables("svn"))

    def _remote_client(self) -> RemoteClient:
        """Klient zdalnego repozytorium."""
        return RemoteClient(self.url, username=self.user, password=self.password)

    @classmethod
    def client(cls) -> RemoteClient:
        """Utwórz klienta zdalnego repozytorium."""
        return cls._read_config()._remote_client()


class RepositoryError(Exception):
    """Błąd repozytorium plików."""
    pass


def _svn_safe(func):
    """Wychwyć błąd repozytoprium wewnątrz funkcji."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SvnException as exc:
            raise RepositoryError(exc) from exc

    return wrapper


class Files(Iterable[PurePosixPath]):
    """Pliki z repozytorium."""
    remote: RemoteClient = _Svn.client()

    def __init__(self, source_folder: PurePosixPath):
        self._source = source_folder

    def __iter__(self) -> Iterator[PurePosixPath]:
        for name in self._directory_elements():
            path = self._source / name
            if path.suffix.casefold() == ".pdf":
                yield path

    @_svn_safe
    def _directory_elements(self) -> Iterator[str]:
        """Wymień elementy wewnątrz źródła."""
        return self.remote.list(rel_path=str(self._source))
    
    @_svn_safe
    @classmethod
    def download(cls, remote_path: PurePosixPath) -> bytes:
        """Pobierz wskazany element z repozytorium."""
        return cls.remote.cat(str(remote_path))

    @staticmethod
    def product_path(product: Label) -> PurePosixPath:
        return PurePosixPath(product.with_prefix)
    
