import orjson
from aiokafka import AIOKafkaProducer
from loguru import logger
from typing import Final, Optional, Union

from opentelemetry import trace

from inventory.config.kafka import get_kafka_settings
from inventory.tracing.trace_context import TraceContext
from inventory.tracing.trace_context_util import TraceContextUtil


class KafkaProducerService:
    """Kafka Producer mit automatischem Tracing und Header-Support."""

    def __init__(self) -> None:
        self._producer: Optional[AIOKafkaProducer] = None
        self.started: bool = False

        settings = get_kafka_settings()
        self._bootstrap: Final = settings.bootstrap_servers
        self._client_id: Final = settings.client_id
        self._topic_log: Final = settings.topic_log

    async def start(self) -> None:
        if not self._producer:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap, client_id=self._client_id, acks="all"
            )
            await self._producer.start()
            self.started = True
            logger.info("✅ Kafka Producer gestartet")

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            self._producer = None
            self.started = False
            logger.info("🛑 Kafka Producer gestoppt")

    async def publish(
        self,
        topic: str,
        payload: Union[dict, bytes],
        trace_ctx: Optional[TraceContext] = None,
        headers: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        if not self.started or not self._producer:
            raise RuntimeError("Kafka Producer ist nicht gestartet")

        trace_ctx = trace_ctx or TraceContextUtil.get()
        tracer = trace.get_tracer("inventory.kafka")

        kafka_headers: list[tuple[str, bytes]] = []

        if trace_ctx:
            kafka_headers += [
                (k, v.encode()) for k, v in TraceContextUtil.to_headers(trace_ctx)
            ]
        if headers:
            kafka_headers += [(k, str(v).encode()) for k, v in headers]

        if isinstance(payload, dict):
            value = orjson.dumps(payload)
        else:
            value = payload  # falls schon serialisiert

        with tracer.start_as_current_span(f"kafka.publish.{topic}") as span:
            span.set_attribute("messaging.system", "kafka")
            span.set_attribute("messaging.destination", topic)
            span.set_attribute("messaging.operation", "send")
            span.set_attribute("messaging.message_payload_size_bytes", len(value))

            logger.debug("📤 Sende Kafka-Event an '{}': {}", topic, payload)
            await self._producer.send_and_wait(
                topic, value=value, headers=kafka_headers
            )

    async def send_log_event(self, log_event: dict, trace_ctx: TraceContext) -> None:
        """Sende strukturierte Log-Events (z. B. von LoggerPlus)."""
        await self.publish(
            topic=self._topic_log,
            payload=log_event,
            trace_ctx=trace_ctx,
            headers=[
                ("x-service", self._client_id),
                ("x-event-name", "log"),
                ("x-event-version", "1.0.0"),
            ],
        )
