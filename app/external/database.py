from psycopg2 import connect, Error as Psycopg2Error
from typing import Literal
from pathlib import Path
from .environment import Environment


class DatabaseError(Exception):
    """Błąd bazy danych."""

    pass


def _db_safe(func):
    """Wychwyć błąd bazy danych wewnątrz funkcji."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Psycopg2Error as exc:
            raise DatabaseError(exc) from exc

    return wrapper


class Database:
    """Dostęp do bazy danych."""

    _db_keys: dict = Environment.variables("postgres")

    def __init__(self, object: Literal["products", "projects"]):
        """Zaczytaj kwerendę właściwą obiektowi."""
        file = Path(f"app/sql/{object}.sql")
        self._query: str = file.read_text()

    def query(self, **kwargs: dict[str, str]) -> "Database":
        """Uzupełnij kwerendę o argumenty."""
        for placeholder, value in kwargs.items():
            self._query = self._query.replace(f":{placeholder}", value)
        return self

    @_db_safe
    def get_values(self, keys: bool) -> list[dict] | list:
        """Pobierz wartości z bazy danych, z kluczami lub bez."""
        with connect(**self._db_keys) as connection:
            with connection.cursor() as cursor:
                cursor.execute(self._query)
                values = list(cursor.fetchall())
                if keys:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in values]
                else:
                    return values
