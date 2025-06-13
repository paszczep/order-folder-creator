from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from .environment import Environment, AppMode


@dataclass
class _Fileserver:
    """Sieciowy serwer plików."""
    domain: str
    user: str
    password: str
    url: str
    folder: PurePosixPath
    mount: Path

    def __post_init__(self):
        self.folder = PurePosixPath(self.folder)
        self.mount = Path(self.mount)

    @classmethod
    def read_config(cls) -> "_Fileserver":
        return cls(**Environment.variables("fileserver"))
    
    @property
    def test_directory(self) -> Path:
        return self.mount / AppMode.TEST


FILESERVER = _Fileserver.read_config()
