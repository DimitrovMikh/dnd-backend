from enum import Enum

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    """Aufzählung der möglichen Nutzer-Rollen."""

    PLAYER = "player"
    DUNGEON_MASTER = "dungeon_master"
    ADMIN = "admin"


class User(SQLModel, table=True):
    """Haupt-Datenbankmodell für Benutzer.
    Speichert das gehashte Passwort sicher in der Datenbank.
    """

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        unique=True, index=True, description="Eindeutiger Benutzername"
    )
    email: str = Field(
        unique=True, index=True, description="Eindeutige E-Mail-Adresse"
    )
    is_active: bool = Field(
        default=True, description="Status, ob das Konto aktiv ist"
    )
    role: UserRole = Field(
        default=UserRole.PLAYER, description="Rolle des Benutzers im System"
    )
    hashed_password: str = Field(
        description="Argon2/Bcrypt-Hash des Benutzerpassworts"
    )
