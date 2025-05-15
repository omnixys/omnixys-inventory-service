from collections import defaultdict
from collections.abc import Mapping
import csv
from datetime import datetime
from pathlib import Path
import re
from typing import Final, List, Optional

from loguru import logger
from openpyxl import Workbook
from sqlalchemy.ext.asyncio import AsyncSession

from inventory.config import env, excel_enabled
from inventory.error.exceptions import NotFoundError
from inventory.model.entity.inventory import Inventory, InventoryType, map_inventory_to_inventory_type
from inventory.model.entity.reserved_item import ReserveInventoryItemType, Reserved_item
from inventory.repository.inventory_repository import InventoryRepository
from inventory.repository.reserved_item_repository import ReservedItemRepository
from inventory.repository.session import get_session
from inventory.repository.slice import Slice
from inventory.repository.pageable import Pageable
from inventory.config.feature_flags import excel_export_enabled  # z. B. True/False-Flag

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Border, Font, PatternFill, Side


class ReservedItemReadService:

    def __init__(self, repository: ReservedItemRepository, session: AsyncSession):
        self._repository = repository
        self._session = session

    async def find(
        self,
        customer_id: Optional[str] = None,
    ) -> list[ReserveInventoryItemType]:
        logger.debug("ReserveItemReadService.find_reserve_items: customer_id={}", customer_id)
        items: list[Reserved_item] = await self._repository.find_reserve_items(
            customer_id=customer_id,
        )

        if not items:
            raise NotFoundError("Keine reservierten Artikel gefunden.")

        return [self._map_to_type(item) for item in items]

    async def find_by_customer(
        self,
        customer_id: str,
    ) -> list[ReserveInventoryItemType]:
        logger.debug("ReserveItemReadService.find_by_customer: customer_id={}", customer_id)
        items: list[Reserved_item] = await self._repository.find_reserve_items(
            customer_id=customer_id,
        )

        if not items:
            raise NotFoundError(f"Keine reservierten Artikel für Kunde {customer_id} gefunden.")

        return [self._map_to_type(item) for item in items]

    def _map_to_type(self, item: Reserved_item) -> ReserveInventoryItemType:
        return ReserveInventoryItemType(
            id=item.id,
            version=item.version,
            customer_id=item.customer_id,
            quantity=item.quantity,
            inventory_id=item.inventory_id,
            created=item.created,
            updated=item.updated,
        )
