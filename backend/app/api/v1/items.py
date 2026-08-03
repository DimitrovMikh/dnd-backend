"""API Router für Gegenstände / Items.
Stellt CRUD-Endpunkte für das Erstellen und Abrufen von Items bereit.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import RoleChecker
from app.database import get_session
from app.models.items import Item, ItemCreate
from app.models.users import User, UserRole

router = APIRouter()

# Instanz für DM & Admin Rechte erstellen
allow_dm_or_admin = RoleChecker([UserRole.DUNGEON_MASTER, UserRole.ADMIN])


@router.get("/", response_model=List[Item])
async def read_items(db: AsyncSession = Depends(get_session)):
    """Ruft eine Liste aller in der Datenbank registrierten Items ab."""
    statement = select(Item)
    results = await db.exec(statement)
    return results.all()


@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int, db: AsyncSession = Depends(get_session)):
    """Ruft die Details eines einzelnen Items anhand seiner ID ab."""
    db_item = await db.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Item existiert noch nicht. | Item ID nicht gefunden."
        )
    return db_item


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(allow_dm_or_admin),
):
    """Erstellt ein neues Item in der Datenbank.
    Nur für Nutzer mit den Rollen 'dungeon_master' oder 'admin'.
    """
    db_item = Item.model_validate(item)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item