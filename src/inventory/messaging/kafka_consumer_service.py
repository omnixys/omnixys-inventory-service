"""
KafkaConsumerService – liest Log-Nachrichten aus Kafka und verarbeitet sie.
"""

from aiokafka import AIOKafkaConsumer
from loguru import logger
import asyncio, json

from inventory.messaging.kafka_event_dispatcher import KafkaEventDispatcher

class KafkaConsumerService:
    """Asynchrone Kafka-Consumer-Logik für Log-Einträge."""

    def __init__(
        self,
        dispatcher: KafkaEventDispatcher,
        topics: list[str],
        bootstrap_servers: str = "localhost:9092",
    ):
        self.dispatcher = dispatcher
        self.topics = topics
        self._bootstrap_servers = bootstrap_servers
        self._consumer = None
        self._task = None

    async def start(self):
        self._consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self._bootstrap_servers,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="inventory-group",
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume())
        logger.info("📡 Kafka Consumer gestartet.")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.stop()

    async def _consume(self):
        async for msg in self._consumer:
            topic = msg.topic
            headers = dict((k, v.decode("utf-8")) for k, v in (msg.headers or []))
            logger.debug(f"📥 Kafka MSG: {msg.value} on topic={topic} headers={headers}")
            handler = self.dispatcher.get_handler(topic)
            if handler:
                try:
                    await handler(msg.value, headers)
                    logger.debug(f"✅ Handler für Topic '{topic}' erfolgreich ausgeführt")
                except Exception as e:
                    logger.exception(f"❌ Fehler im Handler für Topic '{topic}': {e}")
            else:
                logger.warning(f"⚠️ Kein Handler für Topic: {topic}")


    async def handle_log(self, event: dict):
        """Verarbeitet empfangene Kafka-Events."""
        event_type = event.get("event") or event.get(
            "type"
        )  # robust für verschiedene Schemas

        if event_type == "shutdown":
            logger.warning("⚠️ Shutdown-Event empfangen! Anwendung wird beendet.")
            await self.shutdown_application()
        else:
            # Normaler Logprozess
            logger.info(f"📝 Log-Eintrag: {event}")

    async def shutdown_application(self):
        """Führt einen geregelten Shutdown der FastAPI-Anwendung durch."""
        await self.stop()  # zuerst Kafka-Consumer stoppen
        loop = asyncio.get_event_loop()
        loop.call_later(1, loop.stop)  # sanfter Stop (optional: os._exit(0))
