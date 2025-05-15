# from collections.abc import Mapping
# from typing import Final

# from loguru import logger
# from sqlalchemy import func, select
# from sqlalchemy.orm import Session

# from inventory.model.entity import Inventory
# from inventory.model.entity.reserved_item import Reserved_item
# from inventory.repository.pageable import Pageable
# from inventory.repository.slice import Slice


# class InventoryRepository:
#     def __init__(self, session: Session):
#         self.session = session

#     def find_by_id(self, inventory_id: str | None) -> Inventory | None:
#         logger.debug("inventory_id={}", inventory_id)
#         if inventory_id is None:
#             return None
#         stmt = select(Inventory).where(Inventory.id == inventory_id)
#         result = self.session.scalar(stmt)
#         logger.debug("{}", result)
#         return result

#     def find_by_sku_or_throw(self, sku_code: str) -> Inventory:
#         stmt = select(Inventory).where(Inventory.sku_code == sku_code)
#         result = self.session.scalar(stmt)
#         if result is None:
#             raise ValueError(f"Inventory mit SKU '{sku_code}' nicht gefunden")
#         return result

#     def find(
#         self, search_criteria: Mapping[str, str], pageable: Pageable
#     ) -> Slice[Inventory]:
#         logger.debug("{}", search_criteria)
#         if not search_criteria:
#             return self._find_all(pageable)

#         for key, value in search_criteria.items():
#             if key == "sku_code":
#                 inventory = self._find_by_sku_code(value)
#                 return (
#                     Slice(content=[inventory], total_elements=1)
#                     if inventory
#                     else Slice([], 0)
#                 )
#             if key == "product_name":
#                 return self._find_by_product_name(value, pageable)

#         return Slice([], 0)

#     def _find_all(self, pageable: Pageable) -> Slice[Inventory]:
#         offset = pageable.number * pageable.size
#         stmt = (
#             select(Inventory).limit(pageable.size).offset(offset)
#             if pageable.size
#             else select(Inventory)
#         )
#         content = self.session.scalars(stmt).all()
#         total = self._count()
#         return Slice(content=content, total_elements=total)

#     def _find_by_sku_code(self, sku_code: str) -> Inventory | None:
#         stmt = select(Inventory).where(Inventory.sku_code == sku_code)
#         return self.session.scalar(stmt)

#     def _find_by_product_name(self, teil: str, pageable: Pageable) -> Slice[Inventory]:
#         offset = pageable.number * pageable.size
#         stmt = (
#             select(Inventory)
#             .where(Inventory.product_id.ilike(f"%{teil}%"))
#             .limit(pageable.size)
#             .offset(offset)
#             if pageable.size
#             else select(Inventory).where(Inventory.product_id.ilike(f"%{teil}%"))
#         )
#         content = self.session.scalars(stmt).all()
#         total = self._count()
#         return Slice(content=content, total_elements=total)

#     def exists_sku_code(self, sku_code: str) -> bool:
#         stmt = select(func.count()).where(Inventory.sku_code == sku_code)
#         count = self.session.scalar(stmt)
#         return count is not None and count > 0

#     def exists_sku_code_other_id(self, sku_code: str, inventory_id: str) -> bool:
#         stmt = select(Inventory.id).where(Inventory.sku_code == sku_code)
#         id_db = self.session.scalar(stmt)
#         return id_db is not None and id_db != inventory_id

#     def create(self, inventory: Inventory) -> Inventory:
#         logger.debug("{}", inventory)
#         self.session.add(inventory)
#         self.session.flush([inventory])
#         return inventory

#     def update(self, inventory: Inventory) -> Inventory | None:
#         existing = self.find_by_id(inventory.id)
#         if not existing:
#             return None
#         existing.set(inventory)
#         return existing

#     def delete_by_id(self, inventory_id: str) -> None:
#         inventory = self.find_by_id(inventory_id)
#         if inventory:
#             self.session.delete(inventory)

#     def _count(self) -> int:
#         stmt = select(func.count()).select_from(Inventory)
#         return self.session.scalar(stmt) or 0
