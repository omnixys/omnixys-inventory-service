# src/product/logging/trace_context_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp
from loguru import logger

from inventory.tracing.trace_context import TraceContext
from inventory.tracing.trace_context_util import TraceContextUtil


class TraceContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        trace_ctx = TraceContextUtil.from_current_span()
        TraceContextUtil.set(trace_ctx)  # 💡 jetzt automatisch gesetzt
        logger.debug("🧠 TraceContext gesetzt: {}", trace_ctx)
        response = await call_next(request)
        return response

    async def dispatch2(self, request: Request, call_next):
        trace_id = request.headers.get("x-trace-id", "")
        span_id = request.headers.get("x-span-id", "")
        logger.debug(
            "🧠 TraceContext gesetzt: trace_id={}, span_id={}", trace_id, span_id
        )
        TraceContextUtil.set(TraceContext(trace_id=trace_id, span_id=span_id))

        # TraceContextUtil.set(trace_ctx)  # 💡 jetzt automatisch gesetzt
        response = await call_next(request)
        return response
