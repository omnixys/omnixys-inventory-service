# inventory/di/dependency_provider_async.py

from contextlib import asynccontextmanager

from inventory.repository.session import get_session
from inventory.repository.inventory_repository import InventoryRepository
from inventory.repository.reserved_item_repository import ReservedItemRepository
from inventory.resolver.inventory_mutation_resolver import InventoryMutationResolver
from inventory.resolver.inventory_query_resolver import InventoryQueryResolver
from inventory.resolver.reserved_item_query_resolver import ReservedItemQueryResolver
from inventory.service.inventory_read_service import InventoryReadService
from inventory.service.inventory_write_service import InventoryWriteService
from sqlalchemy.ext.asyncio import AsyncSession

from inventory.service.reserved_item_read_service import ReservedItemReadService


# 🔄 Gemeinsame Session + Repositories
@asynccontextmanager
async def provide_repositories(session: AsyncSession):
    inventory_repo = InventoryRepository(session)
    reserved_repo = ReservedItemRepository(session)
    yield inventory_repo, reserved_repo


# 🔍 Query-Service (nur lesen)
@asynccontextmanager
async def provide_inventory_read_service(session: AsyncSession):
    async with session:
        async with provide_repositories(session) as (inventory_repo, _):
            yield InventoryReadService(inventory_repo, session=session)


@asynccontextmanager
async def provide_reserved_item_read_service(session: AsyncSession):
    async with provide_repositories(session) as (_, reserved_repo):
        yield ReservedItemReadService(reserved_repo, session=session)


# ✏️ Write-Service (schreiben + logging)
@asynccontextmanager
async def provide_inventory_write_service(session: AsyncSession):
    async with session:
        async with provide_repositories(session) as (inventory_repo, reserved_repo):
            yield InventoryWriteService(
                session=session,
                inventory_repo=inventory_repo,
                reserved_item_repo=reserved_repo,
            )


# 🍓 GraphQL Resolver
async def provide_inventory_query_resolver():
    async with get_session() as session:
        async with provide_inventory_read_service(session=session) as read_service:
            return InventoryQueryResolver(read_service)


async def provide_reserved_item_query_resolver():
    async with get_session() as session:
        async with provide_reserved_item_read_service(session=session) as read_service:
            return ReservedItemQueryResolver(read_service)


async def provide_inventory_mutation_resolver():
    async with get_session() as session:
        async with provide_inventory_write_service(session=session) as write_service:
            return InventoryMutationResolver(write_service)
