from loguru import logger
from inventory.model.entity.reserved_item import ReserveInventoryItemInput
from inventory.repository.session import get_session
from inventory.tracing.trace_context_util import TraceContextUtil


class ReserveItemHandler:
    async def __call__(self, payload: dict, headers: dict):
        # ⛔ Zirkularimport vermeiden durch Lazy Import:
        from inventory.dependency_provider import provide_inventory_write_service

        async with get_session() as session:
            async with provide_inventory_write_service(session=session) as write_service:
                trace = TraceContextUtil.from_kafka_headers(headers)

                try:
                    input = ReserveInventoryItemInput(
                        sku_code=payload["skuCode"],
                        quantity=payload["quantity"],
                        customer_id=payload["customerId"],
                    )

                    await write_service.reserve(input)
                except KeyError as e:
                    logger.error(f"⚠️ Fehlendes Feld im Payload: {e}")
                    return
