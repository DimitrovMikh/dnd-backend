"""API Router für Zaubersprüche.
Stellt CRUD-Endpunkte für das Verwalten von Zaubersprüchen bereit.
"""

from typing import Annotated

from app.core.security import RoleChecker
from app.database import get_session
from app.db.models.spell import Spell
from app.db.models.user import User, UserRole
from app.schemas.spell import SpellCreate
from app.services import spell_service
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()

# Instanz für DM & Admin Rechte erstellen
allow_dm_or_admin = RoleChecker([UserRole.DUNGEON_MASTER, UserRole.ADMIN])


@router.get("/", response_model=list[Spell])
async def read_spells(db: Annotated[AsyncSession, Depends(get_session)]):
    """Ruft eine Liste aller registrierten Zaubersprüche ab."""
    return await spell_service.get_all_spells(db)


@router.get("/{spell_id}", response_model=Spell)
async def read_spell(spell_id: int, db: Annotated[AsyncSession, Depends(get_session)]):
    """Ruft die Details eines einzelnen Zauberspruchs anhand seiner ID ab."""
    return await spell_service.get_spell_by_id(db, spell_id)


@router.post("/", response_model=Spell, status_code=status.HTTP_201_CREATED)
async def create_spell(
    spell: SpellCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(allow_dm_or_admin)],
):
    """Erstellt einen neuen Zauberspruch in der Datenbank.
    Nur für Nutzer mit den Rollen 'dungeon_master' oder 'admin'.
    """
    return await spell_service.create_spell(db, spell)
