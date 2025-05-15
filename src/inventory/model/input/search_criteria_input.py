from typing import Optional
from pydantic import BaseModel
import strawberry

from inventory.model.enum.inventory_status_type import InventoryStatusType


@strawberry.input
class InventorySearchCriteriaInput:
    sku_code: str | None = None
    product_id: str | None = None
    status: InventoryStatusType | None = None


class InventorySearchCriteria(BaseModel):
    """DTO für Inventarsuche per Service, Repository oder API."""

    sku_code: Optional[str] = None
    product_id: Optional[str] = None
    status: Optional[InventoryStatusType] = None
