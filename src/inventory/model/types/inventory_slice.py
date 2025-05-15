from typing import List

import strawberry
from inventory.model.entity.inventory import InventoryType


@strawberry.type
class InventorySlice:
    content: List[InventoryType]
    total: int
    page: int
    size: int
