"""Ausschnitt an gefundenen Daten mit Paginierungsinformationen."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar, Generic

__all__ = ["Slice"]

T = TypeVar("T")


@dataclass(eq=False, slots=True, kw_only=True)
class Slice(Generic[T]):
    """Generische Datenklasse für Paginierungsergebnisse."""

    content: Sequence[T]
    """Teilausschnitt der gefundenen Datensätze."""

    total: int
    """Gesamtanzahl der gefundenen Datensätze (für Paging-Anzeige)."""

    page: int
    """Aktuelle Seite (beginnend bei 0)."""

    size: int
    """Anzahl von Elementen pro Seite."""
