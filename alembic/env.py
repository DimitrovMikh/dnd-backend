"""Alembic Migrations-Umgebungskonfiguration.
Verbindet Alembic mit den SQLModel-Metadaten und stellt den
asynchronen Migrationsablauf für SQLite und PostgreSQL bereit.
"""
import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

# Models importieren, damit SQLModel.metadata die Tabellenstrukturen kennt
from app.models.characters import Character  # noqa: F401
from app.models.items import Item  # noqa: F401
from app.models.spells import CharacterSpellLink, Spell  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def get_url() -> str:
    """Ermittelt die Datenbank-URL dynamisch aus Umgebungsvariablen
    oder nutzt den Fallback-Wert aus der alembic.ini.
    """
    return os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))


def run_migrations_offline() -> None:
    """Migrationen im 'offline'-Modus ausführen (generiert reines SQL-Skript)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Führt die Migrationen innerhalb einer aktiven DB-Verbindung aus."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Asynchroner Engine-Ablauf für Online-Migrationen."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Migrationen im 'online'-Modus direkt gegen die Datenbank ausführen."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()