from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from inventory.model.entity.reserved_item import Reserved_item


class ReservedItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_reserve_items(
        self,
        customer_id: Optional[str] = None,
    ) -> list[Reserved_item]:
        stmt = select(Reserved_item)

        if customer_id:
            stmt = stmt.where(Reserved_item.customer_id == customer_id)

        result = await self.session.scalars(stmt)
        return result.all()

    async def find_by_composite_key_or_throw(
        self,
        customer_id: str,
    ) -> Reserved_item:
        stmt = (
            select(Reserved_item)
            .join(Reserved_item.inventory)
            .where(
                Reserved_item.customer_id == customer_id,
            )
        )
        result = await self.session.scalar(stmt)
        if result is None:
            raise ValueError(
                f"Keine Reservierung gefunden für Customer={customer_id}"
            )
        return result

    async def save(self, reserved_item: Reserved_item) -> Reserved_item:
        self.session.add(reserved_item)
        await self.session.flush()
        return reserved_item

    async def delete(self, reserved_item: Reserved_item) -> None:
        await self.session.delete(reserved_item)
