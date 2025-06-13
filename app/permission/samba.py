import subprocess
from dataclasses import dataclass
from logging import info
from app.external import FILESERVER
from app.project import ProjectFolder
from .security import Security
from .create import Settings
from .settings import Project


class PermissionError(Exception):
    """Błąd nadawania uprawnień."""
    pass

@dataclass(init=False)
class _Samba:
    """Wywołanie programu smbcacls.
    
    Atrybuty:
        server      - serwer plików,
        directory   - ścieżka do zasobu,
        user_values - klucze użytkownika,
        option      - dodaj/usuń ustawienie,
        acl_entry   - ustawienie dopuszczenia.
    
    """
    
    server: str
    directory: str
    user_values: str 
    acl_entry: str
    option: str
        
    def __init__(self, setting: Security):
        srvr = FILESERVER
        self.server = srvr.url
        self.directory = str(srvr.folder / setting.path.relative_to(srvr.mount))
        self.user_values = f"{srvr.domain}\\{srvr.user}%{srvr.password}"
        permission = f'{setting.allowed}/{setting.inherit}/{setting.permission}'
        self.option = setting.option
        self.acl_entry = f"{srvr.domain}\\{setting.group}:{permission}"
    
    @property
    def _command(self) -> list[str]:
        r"""Komenda:
        `
            smbcacls //server/share "path/in/share" \
            --user "DomainName\adminuser%password" \
            --add "ACL:DomainName\GroupName:ALLOWED|DENIED/OI|CI|READ"
        `
        """
        return[
            'smbcacls', self.server, self.directory,
            '--user', self.user_values,
            f'--{self.option}', f'ACL:{self.acl_entry}',
            # '--test-args',
            # '--debuglevel=2'
            ]
                
    def run(self):
        result = subprocess.run(self._command, text=True, capture_output=True)
        match result.returncode:
            case 0:
                if (output := result.stdout):
                    info(f'{output}')
                pass
            case 1:
                raise PermissionError(f"Fileserver error {result.stderr}")
            case 2:
                raise PermissionError(f"Argument error {result.stderr}")
            case _:
                raise PermissionError(f"Unknown error {result.stderr}")


class Permissions:
    """Ustawienia dopuszczeń do folderu projektu."""
    def __init__(self, project: ProjectFolder):
        project = Project(project.full_path)
        self.all_settings: list[Security] = Settings(project)
    
    def give(self):
        for setting in self.all_settings:
            _Samba(setting).run()
        info(f'Ustawienia dostępu: {len(self.all_settings)}.')
