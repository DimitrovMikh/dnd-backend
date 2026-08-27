"""API Router für Charaktere.
Stellt Endpunkte für CRUD-Operationen und D&D-Regellogik (Zauber lernen) bereit.
"""

from typing import Annotated

from app.database import get_session
from app.db.models.character import Character
from app.schemas.character import CharacterCreate, CharacterReadWithRelations
from app.services import character_service
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.get("/", response_model=list[CharacterReadWithRelations])
async def read_characters(db: Annotated[AsyncSession, Depends(get_session)]):
    """Ruft alle Charaktere aus der Datenbank ab.
    Verwendet Eager Loading für Items und Spells.
    """
    return await character_service.get_all_characters(db)


@router.get("/{character_id}", response_model=CharacterReadWithRelations)
async def read_character(
    character_id: int, db: Annotated[AsyncSession, Depends(get_session)]
):
    """Ruft einen einzelnen Charakter anhand seiner ID ab."""
    return await character_service.get_character_by_id(db, character_id)


@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character(
    character: CharacterCreate, db: Annotated[AsyncSession, Depends(get_session)]
):
    """Erstellt einen neuen Charakter in der Datenbank."""
    return await character_service.create_character(db, character)


@router.post("/{character_id}/spells/{spell_id}")
async def learn_spell(
    character_id: int,
    spell_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Verknüpft einen Charakter mit einem Zauberspruch über die N:M-Link-Tabelle,
    nachdem alle D&D-Regeln im Service geprüft wurden.
    """
    await character_service.learn_spell_for_character(db, character_id, spell_id)
    return {
        "message": f"Character {character_id} hat Zauberspruch {spell_id} erfolgreich gelernt!"
    }
