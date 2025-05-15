"""Funktion `run`, um die FastAPI-Applikation mit einem ASGI-Server zu starten.

Dazu stehen _uvicorn_ (default) und _hypercorn_ zur Verfügung.
"""

import asyncio
from ssl import PROTOCOL_TLS_SERVER
from typing import Final

import uvicorn
from hypercorn.asyncio import serve
from hypercorn.config import Config

from .config import (
    asgi,
    host_binding,
    port,
    tls_certfile,
    tls_keyfile,
)
from .fastapi_app import app

__all__ = ["run"]

def _run_hypercorn() -> None:
    """Start der Anwendung mit hypercorn."""
    config: Final = Config()
    config.bind = [f"{host_binding}:{port}"]
    # config.keyfile = tls_keyfile
    # config.certfile = tls_certfile
    # asyncio.run(serve(app=app, config=config, mode="asgi"))  # pyright: ignore[reportArgumentType]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(serve(app=app, config=config, mode="asgi"))  # pyright: ignore[reportArgumentType]
        loop.run_until_complete(asyncio.sleep(0.5))  # ⚠️ Zeit für TLS/aiomysql shutdown
    finally:
        loop.close()


def run() -> None:
    """CLI für den asynchronen Appserver."""
    _run_hypercorn()
