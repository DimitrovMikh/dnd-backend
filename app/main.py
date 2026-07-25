from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from app.core.exceptions import DNDGameException
from app.database import engine
from app.api.characters import router as characters_router
from app.api.items import router as items_router
from app.api.spells import router as spells_router

# Importieren der Modelle, damit SQLModel die Tabellenstruktur für create_all kennt
import app.models.characters    # noqa: F401
import app.models.items         # noqa: F401
import app.models.spells        # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan-Handler für Anwendungs-Start und -Stopp.
    Erstellt beim Serverstart automatisch alle Datenbank-Tabellen, falls sie fehlen.
    """

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(title="D&D Campaign Manager API", lifespan=lifespan)


@app.exception_handler(DNDGameException)
async def dnd_game_exception_handler(request: Request, exc: DNDGameException):
    """Fängt alle Domain Exceptions (DNDGameException und Kindklassen) ab
    und übersetzt sie automatisch in eine strukturierte JSON-Antwort für den Client.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )


# Einbinden der modularen API-Router
app.include_router(characters_router, prefix="/characters", tags=["Characters"])
app.include_router(items_router, prefix="/items", tags=["Items"])
app.include_router(spells_router, prefix="/spells", tags=["Spells"])


@app.get("/", tags=["Health"])
async def read_root():
    return {"status": "online", "message": "Willkommen im modularen Backend!"}


@app.get("/ping", tags=["Health"])
async def ping():
    return {"ping": "pong"}