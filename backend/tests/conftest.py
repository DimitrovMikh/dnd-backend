"""Pytest-Konfiguration und globale Async-Fixtures.
Stellt eine In-Memory-SQLite-Datenbank und einen Test-Client bereit.
"""
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.main import app

# In-Memory SQLite URL für isolierte, blitzschnelle Tests im RAM
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Erstellt vor jedem Test frische Tabellen im Arbeitsspeicher
    und löscht sie nach Ausführung des Tests wieder (Teardown).
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Setup: Tabellen im RAM anlegen
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    # Teardown: Tabellen droppen & Engine schließen
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    async_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Erstellt einen httpx AsyncClient und überschreibt die get_session-Dependency
    von FastAPI mit der aktuellen Test-Session.
    """
    async def get_test_session():
        # Leert den Session-Cache vor jedem Request, damit frische Daten aus der DB geladen werden
        async_session.expire_all()
        yield async_session
    
    # FastAPI-Dependency Override aktivieren
    app.dependency_overrides[get_session] = get_test_session

    # HTTP-Client an das FastAPI-App-Objekt binden
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    # Nach dem Test alle Overrides entfernen
    app.dependency_overrides.clear()