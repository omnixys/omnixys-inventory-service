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
from inventory.tracing.decorators import traced
from inventory.service.product_service import get_product_by_id


@strawberry.type
class InventoryQueryResolver:
    """Resolver für GraphQL-Queries zum Abrufen von Inventaren."""

    def __init__(self, read_service: InventoryReadService):
        self.read_service = read_service

    @traced("resolve_inventory")
    async def resolve_inventory(
        self,
        info: Info,
        inventory_id: str,
    ) -> InventoryType | None:
        logger.debug("resolve_inventory: inventory_id={}", inventory_id)

        try:
            inventory = await self.read_service.find_by_id(inventory_id)
            # try:
            #     product = await get_product_by_id(inventory.product_id, keycloak.token)
            #     inventory.product_name = product.get("name", "Unbekannt")
            # except Exception as e:
            #     logger.warning("Produktservice nicht erreichbar: {}", e)
            #     inventory.product_name = "Unbekannt"

            return inventory
        except NotFoundError:
            logger.warning("Kein Produkt gefunden für ID: {}", inventory_id)
            return None

    @traced("resolve_inventory")
    async def resolve_inventorys(
        self,
        info: Info,
        pageable: Pageable,
        search_criteria: InventorySearchCriteriaInput | None = None,
    ) -> list[InventoryType]:
        logger.debug("resolve_inventorys: search_criteria={}", search_criteria)

        # Filter leere Felder heraus
        criteria_dict: Final = dict(vars(search_criteria)) if search_criteria else {}
        filtered: Final = {key: val for key, val in criteria_dict.items() if val}

        try:
            result_slice = await self.read_service.find(
                filter=filtered,
                pageable=pageable
                )
        except NotFoundError:
            logger.info("Keine Produkte gefunden mit Kriterien: {}", filtered)
            return []

        logger.debug("resolve_inventorys: found=%{}", len(result_slice.content))
        return result_slice
