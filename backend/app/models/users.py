from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    """Aufzählung der möglichen Nutzer-Rollen."""

    PLAYER = "player"
    DUNGEON_MASTER = "dungeon_master"
    ADMIN = "admin"

class UserBase(SQLModel):
    """Gemeinsames Basis-Schema für Benutzerdaten.
    Enthält allgemeine Felder, die weder Passwort noch ID preisgeben.
    """

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

class User(UserBase, table=True):
    """Haupt-Datenbankmodell für Benutzer.
    Speichert das gehashte Passwort sicher in der Datenbank.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(
        description="Bcrypt-Hash des Benutzerpassworts"
    )

class UserCreate(UserBase):
    """Pydantic-Schema für eingehende Registrierungs-Requests.
    Enthält das Passwort im Klartext vor dem Hashing.
    """
    password: str = Field(description="Klartext-Passwort des Benutzers")

class UserResponse(UserBase):
    """Pydantic-Schema für API-Antworten.
    Gibt Benutzerdaten ohne sensitive Informationen (Passwort/Hash) zurück.
    """
    id: int

class UserLogin(SQLModel):
    """Schema für den eingehenden Login-Request."""

    username: str = Field(description="Benutzername für die Anmeldung")
    password: str = Field(description="Klartext-Passwort für die Anmeldung")


class Token(SQLModel):
    """Schema für die JWT-Response nach erfolgreichem Login."""

    access_token: str = Field(
        description="Signierter JWT Access Token String"
    )
    token_type: str = Field(
        default="bearer", description="OAuth2 Token-Typ (Standard: bearer)"
    )