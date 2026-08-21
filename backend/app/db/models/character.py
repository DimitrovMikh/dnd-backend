from typing import TYPE_CHECKING

from app.db.models.spell import CharacterSpellLink
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.item import Item
    from app.db.models.spell import Spell


class Character(SQLModel, table=True):
    """Haupt-Datenbankmodell für Charaktere.
    Verknüpft Inventar-Items (1:N) und Zaubersprüche (N:M via Link-Tabelle).
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str
    character_class: str
    lvl: int = Field(default=1, ge=1)
    stat_str: int = Field(default=1, ge=1)
    stat_dex: int = Field(default=1, ge=1)
    stat_con: int = Field(default=1, ge=1)
    stat_int: int = Field(default=1, ge=1)
    stat_wis: int = Field(default=1, ge=1)
    stat_cha: int = Field(default=1, ge=1)

    items: list["Item"] = Relationship(back_populates="character")
    spells: list["Spell"] = Relationship(
        back_populates="characters",
        link_model=CharacterSpellLink,
    )
