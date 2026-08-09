from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings

# Relativer Pfad zur SQLite-Datenbank im Projektstamm
DATABASE_URL = settings.DATABASE_URL

# Engine mit Logging für SQL-Queries
engine = create_async_engine(DATABASE_URL, echo=True)

# Session Factory: expire_on_commit=False verhindert Detached-Instance-Fehler nach commits
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency Injector: Stellt eine asynchrone Datenbank-Session bereit 
    und schließt diese nach dem Request automatisch (yield pattern).
    """

    async with async_session_maker() as session:
        yield session