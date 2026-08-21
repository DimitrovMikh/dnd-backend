from typing import Annotated

from app.database import get_session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Healthcheck-Endpoint für Monitoring-Tools (z. B. Docker, Kubernetes, Hetzner Uptime-Pings).
    Führt einen leichten Ping-Query ('SELECT 1') auf der Datenbank aus, um die Erreichbarkeit zu garantieren.
    """
    try:
        # Führe eine minimale SQL-Abfrage aus, um die aktive DB-Verbindung zu verifizieren
        result = await session.exec(select(1))
        db_alive = result.first() is not None
        if not db_alive:
            raise HTTPException(
                status_code=503, 
                detail="Datenbank hat keine Antwort geliefert."
            )
    except SQLAlchemyError:
        # Reagiert mit HTTP 503 (Service Unavailable), falls die Datenbank ausfällt oder blockiert ist
        raise HTTPException(
            status_code=503, 
            detail="Datenbankverbindung fehlgeschlagen"
        )
    
    # Erfolgreicher System-Status bei funktionierender Datenbank-Verbindung
    return {
        "status": "healthy",
        "database": "connected",
    }
