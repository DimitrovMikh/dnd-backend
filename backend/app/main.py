"""Haupt-Einstiegspunkt der FastAPI-Anwendung.
Registriert Middleware, Exception-Handler, Lifespan-Hooks und API-Router.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.exceptions import DNDGameException
from app.core.config import settings
from app.core.limiter import limiter
from app.core.middleware import SecurityHeadersMiddleware
from app.api.v1.characters import router as characters_router
from app.api.v1.items import router as items_router
from app.api.v1.spells import router as spells_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan-Handler für Anwendungs-Start und -Stopp.
    Dient als Hook für Start- und Aufräumarbeiten der Anwendung.
    """

    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# --- RATE LIMITER CONFIGURATION (slowapi) ---
# Registriert die Limiter-Instanz im App-State für routenbasierte Zugriffsbeschränkungen
app.state.limiter = limiter

# Fängt RateLimitExceeded-Exceptions ab und übersetzt sie in HTTP 429 Responses
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Verarbeitet Anfragen-Headers und IP-Adressen für das Rate-Limiting
app.add_middleware(SlowAPIMiddleware)


# --- OWASP SECURITY HEADERS MIDDLEWARE ---
app.add_middleware(SecurityHeadersMiddleware)


# --- SECURITY & CORS HARDENING ---
# Konfiguriert Cross-Origin Resource Sharing für den sicheren Datenaustausch mit dem Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Strikte Herkunftskontrolle (kein Wildcard)
    allow_credentials=True,                  # Erlaubt das Übertragen von HttpOnly Refresh-Cookies
    allow_methods=["*"],                     # Erlaubt alle Standard-HTTP-Methoden (GET, POST, etc.)
    allow_headers=["*"],                     # Erlaubt alle gängigen HTTP-Header (Authorization, Content-Type)
)


@app.exception_handler(DNDGameException)
async def dnd_game_exception_handler(request: Request, exc: DNDGameException):
    """Fängt alle Domain Exceptions (DNDGameException und Kindklassen) ab
    und übersetzt sie automatisch in eine strukturierte JSON-Antwort für den Client.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )


# Einbinden der modularen API-Router
app.include_router(characters_router, prefix="/characters", tags=["Characters"])
app.include_router(items_router, prefix="/items", tags=["Items"])
app.include_router(spells_router, prefix="/spells", tags=["Spells"])
app.include_router(auth_router)
app.include_router(health_router)


@app.get("/", tags=["Health"])
async def read_root():
    return {"status": "online", "message": "Willkommen im modularen Backend!"}


@app.get("/ping", tags=["Health"])
async def ping():
    return {"ping": "pong"}