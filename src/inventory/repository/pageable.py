"""Parameter für Pagination."""

from dataclasses import dataclass
from typing import Final

__all__ = ["MAX_PAGE_LIMIT", "Pageable"]

DEFAULT_LIMIT = 10
MAX_PAGE_LIMIT = 100
DEFAULT_SKIP = 0


@dataclass(eq=False, slots=True, kw_only=True)
class Pageable:
    """Datenklasse für Offset-basierte Paginierung mit skip + limit."""

    skip: int
    """Anzahl zu überspringender Datensätze (offset)."""

    limit: int
    """Maximale Anzahl von Datensätzen pro Seite."""

    @staticmethod
    def create(skip: int | None = None, limit: int | None = None) -> "Pageable":
        """Erzeugt ein `Pageable`-Objekt aus skip/limit-Werten.

        :param skip: Offset (wie viele Elemente sollen übersprungen werden)
        :param limit: Anzahl der Elemente, die zurückgegeben werden sollen
        :return: `Pageable`-Objekt
        """
        final_skip: Final = skip if skip is not None and skip >= 0 else DEFAULT_SKIP
        final_limit: Final = (
            DEFAULT_LIMIT
            if limit is None or limit > MAX_PAGE_LIMIT or limit < 1
            else limit
        )
        return Pageable(skip=final_skip, limit=final_limit)
