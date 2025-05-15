from loguru import logger
from strawberry.types import Info

from inventory.model.entity.inventory import InventoryInput, InventoryType
from inventory.model.entity.reserved_item import ReserveInventoryItemInput
from inventory.service.inventory_write_service import InventoryWriteService
from inventory.tracing.decorators import traced


class InventoryMutationResolver:
    """GraphQL-Mutationsresolver für Inventory."""

    def __init__(self, write_service: InventoryWriteService):
        self.write_service = write_service

    @traced("create_inventory")
    async def create_inventory(
        self, info: Info, input: InventoryInput
    ) -> InventoryType:
        logger.debug("create_inventory: input={}", input)
        return await self.write_service.create(input)

    @traced("update_inventory")
    async def update_inventory(
        self, info: Info, inventory_id: str, input: InventoryInput
    ) -> InventoryType:
        logger.debug("update_inventory: id={}, input={}", inventory_id, input)
        return await self.write_service.update(inventory_id, input)

    @traced("delete_inventory")
    async def delete_inventory(self, info: Info, inventory_id: str) -> bool:
        logger.debug("delete_inventory: id={}", inventory_id)
        return await self.write_service.delete(inventory_id)

    @traced("reserve_inventory")
    async def reserve_inventory(
        self, info: Info, input: ReserveInventoryItemInput
    ) -> InventoryType:
        logger.debug("reserve_inventory: input={}", input)
        return await self.write_service.reserve(input)

    @traced("release_inventory")
    async def release_inventory(
        self, info: Info, input: ReserveInventoryItemInput
    ) -> InventoryType:
        logger.debug("release_inventory: input={}", input)
        return await self.write_service.release(input)
