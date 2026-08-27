from sqlmodel import SQLModel

from app.db.models.spell import SpellSchool


class SpellBase(SQLModel):
    """Basis-Schema für Zaubersprüche."""

    name: str
    lvl: int
    school: SpellSchool


class SpellCreate(SpellBase):
    """Pydantic-Schema für die Erstellung neuer Zaubersprüche."""


class SpellResponse(SpellBase):
    """Pydantic-Schema für API-Antworten von Zaubersprüchen."""

    id: int
