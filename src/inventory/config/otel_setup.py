# src/product/otel_setup.py

from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 🔧 Prometheus Setup
from inventory.config import env
from inventory.config.kafka import get_kafka_settings

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware

from inventory.tracing.trace_context_middleware import TraceContextMiddleware

def setup_otel(app):
    resource = Resource(attributes={SERVICE_NAME: get_kafka_settings().client_id})

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint=env.TEMPO_URI
        )
    except Exception as e:
        logger.warning("Tempo Exporter konnte nicht gestartet werden: {}", str(e))

    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    # Instrumentiere FastAPI und MongoDB
    FastAPIInstrumentor().instrument_app(app)

    # 🛠 TraceContextMiddleware aktivieren
    app.add_middleware(TraceContextMiddleware)
    app.add_middleware(OpenTelemetryMiddleware)
