# inventory/messaging/kafka_singleton.py

from typing import Optional
from inventory.config import env
from inventory.messaging.handler.release_item_handler import ReleaseItemHandler
from inventory.messaging.kafka_consumer_service import KafkaConsumerService
from inventory.messaging.kafka_event_dispatcher import KafkaEventDispatcher
from inventory.messaging.kafka_producer_service import KafkaProducerService
from inventory.messaging.kafka_topic_properties import KafkaTopics
from inventory.messaging.handler.reserve_item_handler import ReserveItemHandler

# ❌ Kein @lru_cache, damit .start()/.stop() steuerbar bleiben
_kafka_producer_instance: Optional[KafkaProducerService] = None
_kafka_consumer_instance: Optional[KafkaConsumerService] = None


def get_kafka_producer() -> KafkaProducerService:
    global _kafka_producer_instance
    if _kafka_producer_instance is None:
        _kafka_producer_instance = KafkaProducerService()
    return _kafka_producer_instance


dispatcher = KafkaEventDispatcher()


async def get_kafka_consumer() -> KafkaConsumerService:
    dispatcher.register(
    KafkaTopics.inventory_reserve,
    ReserveItemHandler(),
    )

    dispatcher.register(
        KafkaTopics.inventory_release,
        ReleaseItemHandler(),
    )

    return KafkaConsumerService(
        dispatcher=dispatcher,
        topics=[KafkaTopics.inventory_reserve, KafkaTopics.inventory_release],
        bootstrap_servers=env.KAFKA_URI,
    )
