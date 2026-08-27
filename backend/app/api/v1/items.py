"""API Router für Gegenstände / Items.
Stellt CRUD-Endpunkte für das Erstellen und Abrufen von Items bereit.
"""

from typing import Annotated

from app.core.security import RoleChecker
from app.database import get_session
from app.db.models.item import Item
from app.db.models.user import User, UserRole
from app.schemas.item import ItemCreate
from app.services import item_service
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()

# Instanz für DM & Admin Rechte erstellen
allow_dm_or_admin = RoleChecker([UserRole.DUNGEON_MASTER, UserRole.ADMIN])


@router.get("/", response_model=list[Item])
async def read_items(db: Annotated[AsyncSession, Depends(get_session)]):
    """Ruft eine Liste aller in der Datenbank registrierten Items ab."""
    return await item_service.get_all_items(db)


@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int, db: Annotated[AsyncSession, Depends(get_session)]):
    """Ruft die Details eines einzelnen Items anhand seiner ID ab."""
    return await item_service.get_item_by_id(db, item_id)


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(allow_dm_or_admin)],
):
    """Erstellt ein neues Item in der Datenbank.
    Nur für Nutzer mit den Rollen 'dungeon_master' oder 'admin'.
    """
    return await item_service.create_item(db, item)
