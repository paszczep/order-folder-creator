from typing import Literal
from logging import info
from .security import Security
from .settings import Implied, Project


        
        
class Settings(list[Security]):
    """Lista ustawień uprawnień dla projektu."""
    def _permission_holders(
            self, 
            permission: Literal['FULL', 'READ', 'CHANGE', 'D']
        ) -> list[str]:
        """Beneficjenci określonego uprawnienia."""
        return [_s.group for _s in self if _s.permission == permission]
        
    def _hardcoded_settings(self) -> list[Implied]:
        """Wartości na potrzeby zaimplikowanych uprawnień."""
        return Implied.settings(
            readers=self._permission_holders('READ'),
            changers=self._permission_holders('CHANGE'),
            project=self._project)
        
    def _create_implied(self):
        """Utwórz zaimplikowane uprawnienia."""
        for setting in self._hardcoded_settings():
            self += Security.implied(setting)
        
    def _create_configured(self):
        """Utwórz skonfigurowane uprawnienia."""
        for docs_folder in self._project.docs_groups:
            self += Security.configured(docs_folder)
    
    def __init__(self, project: Project):
        super().__init__()
        self._project: Project = project
        self._create_configured()
        self._create_implied()
        
        self._log()
        
    def _log(self):
        info(f'permission settings: {len(self)}')
        for _p in ['FULL', 'READ', 'CHANGE', 'D']:
            _perm = _p.lower() if not _p == 'D' else 'delete'
            _holders = self._permission_holders(_p)
            info(f'\t{_perm}: {len(_holders)}')
            