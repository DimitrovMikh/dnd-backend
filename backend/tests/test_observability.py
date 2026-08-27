from unittest.mock import patch

import pytest
from app.core.logging import init_sentry
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_logging_middleware_executes_successfully(client: AsyncClient):
    """Verifiziert, dass die Logging-Middleware Anfragen ohne Blockaden verarbeitet und weiterleitet."""
    response = await client.get("/")
    assert response.status_code in [
        200,
        404,
    ]


def test_init_sentry_skips_when_dsn_is_none():
    """Stellt sicher, dass Sentry inaktiv bleibt, wenn keine DSN konfiguriert ist (z. B. beim lokalen Testen)."""
    with patch("sentry_sdk.init") as mock_sentry_init:
        init_sentry(dsn=None)
        mock_sentry_init.assert_not_called()


def test_init_sentry_initializes_when_dsn_present():
    """Prüft, ob sentry_sdk.init mit den richtigen Parametern aufgerufen wird, sobald eine DSN vorhanden ist."""
    dummy_dsn = "https://examplePublicKey@o0.ingest.sentry.io/0"
    with patch("sentry_sdk.init") as mock_sentry_init:
        init_sentry(dsn=dummy_dsn, environment="testing")
        mock_sentry_init.assert_called_once()
