"""API Router für Zaubersprüche.
Stellt CRUD-Endpunkte für das Verwalten von Zaubersprüchen bereit.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import RoleChecker
from app.database import get_session
from app.models.spells import Spell, SpellCreate
from app.models.users import User, UserRole

router = APIRouter()

# Instanz für DM & Admin Rechte erstellen
allow_dm_or_admin = RoleChecker([UserRole.DUNGEON_MASTER, UserRole.ADMIN])


@router.get("/", response_model=List[Spell])
async def read_spells(db: AsyncSession = Depends(get_session)):
    """Ruft eine Liste aller registrierten Zaubersprüche ab."""
    statement = select(Spell)
    results = await db.exec(statement)
    return results.all()


@router.get("/{spell_id}", response_model=Spell)
async def read_spell(spell_id: int, db: AsyncSession = Depends(get_session)):
    """Ruft die Details eines einzelnen Zauberspruchs anhand seiner ID ab."""
    db_spell = await db.get(Spell, spell_id)
    if not db_spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Spell existiert noch nicht. | Spell-ID nicht gefunden."
        )
    return db_spell


@router.post("/", response_model=Spell, status_code=status.HTTP_201_CREATED)
async def create_spell(
    spell: SpellCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(allow_dm_or_admin),
):
    """Erstellt einen neuen Zauberspruch in der Datenbank.
    Nur für Nutzer mit den Rollen 'dungeon_master' oder 'admin'.
    """
    db_spell = Spell.model_validate(spell)
    db.add(db_spell)
    await db.commit()
    await db.refresh(db_spell)
    return db_spell