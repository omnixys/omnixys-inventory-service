"""Neuladen der DB im Modus DEV."""

import sqlite3  # noqa: F401
from importlib.resources import files
from importlib.resources.abc import Traversable
from re import match
from string import Template
from typing import Final

from loguru import logger
from sqlalchemy import Connection, text

from inventory.config.config import resources_path
from inventory.config.db import db_url, name
from inventory.config.dev_modus import dev
from inventory.repository import engine
from inventory.repository.session import AsyncSessionFactory

__all__ = ["db_populate"]


utf8: Final = "utf-8"
_db_traversable: Final[Traversable] = files(resources_path)


async def db_populate() -> None:
    """DB durch einzelne SQL-Anweisungen als Prepared Statement neu laden."""

    if not dev:
        return

    logger.warning(">>> Die DB wird neu geladen: {} <<<", db_url)

    async with AsyncSessionFactory() as session:
        async with session.begin():
            conn = await session.connection()
    
            db_dialect: Final = conn.dialect.name
            dialect_path: Final = _db_traversable / db_dialect
    
            with open(file=str(dialect_path / "drop.sql"), encoding=utf8) as drop_sql:
                zeilen_drop = _remove_comment(drop_sql.readlines())
                drop_statements = _build_sql_statements(zeilen_drop)
                for stmt in drop_statements:
                    await conn.execute(text(stmt))
    
            with open(file=str(dialect_path / "create.sql"), encoding=utf8) as create_sql:
                zeilen_create = _remove_comment(create_sql.readlines())
                create_statements = _build_sql_statements(zeilen_create)
                for stmt in create_statements:
                    await conn.execute(text(stmt))

    logger.warning(">>> Die DB wurde neu geladen <<<")

    # ggf. separate CSV-Phase (asynchron)
    async with engine.begin() as conn:
        db_dialect = conn.dialect.name
        await _load_csv_files(conn, db_dialect=db_dialect)
    await engine.dispose()
    logger.warning(">>> Die DB wurde neu geladen <<<")


def _remove_comment(zeilen: list[str]) -> list[str]:
    """SQL-Kommentare und Leerzeilen entfernen."""
    return [zeile for zeile in zeilen if not match(r"^ *--", zeile) and zeile != "\n"]

def _build_sql_statements(zeilen: list[str]) -> list[str]:
    """Zeilen mit SQL-Anweisungen zu einer Zeile zusammenfassen."""
    statements: list[str] = []
    sql: str = ""
    anzahl: Final = len(zeilen)
    for i in range(anzahl):
        zeile = zeilen[i]
        sql += zeile.replace("\n", " ")
        if zeile.endswith(";\n"):
            statements.append(sql)
            sql = ""
    return statements


async def _load_csv_files(conn, db_dialect: str) -> None:
    logger.debug("begin")

    tabellen: Final = ["inventory", "reserved_item"]
    csv_path: Final = "/var/lib/mysql-files/inventory"

    await _set_schema(db_dialect, conn)

    for tabelle in tabellen:
        await _load_csv_file(
            tabelle=tabelle,
            csv_path=csv_path,
            db_dialect=db_dialect,
            conn=conn,
        )


async def _set_schema(db_dialect: str, conn) -> None:
    logger.debug("db_dialect={} url={}", db_dialect, conn.engine.url)
    await conn.execute(text(f"USE `{name}`;"))


async def _load_csv_file(tabelle: str, csv_path: str, db_dialect: str, conn) -> None:
    await _load_csv_mysql(tabelle, csv_path, conn)


async def _load_csv_mysql(tabelle: str, csv_path: str, conn) -> None:
    logger.debug("tabelle={}", tabelle)

    load_cmd: Final = (
        Template(
            "LOAD DATA INFILE '"
            + csv_path
            + "/${tabelle}.csv' INTO TABLE ${tabelle} FIELDS TERMINATED BY ',' ENCLOSED"
            " BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS;",
        )
        if tabelle != "inventory"
        else Template(
            "LOAD DATA INFILE '"
            + csv_path
            + "/${tabelle}.csv' INTO TABLE ${tabelle} FIELDS TERMINATED BY ',' ENCLOSED"
            " BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS "
            "(id, version, sku_code, quantity, unit_price, status, product_id, created, updated);"
        )
    ).substitute(tabelle=tabelle)

    await conn.execute(text(load_cmd))

async def db_populate_multiple() -> None:
    logger.warning(">>> Die DB wird neu geladen: {} <<<", db_url)

    async with engine.begin() as conn:
        script_path: Final = _db_traversable / conn.dialect.name

        with open(file=str(script_path / "drop.sql"), encoding=utf8) as drop_sql:
            await conn.execute(text(drop_sql.read()))

        with open(file=str(script_path / "create.sql"), encoding=utf8) as create_sql:
            await conn.execute(text(create_sql.read()))

        with open(file=str(script_path / "insert.sql"), encoding=utf8) as insert_sql:
            await conn.execute(text(insert_sql.read()))

    await engine.dispose()
    logger.warning(">>> Die DB wurde neu geladen <<<")
