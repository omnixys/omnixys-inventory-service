from typing import Final, List

import strawberry
from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.federation import Schema

from inventory.config.graphql import graphql_ide
from inventory.graphql_api.graphql_types import InventorySearchCriteria
from inventory.model.entity.inventory import InventoryType
from inventory.resolver.inventory_query_resolver import (
    resolve_inventories,
    resolve_inventory,
)
from inventory.security.keycloak_service import KeycloakService


async def get_context(request: Request) -> dict:
    return {
        "request": request,
        # "keycloak": KeycloakService(request),
        "keycloak": request.state.keycloak,  # ✅ statt KeycloakService(request)
    }


@strawberry.type
class Query:

    @strawberry.field
    async def inventory(
        self,
        inventory_id: strawberry.ID,
        info: strawberry.types.Info = None,
    ) -> InventoryType | None:
        return await resolve_inventory(info=info, inventory_id=inventory_id)

    @strawberry.field
    async def inventories(
        self,
        suchkriterien: InventorySearchCriteria | None = None,
        info: strawberry.types.Info = None,
    ) -> List[InventoryType]:
        return await resolve_inventories(suchkriterien=suchkriterien, info=info)


schema = Schema(
    query=Query,
    enable_federation_2=True,
)

graphql_router: Final = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)
