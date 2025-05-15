"""Entity-Klasse für Reserved_item."""

from datetime import datetime
from typing import Any, Literal, Self
import uuid

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import strawberry

from inventory.model.entity.base import Base


@strawberry.input
class ReserveInventoryItemInput:
    sku_code: str
    quantity: int
    customer_id: str


@strawberry.type
class ReserveInventoryItemType:
    id: str | None
    version: int
    quantity: int
    customer_id: str
    inventory_id: str
    created: datetime
    updated: datetime


class Reserved_item(Base):
    """Entity-Klasse für einen reservierten Artikel (Reserved_item) im Lagerbestand."""

    __tablename__ = "reserved_item"

    quantity: Mapped[int]
    """Anzahl reservierter Artikel."""

    customer_id: Mapped[str | None]
    """ID des Kunden, der mit der Reservierung verknüpft ist."""

    inventory_id: Mapped[str] = mapped_column(ForeignKey("inventory.id"))
    """ID des zugehörigen Inventars (Fremdschlüssel auf Tabelle `inventory`)."""

    inventory: Mapped["Inventory"] = relationship(  # noqa: F821
        back_populates="reserved_items",
    )
    """Beziehung zum zugehörigen `Inventory`-Objekt (N:1)."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
    )

    """Eindeutige ID des reservierten Artikels (UUID, automatisch generiert)."""

    version: Mapped[int] = mapped_column(nullable=False, default=1)
    """Versionsnummer zur Unterstützung von Optimistic Locking."""

    created: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        default=None,
    )
    """Zeitstempel bei Erstellung des Datensatzes."""

    updated: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
        default=None,
    )
    """Zeitstempel bei letzter Aktualisierung des Datensatzes."""

    @classmethod
    def from_dict(
        cls,
        reserved_item_dict: dict[Literal["quantity", "customer_id"], Any],
    ) -> Self:
        """Erstelle ein `Reserved_item`-Objekt aus einem Dictionary.

        :param reserved_item_dict: Dictionary mit Werten für `quantity`,  `customer_id`
        :return: Neues `Reserved_item`-Objekt
        """
        return cls(
            id=None,
            quantity=reserved_item_dict["quantity"],
            customer_id=reserved_item_dict["customer_id"],
            inventory_id=None,
            inventory=None,
            created=None,
            updated=None,
        )

    def __repr__(self) -> str:
        """Gibt eine technische String-Repräsentation des Objekts zurück (nur für Entwickler:innen)."""
        return (
            f"Reserved_item(id={self.id}, version={self.version}, "
            f"quantity={self.quantity}, customer_id={self.customer_id},"
            f"created={self.created}, updated={self.updated})"
        )
