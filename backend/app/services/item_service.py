"""Business Logic / Service Layer für Items / Gegenstände."""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.item import Item
from app.schemas.item import ItemCreate


async def get_all_items(session: AsyncSession) -> List[Item]:
    """Ruft alle Items aus der Datenbank ab."""
    statement = select(Item)
    results = await session.exec(statement)
    return list(results.all())


async def get_item_by_id(session: AsyncSession, item_id: int) -> Item:
    """Ruft ein einzelnes Item anhand seiner ID ab.

    Raises:
        HTTPException (404): Wenn das Item nicht existiert.
    """
    db_item = await session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item existiert noch nicht. | Item ID nicht gefunden.",
        )
    return db_item


async def create_item(session: AsyncSession, item_in: ItemCreate) -> Item:
    """Erstellt ein neues Item in der Datenbank."""
    db_item = Item.model_validate(item_in)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item
