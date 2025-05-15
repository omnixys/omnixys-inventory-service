# src/product/logging/trace_context_util.py

from contextvars import ContextVar
from opentelemetry.context import Context
from fastapi import Request
from opentelemetry.trace import get_current_span
from opentelemetry.trace import (
    SpanContext,
    TraceFlags,
    TraceState,
    NonRecordingSpan,
    set_span_in_context,
    INVALID_SPAN_CONTEXT,
)

from inventory.config.kafka import get_kafka_settings
from inventory.tracing.trace_context import TraceContext

_trace_context_var: ContextVar[TraceContext] = ContextVar(
    "trace_context", default=TraceContext()
)

class TraceContextUtil:
    """Hilfsklasse zur Extraktion von Trace-Daten aus HTTP- oder Kafka-Headern."""

    _service: str = get_kafka_settings().client_id


    @staticmethod
    def set(trace_context: TraceContext):
        _trace_context_var.set(trace_context)

    @staticmethod
    def get() -> TraceContext:
        return _trace_context_var.get()

    @classmethod
    def from_current_span(cls) -> TraceContext:
        span = get_current_span()
        ctx = span.get_span_context()
        return TraceContext(
            trace_id=format(ctx.trace_id, "032x") if ctx.trace_id else None,
            span_id=format(ctx.span_id, "016x") if ctx.span_id else None,
            parent_id=None,
            x_service=cls._service,
        )

    @staticmethod
    def from_request(request: Request) -> tuple[TraceContext, Context]:
        """
        Extrahiert TraceContext + OpenTelemetry-Kontext aus Kafka-Headern.

        :param headers: Kafka-Header als (key, value)-Paare
        :return: (TraceContext, OpenTelemetry-Kontext)
        """
        headers = request.headers
        print("🌐 Headers:", dict(request.headers))

        # Sicheres Decoding
        decoded = {
            k.decode() if isinstance(k, bytes) else k: (
                v.decode() if isinstance(v, bytes) else v
            )
            for k, v in headers or []
        }

        trace_id = decoded.get("x-b3-traceid") or decoded.get("x-trace-id")
        span_id = decoded.get("x-b3-spanid")
        parent_id = decoded.get("x-b3-parentspanid")
        x_service = decoded.get("x-service")

        trace_ctx = TraceContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            x_service=x_service,
        )

        # Kontext für OpenTelemetry-Span bauen
        try:
            if trace_id and span_id:
                span_context = SpanContext(
                    trace_id=int(trace_id, 16),
                    span_id=int(span_id, 16),
                    is_remote=True,
                    trace_flags=TraceFlags(TraceFlags.SAMPLED),
                    trace_state=TraceState(),
                )
                otel_context = set_span_in_context(NonRecordingSpan(span_context))
                return trace_ctx, otel_context
        except Exception:
            pass

        # Fallback: leerer Kontext
        return trace_ctx, set_span_in_context(NonRecordingSpan(INVALID_SPAN_CONTEXT))

    @staticmethod
    def from_kafka_headers(headers: list[tuple[str, bytes]]) -> tuple[TraceContext, Context]:
        """
        Extrahiert TraceContext + OpenTelemetry-Kontext aus Kafka-Headern.

        :param headers: Kafka-Header als Liste von (key, bytes)
        :return: (TraceContext, OTel-Kontext)
        """
        decoded = {
            k.decode() if isinstance(k, bytes) else k:
            v.decode() if isinstance(v, bytes) else v
            for k, v in headers or []
        }

        trace_id = decoded.get("x-b3-traceid") or decoded.get("x-trace-id")
        span_id = decoded.get("x-b3-spanid")
        parent_id = decoded.get("x-b3-parentspanid")
        x_service = decoded.get("x-service")

        trace_ctx = TraceContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            x_service=x_service,
        )

        try:
            if trace_id and span_id:
                span_context = SpanContext(
                    trace_id=int(trace_id, 16),
                    span_id=int(span_id, 16),
                    is_remote=True,
                    trace_flags=TraceFlags(TraceFlags.SAMPLED),
                    trace_state=TraceState(),
                )
                otel_context = set_span_in_context(NonRecordingSpan(span_context))
                return trace_ctx, otel_context
        except Exception as e:
            print("⚠️ Fehler beim Erstellen des SpanContext:", e)

        return trace_ctx, set_span_in_context(NonRecordingSpan(INVALID_SPAN_CONTEXT))

    @staticmethod
    def to_headers(trace_ctx: TraceContext) -> list[tuple[str, str]]:
        """
        Erzeugt Kafka-kompatible Header aus einem TraceContext.

        :param trace_ctx: TraceContext-Objekt
        :return: Liste von Headern (key, str_value)
        """
        headers: list[tuple[str, str]] = []

        if trace_ctx.trace_id:
            headers.append(("x-b3-traceid", trace_ctx.trace_id))
        if trace_ctx.span_id:
            headers.append(("x-b3-spanid", trace_ctx.span_id))
        if trace_ctx.parent_id:
            headers.append(("x-b3-parentspanid", trace_ctx.parent_id))
        if trace_ctx.x_service:
            headers.append(("x-service", trace_ctx.x_service))

        return headers
