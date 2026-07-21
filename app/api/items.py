from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.items import Item, ItemCreate
from app.database import get_session

router = APIRouter()

@router.get("/")
async def show_all_items(db: AsyncSession = Depends(get_session)):
    """
    Ruft eine Liste aller in der Datenbank registrierten Items ab.
    """
    statement = select(Item)
    results = await db.exec(statement)
    items = results.all()
    return items

@router.get("/{item_id}")
async def show_single_item(
    item_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    Ruft die Details eines einzelnen Items anhand seiner ID ab.
    """
    db_item = await db.get(Item, item_id)

    if not db_item:
        raise HTTPException(
            status_code = 404,
            detail = "Item existiert noch nicht. | Item ID nicht gefunden."
        )
    return db_item

@router.post("/", response_model=Item)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Erstellt ein neues Item in der Datenbank.
    """
    db_item = Item.model_validate(item)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item