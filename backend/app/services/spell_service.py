"""Business Logic / Service Layer für Zaubersprüche.
Enthält D&D-Regelprüfungen sowie Datenbank-Operationen für Spells.
"""
from typing import List

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import SpellAlreadyKnownError, SpellLevelTooLowError
from app.db.models.character import Character
from app.db.models.spell import Spell
from app.schemas.spell import SpellCreate


def validate_spell_learning(character: Character, spell: Spell) -> None:
    """Prüft die D&D-Regeln für das Erlernen eines Zauberspruchs.

    Raises:
        SpellAlreadyKnownError: Wenn der Zauberspruch bereits gelernt wurde.
        SpellLevelTooLowError: Wenn das Zauber-Level höher als das Charakter-Level ist.
    """
    if any(s.id == spell.id for s in character.spells):
        raise SpellAlreadyKnownError(spell_name=spell.name)

    if spell.lvl > character.lvl:
        raise SpellLevelTooLowError(
            character_lvl=character.lvl, spell_lvl=spell.lvl
        )

    return None


async def get_all_spells(session: AsyncSession) -> List[Spell]:
    """Ruft eine Liste aller registrierten Zaubersprüche ab."""
    statement = select(Spell)
    results = await session.exec(statement)
    return list(results.all())


async def get_spell_by_id(session: AsyncSession, spell_id: int) -> Spell:
    """Ruft die Details eines einzelnen Zauberspruchs anhand seiner ID ab.

    Raises:
        HTTPException (404): Wenn der Spell nicht existiert.
    """
    db_spell = await session.get(Spell, spell_id)
    if not db_spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spell existiert noch nicht. | Spell-ID nicht gefunden.",
        )
    return db_spell


async def create_spell(session: AsyncSession, spell_in: SpellCreate) -> Spell:
    """Erstellt einen neuen Zauberspruch in der Datenbank."""
    db_spell = Spell.model_validate(spell_in)
    session.add(db_spell)
    await session.commit()
    await session.refresh(db_spell)
    return db_spell