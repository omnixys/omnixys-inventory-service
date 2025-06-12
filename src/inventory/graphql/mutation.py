import strawberry
from strawberry.types import Info
from inventory.error.authentication_error import AuthenticationError
from inventory.model.entity.inventory import InventoryInput, InventoryType
from inventory.model.entity.reserved_item import ReserveInventoryItemInput
from inventory.security.keycloak_service import KeycloakService
from inventory.dependency_provider import provide_inventory_mutation_resolver
from loguru import logger

# ---------------------------
# GraphQL Mutation Definition
# ---------------------------
@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_inventory(
        self, info: Info, input: InventoryInput
    ) -> InventoryType:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin"])

        resolver = await provide_inventory_mutation_resolver()
        return await resolver.create_inventory(info=info, input=input)

    @strawberry.mutation
    async def update_inventory(
        self, info: Info, inventory_id: strawberry.ID, input: InventoryInput
    ) -> InventoryType:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin"])

        resolver = await provide_inventory_mutation_resolver()
        return await resolver.update_inventory(
            info=info, inventory_id=str(inventory_id), input=input
        )

    @strawberry.mutation
    async def delete_inventory(self, info: Info, inventory_id: strawberry.ID) -> bool:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin"])

        resolver = await provide_inventory_mutation_resolver()
        return await resolver.delete_inventory(
            info=info, inventory_id=str(inventory_id)
        )

    @strawberry.mutation
    async def reserve_inventory(
        self, info: Info, input: ReserveInventoryItemInput
    ) -> InventoryType:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        resolver = await provide_inventory_mutation_resolver()
        return await resolver.reserve_inventory(info=info, input=input)

    @strawberry.mutation
    async def release_inventory(
        self, info: Info, input: ReserveInventoryItemInput
    ) -> InventoryType:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        resolver = await provide_inventory_mutation_resolver()
        return await resolver.release_inventory(info=info, input=input)
