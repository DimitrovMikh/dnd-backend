from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from app.models.characters import Character

class CharacterSpellLink(SQLModel, table=True):
    """
    N:M-Verknüpfungstabelle (Junction Table) zwischen Character und Spell.
    Koppelt Primärschlüssel beider Modelle als zusammengesetzten Primärschlüssel.
    """
    character_id: Optional[int] = Field(default=None, foreign_key="character.id", primary_key=True)
    spell_id: Optional[int] = Field(default=None, foreign_key="spell.id", primary_key=True)

class SpellSchool(str, Enum):
    """Aufzählung der offiziellen D&D 5e Magieschulen."""
    BANNMAGIE = "bannmagie"
    BESCHWOERUNG = "beschwörung"
    ERKENNTNISMAGIE = "erkenntnismagie"
    HERVORRUFUNG = "hervorrufung"
    ILLUSION = "illusion"
    NEKROMATIE = "nekromantie"
    VERWANDLUNG = "verwandlung"
    VERZAUBERUNG = "verzauberung"

class SpellBase(SQLModel):
    """Basis-Schema für Zaubersprüche."""
    name: str
    lvl: int
    school: SpellSchool

class Spell(SpellBase, table=True):
    """Haupt-Datenbankmodell für Zaubersprüche."""
    id: Optional[int] = Field(default=None, primary_key=True)
    character: List["Character"] = Relationship(
        back_populates="spells",
        link_model=CharacterSpellLink
    )

class SpellCreate(SpellBase):
    """Pydantic-Schema für die Erstellung neuer Zaubersprüche."""
    pass