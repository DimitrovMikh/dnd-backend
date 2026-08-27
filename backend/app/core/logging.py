import logging
import sys

import sentry_sdk
import structlog
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration


def setup_logging():
    """Konfiguriert strukturiertes JSON-Logging für die Anwendung mittels structlog.

    Erstellt eine Processing-Pipeline für Log-Events (Timestamps, Log-Level, Stacktraces)
    und leitet alle Ausgaben im JSON-Format an stdout weiter.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,        # Kontextvariablen für asynchrone Requests verknüpfen
            structlog.processors.add_log_level,             # Log-Level (INFO, ERROR, etc.) im Event verankern
            structlog.processors.StackInfoRenderer(),       # Callstacks bei Fehlern aufbereiten
            structlog.dev.set_exc_info,                     # Exception-Details bei Tracebacks erfassen
            structlog.processors.TimeStamper(fmt="iso"),    # ISO-8601 Zeitstempel hinzufügen
            structlog.processors.JSONRenderer(),            # Ausgabe in strukturiertes JSON formatieren
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Standard-Python-Logging (z. B. von Uvicorn) auf stdout umleiten
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)


def init_sentry(dsn: str | None, environment: str = "production"):
    """Initialisiert das Sentry SDK für globales Error Tracking und Performance Monitoring.

    Wird nur aktiviert, wenn eine gültige DSN übergeben wird (Standard im Dev/Test-Betrieb: None).
    """
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            traces_sample_rate=0.2,     # 20 % der HTTP-Transaktionen für Performance-Tracing erfassen
            profiles_sample_rate=0.2,   # 20 % Profiling-Rate zur CPU-/Speicher-Analyse nutzen
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
        )
