"""API Router für Charaktere.
Stellt Endpunkte für CRUD-Operationen und D&D-Regellogik (Zauber lernen) bereit.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.characters import Character, CharacterCreate
from app.models.items import Item
from app.models.spells import CharacterSpellLink, Spell
from app.services.spell_service import validate_spell_learning


class CharacterReadWithRelations(SQLModel):
    """Response-Modell für API-Antworten.
    Stellt sicher, dass Pydantic die mitgeladenen Items und Spells im JSON ausgibt.
    """

    id: int
    name: str
    character_class: str
    lvl: int
    stat_str: int
    stat_dex: int
    stat_con: int
    stat_int: int
    stat_wis: int
    stat_cha: int
    items: list[Item] = []
    spells: list[Spell] = []


router = APIRouter()


@router.get("/", response_model=list[CharacterReadWithRelations])
async def read_characters(db: AsyncSession = Depends(get_session)):
    """Ruft alle Charaktere aus der Datenbank ab.
    Verwendet `selectinload`, um 'items' und 'spells' per Eager Loading mitzufragen.
    """
    statement = (
        select(Character)
        .options(
            selectinload(Character.items),
            selectinload(Character.spells)
        )
    )
    results = await db.exec(statement)
    return results.all()


@router.get("/{character_id}", response_model=CharacterReadWithRelations)
async def read_character(
    character_id: int, db: AsyncSession = Depends(get_session)
):
    """Ruft einen einzelnen Charakter anhand seiner ID ab."""
    statement = (
        select(Character)
        .where(Character.id == character_id)
        .options(
            selectinload(Character.items),
            selectinload(Character.spells),
        )
    )
    result = await db.exec(statement)
    db_character = result.first()

    if not db_character:
        raise HTTPException(
            status_code = 404,
            detail = "Character existiert noch nicht. | Character ID nicht gefunden."
        )
    return db_character


@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character(
    character: CharacterCreate, db: AsyncSession = Depends(get_session)
):
    """Erstellt einen neuen Charakter in der Datenbank."""
    db_character = Character.model_validate(character)
    db.add(db_character)
    await db.commit()
    await db.refresh(db_character)
    return db_character


@router.post("/{character_id}/spells/{spell_id}")
async def learn_spell(
    character_id: int,
    spell_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Verknüpft einen Charakter mit einem Zauberspruch über die N:M-Link-Tabelle,
    nachdem alle D&D-Regeln im Service geprüft wurden.
    """

    statement = (
        select(Character)
        .where(Character.id == character_id)
        .options(selectinload(Character.spells))
    )
    result = await db.exec(statement)
    db_character = result.first()

    db_spell = await db.get(Spell, spell_id)

    if not db_character or not db_spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Charakter oder Zauberspruch nicht gefunden."
        )
    
    validate_spell_learning(db_character, db_spell)
    
    new_link = CharacterSpellLink(character_id=character_id, spell_id=spell_id)
    db.add(new_link)
    await db.commit()

    return {
        "message": f"Character {character_id} hat Zauberspruch {spell_id} erfolgreich gelernt!"
    }