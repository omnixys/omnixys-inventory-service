import os
from typing import Final
from aiokafka import AIOKafkaProducer
import aiomysql
import aiohttp
from inventory.config.config import inventory_config
from inventory.config.env import env
from inventory.health.health_env import health_settings

_db_toml: Final = inventory_config.get("db", {})

name: Final[str] = _db_toml.get("name", "inventory")
_main_memory: Final[bool] = bool(_db_toml.get("main-memory", False))
_host: Final[str] = _db_toml.get("host", "localhost")
_db_host: Final[str] = _host
_username: Final[str] = _db_toml.get("username", "inventory")
_password: Final[str] = _db_toml.get("password", "Change Me!")
_password_admin: Final[str] = _db_toml.get("password-admin", "Change Me!")


async def check_kafka():
    try:
        producer = AIOKafkaProducer(bootstrap_servers=env.KAFKA_URI)
        await producer.start()
        await producer.stop()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "down", "message": str(e)}


def check_cert(filename: str):
    path = os.path.join(env.KEYS_PATH, filename)
    try:
        if not os.path.exists(path):
            return {"status": "down", "message": "missing"}
        with open(path, "rb") as f:
            f.read()
        return {"status": "ok"}
    except Exception:
        return {"status": "down", "message": "unreadable"}


async def check_http(name: str, url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2) as resp:
                if resp.status == 200:
                    return {name: {"status": "ok"}}
                return {name: {"status": "down", "code": resp.status}}
    except Exception as e:
        return {name: {"status": "down", "message": str(e)}}


async def check_mysql():
    if not health_settings.MYSQL_HEALTH_ENABLED:
        return {"status": "skipped"}
    try:
        conn = await aiomysql.connect(
            user=_username,
            password=_password,
            host=_db_host,
            db=name,
            port=3306,
        )
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "down", "message": str(e)}
