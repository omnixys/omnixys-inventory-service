from collections.abc import Mapping
from typing import Final, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from inventory.error.exceptions import NotFoundError
from inventory.model.entity.inventory import Inventory
from inventory.repository.pageable import Pageable
from inventory.repository.slice import Slice


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session: Final = session

    async def find_by_id(self, inventory_id: str) -> Inventory | None:
        stmt = select(Inventory).where(Inventory.id == inventory_id)
        return await self.session.scalar(stmt)

    async def find_by_id_or_throw(self, inventory_id: str) -> Inventory:
        inventory = await self.find_by_id(inventory_id)
        if inventory is None:
            raise NotFoundError(f"Inventory-ID nicht gefunden: {inventory_id}")
        return inventory

    async def find_by_sku_or_throw(self, sku_code: str) -> Inventory:
        stmt = select(Inventory).where(Inventory.sku_code == sku_code)
        inventory = await self.session.scalar(stmt)
        if inventory is None:
            raise NotFoundError(f"SKU nicht gefunden: {sku_code}")
        return inventory

    async def find(
        self,
        filter_dict: dict[str, str] | None = None,
        pageable: Pageable | None = None,
    ) -> List[Inventory]:
        if pageable is None:
            pageable = Pageable.create()

        offset = pageable.skip
        limit = pageable.limit

        stmt = select(Inventory)

        if filter_dict:
            for attr, value in filter_dict.items():
                if hasattr(Inventory, attr):
                    stmt = stmt.where(getattr(Inventory, attr) == value)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.scalars(stmt)
        content = result.all()

        # Zähle die Gesamtmenge separat
        count_stmt = select(func.count()).select_from(Inventory)
        if filter_dict:
            for attr, value in filter_dict.items():
                if hasattr(Inventory, attr):
                    count_stmt = count_stmt.where(getattr(Inventory, attr) == value)

        return content

    async def _count(self) -> int:
        stmt = select(func.count()).select_from(Inventory)
        return await self.session.scalar(stmt) or 0

    async def _find_by_sku_code(self, sku_code: str) -> Inventory | None:
        stmt = select(Inventory).where(Inventory.sku_code == sku_code)
        return await self.session.scalar(stmt)

    async def _find_by_product_id(
        self, pid: str, pageable: Pageable
    ) -> Slice[Inventory]:
        offset = pageable.number * pageable.size
        filter_stmt = Inventory.product_id.ilike(f"%{pid}%")

        stmt = (
            select(Inventory)
            .where(filter_stmt)
            .limit(pageable.size)
            .offset(offset)
            if pageable.size
            else select(Inventory).where(filter_stmt)
        )

        result = await self.session.scalars(stmt)
        return Slice(result.all(), await self._count())

    async def save(self, inventory: Inventory) -> Inventory:
        self.session.add(inventory)
        await self.session.flush()
        return inventory

    async def update(self, inventory: Inventory) -> Inventory | None:
        existing = await self.find_by_id(inventory.id)
        if not existing:
            return None
        existing.set(inventory)
        return existing

    async def delete_by_id(self, inventory_id: str) -> None:
        inventory = self.find_by_id(inventory_id)
        if inventory:
            self.session.delete(inventory)

    async def _count(self) -> int:
        stmt = select(func.count()).select_from(Inventory)
        return self.session.scalar(stmt) or 0
