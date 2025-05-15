# src/product/logging/trace_context.py

from pydantic import BaseModel
from typing import Optional


class TraceContext(BaseModel):
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_id: Optional[str] = None
    x_service: Optional[str] = None
