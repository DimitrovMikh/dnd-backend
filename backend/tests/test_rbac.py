import pytest


@pytest.mark.asyncio
async def test_create_spell_as_player_forbidden(client):
    """Prüft, ob ein normaler Spieler (PLAYER) beim Versuch, einen Spell zu erstellen, mit HTTP 403 abgelehnt wird."""
    # 1. Player-Account registrieren & einloggen
    await client.post(
        "/auth/register",
        json={
            "username": "simpleplayer",
            "email": "player@example.com",
            "password": "Password123!",
            "role": "player",
        },
    )
    login_res = await client.post(
        "/auth/login",
        json={"username": "simpleplayer", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]

    # 2. Versuchen, einen Spell mit Player-Token zu erstellen
    spell_payload = {"name": "Feuerball", "lvl": 3, "school": "hervorrufung"}
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/spells/", json=spell_payload, headers=headers
    )

    # 3. Assert: 403 Forbidden
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Zugriff verweigert: Unzureichende Berechtigungen."
    )


@pytest.mark.asyncio
async def test_create_spell_as_dungeon_master_success(client):
    """Prüft, ob ein Dungeon Master (DUNGEON_MASTER) erfolgreich Spells erstellen darf (HTTP 201)."""
    # 1. Dungeon Master Account registrieren & einloggen
    await client.post(
        "/auth/register",
        json={
            "username": "greatdm",
            "email": "dm@example.com",
            "password": "Password123!",
            "role": "dungeon_master",
        },
    )
    login_res = await client.post(
        "/auth/login",
        json={"username": "greatdm", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]

    # 2. Spell als DM erstellen
    spell_payload = {"name": "Heilendes Wort", "lvl": 1, "school": "bannmagie"}
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/spells/", json=spell_payload, headers=headers
    )

    # 3. Assert: 201 Created
    assert response.status_code == 201
    assert response.json()["name"] == "Heilendes Wort"