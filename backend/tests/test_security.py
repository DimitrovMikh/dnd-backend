import pytest

from app.core.limiter import limiter


@pytest.mark.asyncio
async def test_cors_allowed_origin(client):
    """Prüft, ob Anfragen von einer erlaubten Origin die korrekten CORS-Header erhalten."""
    headers = {"Origin": "http://localhost:5173"}
    response = await client.get("/ping", headers=headers)

    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "http://localhost:5173"
    )
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_disallowed_origin(client):
    """Prüft, ob bei Anfragen von nicht freigegebenen Origins die CORS-Header fehlen."""
    headers = {"Origin": "http://malicious-website.com"}
    response = await client.get("/ping", headers=headers)

    assert response.status_code == 200
    # Der Browser blockiert den Zugriff, weil dieser Header in der Response fehlt:
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.asyncio
async def test_login_rate_limiting(client):
    """Prüft, ob nach 5 fehlerhaften Login-Versuchen der HTTP 429 Rate-Limit-Fehler greift."""
    # 1. Limiter aktivieren & Zähler aus vorherigen Tests leeren
    limiter.enabled = True
    if hasattr(limiter, "_storage"):
        limiter._storage.reset()

    login_payload = {
        "username": "ratelimit_user",
        "password": "WrongPassword123!",
    }

    try:
        # 2. 5 Anfragen senden (erlaubtes Kontingent ausschöpfen)
        for _ in range(5):
            res = await client.post("/auth/login", json=login_payload)
            assert res.status_code == 401

        # 3. 6. Anfrage senden -> Rate Limit muss greifen
        blocked_res = await client.post("/auth/login", json=login_payload)
        assert blocked_res.status_code == 429
        assert "Rate limit exceeded" in blocked_res.text
    finally:
        # 4. Nach dem Test wieder deaktivieren
        limiter.enabled = False