from os import environ
from typing import Literal
from enum import StrEnum, auto
from functools import cached_property


class Environment:
    @staticmethod
    def variables(scope: Literal["postgres", "fileserver", "svn"]) -> dict:
        """Zaczytaj zmienne środowiskowe z określonym przedroskiem."""
        return {
            key.split("_")[1]: value
            for key, value in environ.items()
            if key.startswith(scope)
        }

class AppMode(StrEnum):
    """Tryb działania aplikacji. Test albo nie."""
    PROD = auto()
    TEST = auto()
    
    @classmethod
    def read_mode(cls) -> "AppMode":
        return cls(environ.get('APP_MODE'))
    
    @cached_property
    def is_test(self) -> bool:
        return True if self is AppMode.TEST else False
    
    def consider_test_dir(self, value: str) -> str:
        return (value if not self.is_test else AppMode.TEST)
    
APP_MODE = AppMode.read_mode()
