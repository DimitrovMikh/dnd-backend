
from sqlmodel import Field, SQLModel

from app.db.models.item import ItemRarity


class ItemBase(SQLModel):
    """Basis-Schema für Gegenstände/Waffen im Spiel.
    Definiert Grundwerte wie Seltenheit, Goldwert, Beschreibung und Schäden.
    """

    name: str
    rarity: ItemRarity
    worth: int = Field(
        default=0, ge=0, description="Das Item muss 0 Gold oder höher kosten"
    )
    description: str | None = None
    damage_dice: str
    character_id: int | None = None


class ItemCreate(ItemBase):
    """Pydantic-Schema zur Validierung eingehender POST-Requests beim Erstellen von Items."""



class ItemResponse(ItemBase):
    """Pydantic-Schema für API-Antworten von Items."""

    id: int
