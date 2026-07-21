from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.spells import Spell, SpellCreate
from app.database import get_session

router = APIRouter()

@router.get("/")
async def show_all_spell(db: AsyncSession = Depends(get_session)):
    statement = select(Spell)
    results = await db.exec(statement)
    spells = results.all()
    return spells

@router.get("/{spell_id}")
async def show_single_spell(spell_id: int, db: AsyncSession = Depends(get_session)):
    db_spell = await db.get(Spell, spell_id)

    if not db_spell:
        raise HTTPException(
            status_code = 404,
            detail = "Spell existiert noch nicht. | Spell ID nicht gefunden."
        )
    return db_spell

@router.post("/", response_model=Spell)
async def create_spell(spell: SpellCreate, db: AsyncSession = Depends(get_session)):
    db_spell = Spell.model_validate(spell)
    db.add(db_spell)
    await db.commit()
    await db.refresh(db_spell)
    return db_spell