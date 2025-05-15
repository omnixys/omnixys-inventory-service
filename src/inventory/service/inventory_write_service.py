from typing import Final
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from inventory.model.entity.inventory import Inventory, InventoryInput, InventoryType
from inventory.model.entity.reserved_item import ReserveInventoryItemInput, Reserved_item
from inventory.repository.inventory_repository import InventoryRepository
from inventory.repository.reserved_item_repository import ReservedItemRepository
from inventory.error.exceptions import NotFoundError
from inventory.tracing.decorators import traced
from inventory.model.entity.inventory import map_inventory_to_inventory_type


class InventoryWriteService:
    """Service für Schreiboperationen auf Inventaren."""

    def __init__(
        self,
        session: AsyncSession,
        inventory_repo: InventoryRepository,
        reserved_item_repo: ReservedItemRepository,
    ):
        self._session = session
        self._inventory_repo = inventory_repo
        self._reserved_item_repo = reserved_item_repo

    @traced("create_inventory")
    async def create(self, input: InventoryInput) -> InventoryType:
        logger.debug("InventoryWriteService#create: input={}", input)

        inventory = Inventory.from_dict_primitive(input.__dict__)
        await self._inventory_repo.save(inventory)
        await self._session.commit()

        return map_inventory_to_inventory_type(inventory)

    @traced("update_inventory")
    async def update(self, inventory_id: str, input: InventoryInput) -> InventoryType:
        logger.debug(
            "InventoryWriteService#update: id={}, input={}", inventory_id, input
        )

        inventory = await self._inventory_repo.find_by_id_or_throw(inventory_id)
        updated_data = Inventory.from_dict_primitive(input.__dict__)
        inventory.set(updated_data)

        await self._inventory_repo.update(inventory)
        await self._session.commit()

        return map_inventory_to_inventory_type(inventory)

    @traced("delete_inventory")
    async def delete(self, inventory_id: str) -> bool:
        logger.debug("InventoryWriteService#delete: id={}", inventory_id)

        inventory = await self._inventory_repo.find_by_id_or_throw(inventory_id)
        await self._inventory_repo.delete(inventory)
        await self._session.commit()

        return True

    @traced("reserve_inventory")
    async def reserve(self, input: ReserveInventoryItemInput) -> InventoryType:
        logger.debug("InventoryWriteService#reserve: input={}", input)

        inventory = await self._inventory_repo.find_by_sku_or_throw(input.sku_code)

        if inventory.quantity < input.quantity:
            raise ValueError(f"Nicht genügend Bestand für SKU={input.sku_code}")

        inventory.quantity -= input.quantity

        reserved_item = Reserved_item(
            quantity=input.quantity,
            customer_id=input.customer_id,
            inventory=inventory,
            inventory_id=inventory.id,

        )

        await self._reserved_item_repo.save(reserved_item)
        await self._inventory_repo.update(inventory)
        await self._session.commit()

        return map_inventory_to_inventory_type(inventory)

    @traced("release_inventory")
    async def release(self, input: ReserveInventoryItemInput) -> InventoryType:
        logger.debug("InventoryWriteService#release: input={}", input)

        inventory = await self._inventory_repo.find_by_sku_or_throw(input.sku_code)

        reserved_item = await self._reserved_item_repo.find_by_composite_key_or_throw(
            sku_code=input.sku_code,
            customer_id=input.customer_id,
        )

        inventory.quantity += reserved_item.quantity

        await self._reserved_item_repo.delete(reserved_item)
        await self._inventory_repo.update(inventory)
        await self._session.commit()

        return map_inventory_to_inventory_type(inventory)
