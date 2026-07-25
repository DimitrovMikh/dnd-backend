from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel 

# TYPE_CHECKING verhindert zirkuläre Imports zur Laufzeit
if TYPE_CHECKING:
    from app.models.characters import Character


class ItemRarity(str, Enum):
    """Aufzählung der Verfügbarkeits- und Seltenheitsstufen von Items."""

    COMMON = "common"
    RARE = "rare"
    MYTHICAL = "mythical"
    LEGENDARY = "legendary"


class ItemBase(SQLModel):
    """Basis-Schema für Gegenstände/Waffen im Spiel.
    Definiert Grundwerte wie Seltenheit, Goldwert, Beschreibung und Schäden.
    """

    name: str
    rarity: ItemRarity
    worth: int = Field(
        default=0, ge=0, description="Das Item muss 0 Gold oder höher kosten"
    )
    description: Optional[str] = None
    damage_dice: str

    # 1:N Fremdschlüssel-Beziehung zu Character
    # ondelete="SET NULL": Wenn der Charakter gelöscht wird, bleibt das Item ohne Besitzer existieren.
    character_id: Optional[int] = Field(
        default=None,
        foreign_key="character.id",
        ondelete="SET NULL"
    )


class Item(ItemBase, table = True):
    """Haupt-Datenbankmodell für Items.
    Verknüpft das Item optional mit seinem Besitzer (Character).
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    character: Optional["Character"] = Relationship(back_populates="items")


class ItemCreate(ItemBase):
    """Pydantic-Schema zur Validierung eingehender POST-Requests beim Erstellen von Items."""

    pass