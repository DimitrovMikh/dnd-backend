import time

import structlog
from fastapi import Request

logger = structlog.get_logger()


async def logging_middleware(request: Request, call_next):
    """FastAPI-Middleware zur Aufzeichnung aller eingehenden HTTP-Requests.

    Misst die exakte Verarbeitungszeit und protokolliert HTTP-Methode, Pfad,
    Statuscode, Ausführungsdauer sowie die Client-IP als strukturiertes Log-Event.
    """
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_seconds=round(process_time, 4),
        client_ip=request.client.host if request.client else None,
    )
    return response
