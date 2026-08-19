from typing import List, Optional

from sqlmodel import Field, SQLModel

from app.schemas.item import ItemResponse
from app.schemas.spell import SpellResponse


class CharacterBase(SQLModel):
    """Gemeinsames Basis-Schema für D&D-Charaktere.
    Enthält alle Attribute, die sowohl beim Erstellen als auch beim Lesen benötigt werden.
    """

    name: str
    character_class: str
    lvl: int = Field(default=1, ge=1)
    stat_str: int = Field(default=1, ge=1)
    stat_dex: int = Field(default=1, ge=1)
    stat_con: int = Field(default=1, ge=1)
    stat_int: int = Field(default=1, ge=1)
    stat_wis: int = Field(default=1, ge=1)
    stat_cha: int = Field(default=1, ge=1)


class CharacterCreate(CharacterBase):
    """Pydantic-Schema für eingehende POST-Requests zur Erstellung eines Charakters."""

    pass


class CharacterResponse(CharacterBase):
    """Pydantic-Schema für API-Antworten eines einzelnen Charakters ohne Relationen."""

    id: int


class CharacterReadWithRelations(SQLModel):
    """Response-Modell für API-Antworten mit aufgelösten Relationen (Items & Spells).
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
    items: List[ItemResponse] = []
    spells: List[SpellResponse] = []
