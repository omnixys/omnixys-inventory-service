# src/inventory/logging/logger_plus.py

import inspect
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4
from loguru import logger

from inventory.config import env
from inventory.config.kafka import get_kafka_settings
from inventory.tracing.log_event_dto import LogEventDTO, LogLevel
from inventory.tracing.trace_context_util import TraceContextUtil
from inventory.messaging.kafka_singleton import get_kafka_producer
from inventory.tracing.trace_context import TraceContext


class LoggerPlus:
    def __init__(self):
        self.producer = get_kafka_producer()

    def _get_call_context(self) -> tuple[str, str]:
        frame = inspect.stack()[2]
        return frame.frame.f_globals["__name__"], frame.function

    def _get_context(self) -> tuple[str, str]:
        frame = inspect.stack()[3]
        instance = frame.frame.f_locals.get("self", None)
        class_name = instance.__class__.__name__ if instance else "UnknownClass"
        method_name = frame.function
        return class_name, method_name

    async def log(
        self,
        level: LogLevel,
        message: str,
        *args: Any,
        trace_context: Optional[TraceContext] = None,
    ):
        class_name, method_name = self._get_context()
        trace_ctx = trace_context or TraceContextUtil.get()

        if args:
            message = message % args

        logger.log(level, f"{class_name}.{method_name}: {message}")

        event = LogEventDTO(
            id=uuid4(),
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            service=get_kafka_settings().client_id,
            class_name=class_name,
            method_name=method_name,
        )

        if level not in (LogLevel.DEBUG):
            await self.producer.send_log_event(event, trace_ctx)


    async def info(
        self, message: str, *args: Any, trace_context: Optional[TraceContext] = None
    ):
        await self.log(LogLevel.INFO, message, *args, trace_context=trace_context)

    async def warn(
        self, message: str, *args: Any, trace_context: Optional[TraceContext] = None
    ):
        await self.log(LogLevel.WARNING, message, *args, trace_context=trace_context)

    async def error(
        self, message: str, *args: Any, trace_context: Optional[TraceContext] = None
    ):
        await self.log(LogLevel.ERROR, message, *args, trace_context=trace_context)

    async def debug(
        self, message: str, *args: Any, trace_context: Optional[TraceContext] = None
    ):
        await self.log(LogLevel.DEBUG, message, *args, trace_context=trace_context)
