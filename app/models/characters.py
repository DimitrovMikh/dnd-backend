from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from app.models.spells import CharacterSpellLink

# TYPE_CHECKING verhindert zirkuläre Import-Schleifen zur Laufzeit,
# erlaubt dem Language Server / Linter aber trotzdem die Typenprüfung.
if TYPE_CHECKING:
    from app.models.items import Item
    from app.models.spells import Spell

class CharacterBase(SQLModel):
    """
    Gemeinsames Basis-Schema für D&D-Charaktere.
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

class Character(CharacterBase, table=True):
    """
    Haupt-Datenbankmodell für Charaktere.
    Verknüpft Inventar-Items (1:N) und Zaubersprüche (N:M via Link-Tabelle).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["Item"] = Relationship(back_populates="character")
    spells: List["Spell"] = Relationship(back_populates="character", link_model=CharacterSpellLink)

class CharacterCreate(CharacterBase):
    """Pydantic-Schema für eingehende POST-Requests zur Erstellung eines Charakters."""
    pass 