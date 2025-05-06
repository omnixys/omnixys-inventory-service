"""
KafkaConsumerService – liest Log-Nachrichten aus Kafka und verarbeitet sie.
"""

import asyncio
import json
import re
from aiokafka import AIOKafkaConsumer
from typing import Optional
from loguru import logger


class KafkaConsumerService:
    """Asynchrone Kafka-Consumer-Logik für Log-Einträge."""

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self._bootstrap_servers = bootstrap_servers
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Initialisiert den Kafka-Consumer und startet den Hintergrundtask."""
        self._consumer = AIOKafkaConsumer(
            bootstrap_servers=self._bootstrap_servers,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            group_id="logging-consumer-group",
            enable_auto_commit=True,
            auto_offset_reset="earliest",  # wichtig für lokale Tests
        )
        await self._consumer.start()
        self._consumer.subscribe(
            pattern=re.compile(r"^(system\.shutdown)$")
        )
        self._task = asyncio.create_task(self._consume())
        logger.info("✅ Kafka-Consumer hört auf Topics wie activity.*.log")

    async def stop(self) -> None:
        """Beendet den Kafka-Consumer und den Hintergrundtask."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.info("📴 Kafka-Consumer-Task abgebrochen.")
        if self._consumer:
            await self._consumer.stop()
        logger.info("🛑 Kafka-Consumer gestoppt.")

    async def _consume(self):
        """Liest kontinuierlich Nachrichten aus dem Kafka-Topic."""
        try:
            async for msg in self._consumer:
                logger.debug(f"📥 Kafka-Log empfangen: {msg.topic} – {msg.value}")
                await self.handle_log(msg.value)
        except Exception as e:
            logger.error(f"❌ Fehler im Kafka-Consumer: {e}")

    async def handle_log(self, event: dict):
            """Verarbeitet empfangene Kafka-Events."""
            event_type = event.get("event") or event.get("type")  # robust für verschiedene Schemas

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

