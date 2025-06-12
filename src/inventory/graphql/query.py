from typing import Final
from loguru import logger
import strawberry
from inventory.dependency_provider import provide_inventory_query_resolver, provide_reserved_item_query_resolver
from inventory.error.authentication_error import AuthenticationError
from inventory.model.entity.inventory import InventoryType
from inventory.model.entity.reserved_item import ReserveInventoryItemType
from inventory.model.input.pagination import PaginationInput
from inventory.model.input.search_criteria_input import InventorySearchCriteria, InventorySearchCriteriaInput
from inventory.model.types.inventory_slice import InventorySlice
from inventory.repository.pageable import Pageable
from inventory.security.keycloak_service import KeycloakService

# ---------------------------
# GraphQL Query Definition
# ---------------------------
@strawberry.type
class Query:
    @strawberry.field
    async def inventory(
        self,
        info: strawberry.Info,
        inventory_id: strawberry.ID,
    ) -> InventoryType | None:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        resolver = await provide_inventory_query_resolver()
        return await resolver.resolve_inventory(inventory_id=str(inventory_id), token=keycloak.token)

    @strawberry.field
    async def inventorys(
        self,
        pagination: PaginationInput | None = None,
        search_criteria: InventorySearchCriteriaInput | None = None,
        info: strawberry.types.Info = None,
    ) -> InventorySlice:
        """Inventare anhand von Suchkriterien suchen.

        :param suchkriterien: sku_code, name usw.
        :return: Die gefundenen Inventare
        :rtype: list[Inventory]
        :raises NotFoundError: Falls kein Inventar gefunden wurde, wird zu GraphQLError
        """

        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        such_dict: Final = dict(vars(search_criteria)) if search_criteria else {}
        filtered = {k: v for k, v in such_dict.items() if v}

        if pagination is None:
            pagination = PaginationInput(skip=0, limit=10)
        pageable = Pageable.create(skip=pagination.skip, limit=pagination.limit)

        # 💡 SearchCriteriaInput → SearchCriteria (DTO) umwandeln
        criteria = (
            InventorySearchCriteria(**search_criteria.__dict__)
            if search_criteria is not None
            else None
        )

        resolver = await provide_inventory_query_resolver()
        inventorys = await resolver.resolve_inventorys(
            info=info,
            pageable=pageable,
            search_criteria=criteria,
        )

        return InventorySlice(
            content=inventorys.content,
            total=inventorys.total,
            page=pageable.skip,
            size=pageable.limit,
        )

    @strawberry.field
    async def get_reserve_items_by_customer(
        self, info: strawberry.Info, customer_id: str | None = None
    ) -> list[ReserveInventoryItemType]:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User", "Supreme"])

        resolver = await provide_reserved_item_query_resolver()
        items = await resolver.resolve_reserve_items_by_customer(customer_id=customer_id)
        return items

    @strawberry.field
    async def get_reserve_items(
        self,
        info: strawberry.Info,
        customer_id: str | None = None,
    ) -> list[ReserveInventoryItemType]:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        resolver = await provide_reserved_item_query_resolver()
        items = await resolver.resolve_reserve_items_by_customer(customer_id=customer_id)
        return items
