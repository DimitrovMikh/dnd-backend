from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

# Asynchroner SQLite Treiber (aiosqlite)
DATABASE_URL = "sqlite+aiosqlite:///./database.db"

# Echo=True loggt alle generierten SQL-Statements in die Konsole (hilfreich beim Debuggen)
engine = create_async_engine(DATABASE_URL, echo=True)

async def get_session():
    """
    FastAPI Dependency Injector: Stellt eine asynchrone Datenbank-Session bereit 
    und schließt diese nach dem Request automatisch (yield pattern).
    """
    async with AsyncSession(engine) as session:
        yield session