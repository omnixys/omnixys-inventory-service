from functools import wraps
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from typing import Optional
from starlette.requests import Request

from inventory.tracing.trace_context_util import TraceContextUtil

tracer = trace.get_tracer(__name__)


def traced(name: Optional[str] = None):
    """
    Dekorator für automatisches OpenTelemetry Tracing.

    Erkennt automatisch, ob ein Request (HTTP) oder ein Kafka-Header als Kontext vorliegt.
    """

    def decorator(func):
        span_name = name or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Kontext automatisch übernehmen, wenn vorhanden
            otel_context = None
            for arg in args:
                if isinstance(arg, Request):
                    # HTTP-Request: Extrahiere Kontext
                    trace_ctx, otel_context = TraceContextUtil.from_request(arg)
                    break

            with tracer.start_as_current_span(
                span_name, kind=SpanKind.INTERNAL, context=otel_context
            ):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name, kind=SpanKind.INTERNAL):
                return func(*args, **kwargs)

        return (
            async_wrapper
            if callable(getattr(func, "__await__", None))
            else sync_wrapper
        )

    return decorator
