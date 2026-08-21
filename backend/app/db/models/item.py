from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.character import Character


class ItemRarity(str, Enum):
    """Aufzählung der Verfügbarkeits- und Seltenheitsstufen von Items."""

    COMMON = "common"
    RARE = "rare"
    MYTHICAL = "mythical"
    LEGENDARY = "legendary"


class Item(SQLModel, table=True):
    """Haupt-Datenbankmodell für Items.
    Verknüpft das Item optional mit seinem Besitzer (Character).
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str
    rarity: ItemRarity
    worth: int = Field(
        default=0, ge=0, description="Das Item muss 0 Gold oder höher kosten"
    )
    description: str | None = None
    damage_dice: str

    # 1:N Fremdschlüssel-Beziehung zu Character
    # ondelete="SET NULL": Wenn der Charakter gelöscht wird, bleibt das Item ohne Besitzer existieren.
    character_id: int | None = Field(
        default=None,
        foreign_key="character.id",
        ondelete="SET NULL",
    )

    character: Optional["Character"] = Relationship(back_populates="items")
