# inventory/repository/session.py

import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from inventory.config.db import db_url, db_connect_args

# Engine & SessionFactory (einmalig)
engine = create_async_engine(
    db_url,
    connect_args=db_connect_args or {},  # ← verhindert NoneType Error
    echo=False,
)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncSession:
    from loguru import logger

    async with AsyncSessionFactory() as session:
        logger.debug("🔑 Session opened: {}", session)
        try:
            yield session
        finally:
            logger.debug("🔒 Session closed: {}", session)


from sqlalchemy import inspect
import gc


async def dispose_connection_pool():
    from inventory.repository.session import engine
    from loguru import logger

    logger.info("🔻 Disposing DB Engine...")

    # 1. Versuche alle offenen Verbindungen zu schließen (nur aktiv beim dev-pool)
    try:
        pool = engine.pool
        if hasattr(pool, "_connections"):
            while pool._connections:
                conn = pool._connections.pop()
                if conn:
                    try:
                        raw = await conn.get()
                        raw.close()
                    except Exception:
                        pass
    except Exception:
        pass  # optional: logge Warnung hier

    # 2. Dispose Engine
    await engine.dispose()
    logger.info("✅ DB Engine disposed.")

    await asyncio.sleep(0.1)  # ⏱️ Wait to flush all pending destruction
    # 3. Erzwinge Garbage Collection, damit keine aiomysql-Leichen mehr rumliegen
    gc.collect()
