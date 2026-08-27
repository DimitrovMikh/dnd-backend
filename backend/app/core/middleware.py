from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware zur automatischen Injektion von OWASP-Standard-Sicherheitsheadern.
    Schützt die Anwendung clientseitig vor Clickjacking, MIME-Sniffing und XSS.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Verarbeitet den Request und holt die ursprüngliche Response der API
        response = await call_next(request)
        # Verhindert Clickjacking-Angriffe (Einbetten der Seite in <iframe>)
        response.headers["X-Frame-Options"] = "DENY"
        # Verhindert MIME-Sniffing (zwingt den Browser, den deklarierten Content-Type zu nutzen)
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Aktiviert den veralteten, aber für ältere Browser nützlichen XSS-Filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Steuert, welche Referrer-Informationen bei externen Links mitgesendet werden
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
