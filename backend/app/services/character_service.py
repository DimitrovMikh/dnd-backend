"""Business Logic / Service Layer für Charaktere."""

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.character import Character
from app.db.models.spell import CharacterSpellLink, Spell
from app.schemas.character import CharacterCreate
from app.services.spell_service import validate_spell_learning


async def get_all_characters(session: AsyncSession) -> list[Character]:
    """Ruft alle Charaktere aus der Datenbank ab (inkl. Eager Loading von items und spells)."""
    statement = (
        select(Character)
        .options(
            selectinload(Character.items),  # type: ignore[arg-type]
            selectinload(Character.spells), # type: ignore[arg-type]
        )
    )
    results = await session.exec(statement)
    return list(results.all())


async def get_character_by_id(
    session: AsyncSession, character_id: int
) -> Character:
    """Ruft einen einzelnen Charakter anhand seiner ID ab.

    Raises:
        HTTPException (404): Wenn der Charakter nicht existiert.
    """
    statement = (
        select(Character)
        .where(Character.id == character_id)
        .options(
            selectinload(Character.items),  # type: ignore[arg-type]
            selectinload(Character.spells), # type: ignore[arg-type]
        )
    )
    result = await session.exec(statement)
    db_character = result.first()

    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character existiert noch nicht. | Character ID nicht gefunden.",
        )
    return db_character


async def create_character(
    session: AsyncSession, character_in: CharacterCreate
) -> Character:
    """Erstellt einen neuen Charakter in der Datenbank."""
    db_character = Character.model_validate(character_in)
    session.add(db_character)
    await session.commit()
    await session.refresh(db_character)
    return db_character


async def learn_spell_for_character(
    session: AsyncSession, character_id: int, spell_id: int
) -> None:
    """Verknüpft einen Charakter mit einem Zauberspruch über die N:M-Link-Tabelle,
    nachdem alle D&D-Regeln validiert wurden.

    Raises:
        HTTPException (404): Wenn Charakter oder Zauberspruch nicht gefunden wird.
        SpellAlreadyKnownError / SpellLevelTooLowError: Bei D&D-Regelverstößen.
    """
    statement = (
        select(Character)
        .where(Character.id == character_id)
        .options(selectinload(Character.spells))    # type: ignore[arg-type]
    )
    result = await session.exec(statement)
    db_character = result.first()

    db_spell = await session.get(Spell, spell_id)

    if not db_character or not db_spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Charakter oder Zauberspruch nicht gefunden.",
        )

    validate_spell_learning(db_character, db_spell)

    new_link = CharacterSpellLink(
        character_id=character_id, spell_id=spell_id
    )
    session.add(new_link)
    await session.commit()
