from typing import Final, List

import strawberry
from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.federation import Schema

from inventory.config.graphql import graphql_ide
from inventory.graphql.mutation import Mutation
from inventory.graphql.query import Query
from inventory.repository.inventory_repository import InventoryRepository
from inventory.repository.session import AsyncSessionFactory
from inventory.resolver.inventory_query_resolver import InventoryQueryResolver
from inventory.security.keycloak_service import KeycloakService
from inventory.service.inventory_read_service import InventoryReadService


# async def get_context(request: Request) -> dict:
#     return {
#         "request": request,
#         "keycloak": getattr(request.state, "keycloak", None),
#     }


async def get_context(request: Request) -> dict:
    session = AsyncSessionFactory()
    repo = InventoryRepository(session)
    service = InventoryReadService(repo, session)
    resolver = InventoryQueryResolver(service)

    return {
        "session": session,
        "resolver": resolver,
        "keycloak": getattr(request.state, "keycloak", None),
    }


# ---------------------------
# Schema + Router
# ---------------------------
schema = Schema(
    query=Query,
    mutation=Mutation,
    enable_federation_2=True,
)

graphql_router: Final = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)
