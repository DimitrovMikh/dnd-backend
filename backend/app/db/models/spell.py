from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.character import Character


class CharacterSpellLink(SQLModel, table=True):
    """N:M-Verknüpfungstabelle (Junction Table) zwischen Character und Spell.
    Koppelt Primärschlüssel beider Modelle als zusammengesetzten Primärschlüssel.
    """

    character_id: Optional[int] = Field(
        default=None, foreign_key="character.id", primary_key=True
    )
    spell_id: Optional[int] = Field(
        default=None, foreign_key="spell.id", primary_key=True
    )


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


class Spell(SQLModel, table=True):
    """Haupt-Datenbankmodell für Zaubersprüche."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    lvl: int
    school: SpellSchool

    characters: List["Character"] = Relationship(
        back_populates="spells",
        link_model=CharacterSpellLink,
    )
