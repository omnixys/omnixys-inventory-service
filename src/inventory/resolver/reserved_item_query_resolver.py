from fastapi import Depends, HTTPException
from graphql import GraphQLError
from loguru import logger
import strawberry
from strawberry.types import Info
from typing import Final, Optional
from inventory.error.exceptions import NotFoundError
from inventory.model.entity.inventory import InventoryType
from inventory.model.entity.reserved_item import ReserveInventoryItemType
from inventory.model.input.search_criteria_input import InventorySearchCriteriaInput
from inventory.security.keycloak_service import KeycloakService
from inventory.service.inventory_read_service import InventoryReadService
from inventory.repository.pageable import Pageable
from inventory.service.reserved_item_read_service import ReservedItemReadService
from inventory.tracing.decorators import traced
from inventory.client.product.product_service import get_product_by_id


@strawberry.type
class ReservedItemQueryResolver:
    """Resolver für GraphQL-Queries zum Abrufen von Inventaren."""

    def __init__(self, read_service: ReservedItemReadService):
        self.read_service = read_service

    @traced("resolve_reserve_items")
    async def resolve_reserve_items(
        self, customer_id: Optional[str]
    ) -> list[ReserveInventoryItemType]:
        logger.debug("resolve_reserve_items: customerId={}", customer_id)

        try:
            items = await self.read_service.find(
                customer_id,
            )
        except NotFoundError:
            logger.info("Keine Reservierten Produkte gefunden zum Kunden: {}", customer_id)
            return []

        logger.debug("resolve_reserve_items: found=%{}", len(items))
        return items

    @traced("resolve_reserve_items_by_customer")
    async def resolve_reserve_items_by_customer(
        self, customer_id: Optional[str]
    ) -> list[ReserveInventoryItemType]:
        logger.debug("resolve_reserve_items: customerId={}", customer_id)

        try:
            items = await self.read_service.find_by_customer(customer_id)
        except NotFoundError:
            logger.info(
                "Keine Reservierten Produkte gefunden mit customerId: {}",customer_id
            )
            return []

        logger.debug("resolve_reserve_items: found=%{}", len(items))
        return items
