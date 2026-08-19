"""Integrationstests für die Character-Endpoints.
Prüft die API-Routen, D&D-Regelvalidierungen und Fehlermeldungen.
"""
import pytest

from app.db.models.character import Character
from app.db.models.spell import Spell

@pytest.mark.asyncio
async def test_learn_spell_level_too_low(client, async_session):
    """Prüft, ob ein Fehler (HTTP 400) geworfen wird, wenn der Zauber-Level höher ist als das Charakter-Level."""
    # 1. ARRANGE (Testdaten vorbereiten)
    character = Character(
        name="Mage Azun",
        character_class="Wizzard",
        lvl=1,
        stat_str=8,
        stat_dex=14,
        stat_con=12,
        stat_int=16,
        stat_wis=10,
        stat_cha=12
    )
    spell = Spell(name="Wunsch", lvl=9, school="verwandlung")

    async_session.add(character)
    async_session.add(spell)
    await async_session.commit()
    await async_session.refresh(character)
    await async_session.refresh(spell)

    # 2. ACT (Request abschicken)
    response = await client.post(f"/characters/{character.id}/spells/{spell.id}")

    # 3. ASSERT (Ergebnisse prüfen)
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "SPELL_LEVEL_TOO_LOW"


@pytest.mark.asyncio
async def test_learn_spell_success(client, async_session):
    """Prüft das erfolgreiche Erlernen eines Zauberspruchs inkl. Datenbankverknüpfung."""
    # 1. ARRANGE
    character = Character(
        name="Mage Belix",
        character_class="Wizzard",
        lvl=5,
        stat_str=8,
        stat_dex=14,
        stat_con=12,
        stat_int=18,
        stat_wis=10,
        stat_cha=12
    )
    spell = Spell(name="Licht", lvl=1, school="verwandlung")

    async_session.add(character)
    async_session.add(spell)
    await async_session.commit()
    await async_session.refresh(character)
    await async_session.refresh(spell)

    # 2. ACT
    response = await client.post(f"/characters/{character.id}/spells/{spell.id}")

    # 3. ASSERT
    assert response.status_code == 200

    # Verifizieren, dass die Verknüpfung auch in der DB vorhanden ist
    await async_session.refresh(character, ["spells"])
    assert spell in character.spells


@pytest.mark.asyncio
async def test_learn_spell_already_known(client, async_session):
    """Prüft, ob ein Fehler (HTTP 400) geworfen wird, wenn ein Zauberspruch doppelt gelernt wird."""
    # 1. ARRANGE
    character = Character(
        name="Mage Carl",
        character_class="Wizzard",
        lvl=1,
        stat_str=12,
        stat_dex=14,
        stat_con=8,
        stat_int=16,
        stat_wis=10,
        stat_cha=12
    )
    spell = Spell(name="Licht", lvl=1, school="verwandlung")

    async_session.add(character)
    async_session.add(spell)
    await async_session.commit()
    await async_session.refresh(character)
    await async_session.refresh(spell)

    # 2. ACT: Erster Versuch (Erfolgreich)
    response = await client.post(f"/characters/{character.id}/spells/{spell.id}")
    assert response.status_code == 200

    # 3. ACT: Zweiter Versuch (Duplikat)
    response = await client.post(f"/characters/{character.id}/spells/{spell.id}")

    # 4. ASSERT
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "SPELL_ALREADY_KNOWN"