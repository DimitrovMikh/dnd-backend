import pytest
from app.core.security import create_access_token, get_hash_password, verify_password

# --- REGISTRIERUNGS-TESTS ---


@pytest.mark.asyncio
async def test_register_user_success(client):
    """Prüft die erfolgreiche Registrierung eines neuen Benutzers."""
    # 1. ARRANGE: Payload definieren
    payload = {
        "username": "dungeonlord",
        "email": "lord@example.com",
        "password": "SecurePassword123!",
        "role": "dungeon_master",
    }

    # 2. ACT: POST-Request ausführen
    response = await client.post("/auth/register", json=payload)

    # 3. ASSERT: Response verifizieren
    assert response.status_code == 201
    data = response.json()

    assert data["username"] == "dungeonlord"
    assert data["email"] == "lord@example.com"
    assert data["role"] == "dungeon_master"
    assert "id" in data

    # Sicherheits-Check: Keine Passwörter im Response Payload enthalten
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_user_duplicate_error(client):
    """Prüft, ob bei doppeltem Usernamen oder E-Mail ein 400-Fehler geworfen

    wird.
    """
    payload = {
        "username": "shadowrunner",
        "email": "runner@example.com",
        "password": "Password123!",
    }

    # Erster Versuch: Erfolgreich
    first_response = await client.post("/auth/register", json=payload)
    assert first_response.status_code == 201

    # Zweiter Versuch mit identischen Daten: Fehlgeschlagen
    second_response = await client.post("/auth/register", json=payload)
    assert second_response.status_code == 400

    data = second_response.json()
    assert data["detail"] == "Nutzername oder E-Mail-Adresse bereits vergeben."


# --- LOGIN-TESTS ---


@pytest.mark.asyncio
async def test_login_user_success(client):
    """Prüft den erfolgreichen Login und den Erhalt eines JWT Access Tokens."""
    # 1. ARRANGE: User registrieren
    register_payload = {
        "username": "loginknight",
        "email": "knight@example.com",
        "password": "StrongPassword123!",
    }
    await client.post("/auth/register", json=register_payload)

    # 2. ACT: Login durchführen
    login_payload = {
        "username": "loginknight",
        "password": "StrongPassword123!",
    }
    response = await client.post("/auth/login", json=login_payload)

    # 3. ASSERT: Status 200 OK & Token-Struktur verifizieren
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user_wrong_password(client):
    """Prüft, ob der Login bei falschem Passwort mit HTTP 401 fehlschlägt."""
    # 1. ARRANGE: User registrieren
    register_payload = {
        "username": "paladin",
        "email": "paladin@example.com",
        "password": "CorrectPassword123!",
    }
    await client.post("/auth/register", json=register_payload)

    # 2. ACT: Login mit falschem Passwort
    login_payload = {
        "username": "paladin",
        "password": "WRONGPassword123!",
    }
    response = await client.post("/auth/login", json=login_payload)

    # 3. ASSERT: Status 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert (
        data["detail"]
        == "Ungültige Anmeldedaten (Benutzername oder Passwort falsch)."
    )


@pytest.mark.asyncio
async def test_login_user_not_found(client):
    """Prüft, ob der Login bei einem nicht existierenden User mit HTTP 401

    fehlschlägt.
    """
    login_payload = {
        "username": "ghost_user",
        "password": "AnyPassword123!",
    }
    response = await client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    data = response.json()
    assert (
        data["detail"]
        == "Ungültige Anmeldedaten (Benutzername oder Passwort falsch)."
    )


# --- AUTORISIERUNGS-TESTS (GESCHÜTZTE ROUTEN) ---


@pytest.mark.asyncio
async def test_read_users_me_success(client):
    """Prüft den Zugriff auf geschützte Routen mit einem gültigen Bearer Token."""
    # 1. ARRANGE: User registrieren & einloggen
    reg_payload = {
        "username": "authzuser",
        "email": "authz@example.com",
        "password": "Password123!",
    }
    await client.post("/auth/register", json=reg_payload)

    login_res = await client.post(
        "/auth/login",
        json={"username": "authzuser", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]

    # 2. ACT: Geschützte Route mit Authorization-Header aufrufen
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/auth/me", headers=headers)

    # 3. ASSERT: Profildaten erfolgreich zurückgeliefert
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "authzuser"
    assert data["email"] == "authz@example.com"


@pytest.mark.asyncio
async def test_read_users_me_unauthorized(client):
    """Prüft, ob der Zugriff auf geschützte Routen ohne Token mit HTTP 401 abgelehnt wird."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


# --- ARGON2 & REFRESH-TOKEN-TESTS ---


@pytest.mark.asyncio
async def test_argon2_password_hashing():
    """Verifiziert, dass der PassLib-Kontext Argon2id als Hash-Algorithmus nutzt
    und Passwörter korrekt abgeglichen werden.
    """
    secret_password = "MeinGeheimesD&DPassword2026!"
    wrong_password = "FalschesPasswort123!"

    # Passwort hashen
    hashed_password = get_hash_password(secret_password)

    # Assertions
    assert hashed_password.startswith("$argon2id$")
    assert verify_password(secret_password, hashed_password) is True
    assert verify_password(wrong_password, hashed_password) is False


@pytest.mark.asyncio
async def test_refresh_token_success(client):
    """Prüft den kompletten Refresh-Cycle: Registrierung, Login (Cookie wird gesetzt)
    und erfolgreiche Erneuerung des Access Tokens über /auth/refresh.
    """
    # 1. ARRANGE: User registrieren & einloggen
    user_data = {
        "username": "refreshtestuser",
        "email": "refreshtest@example.com",
        "password": "SecurePassword123!",
    }
    await client.post("/auth/register", json=user_data)
    login_res = await client.post("/auth/login", json=user_data)

    # 2. ASSERT: HttpOnly-Cookie vorhanden
    assert "refresh_token" in login_res.cookies

    # 3. ACT: Cookie auf Client setzen & /auth/refresh aufrufen
    client.cookies.update(login_res.cookies)
    refresh_res = await client.post("/auth/refresh")

    # 4. ASSERT: Neues Access Token erhalten
    assert refresh_res.status_code == 200
    res_json = refresh_res.json()
    assert "access_token" in res_json
    assert res_json["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_missing_cookie(client):
    """Prüft, ob der Aufruf von /auth/refresh ohne Cookie mit HTTP 401 abgelehnt wird."""
    response = await client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh Token fehlt."


@pytest.mark.asyncio
async def test_refresh_token_invalid_type(client):
    """Prüft, ob der Versuch, ein Access Token als Refresh Cookie einzuschleusen,
    mit HTTP 401 abgefangen wird.
    """
    # Access Token (type: access) als mehere Refresh Token Cookie setzen
    access_token = create_access_token(
        data={"sub": "fakeuser", "role": "player"}
    )

    client.cookies.update({"refresh_token": access_token})
    response = await client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Ungültiger Token-Typ."


@pytest.mark.asyncio
async def test_register_user_weak_password(client):
    """ Prüft, ob die Registrierung bei einem schwachen Passwort mit HTTP 422 abgelehnt wird."""
    payload = {
        "username": "weakuser",
        "email": "weak@example.com",
        "password": "schwach",
    }

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 422
    assert "password" in response.text