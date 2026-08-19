from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    Healthcheck-Endpoint für Monitoring-Tools (z. B. Docker, Kubernetes, Hetzner Uptime-Pings).
    Führt einen leichten Ping-Query ('SELECT 1') auf der Datenbank aus, um die Erreichbarkeit zu garantieren.
    """
    try:
        # Führe eine minimale SQL-Abfrage aus, um die aktive DB-Verbindung zu verifizieren
        result = await session.exec(text("SELECT 1"))
        db_alive = result.first() is not None
        if not db_alive:
            raise Exception("Datenbank hat keine Antwort geliefert.")
    except Exception as e:
        # Reagiert mit HTTP 503 (Service Unavailable), falls die Datenbank ausfällt oder blockiert ist
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            },
        )
    
    # Erfolgreicher System-Status bei funktionierender Datenbank-Verbindung
    return {
        "status": "healthy",
        "database": "connected",
    }
