import re
from enum import Enum
from typing import Optional

from pydantic import field_validator
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

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validiert die Komplexität des Klartext-Passworts nach OWASP-Sicherheitsstandards.
        
        Prüft Länge, Groß-/Kleinbuchstaben, Zahlen und Sonderzeichen vor der Verarbeitung.
        Wirft bei Regelverstößen einen ValueError, den FastAPI in HTTP 422 übersetzt.
        """
        # 1. Mindestlänge prüfen (mindestens 9 Zeichen)
        if len(v) < 9:
            raise ValueError(
                "Das Passwort muss mindestens 9 Zeichen lang sein."
            )

        # 2. Mindestens ein Großbuchstabe (A-Z)
        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "Das Passwort muss mindestens einen Großbuchstaben enthalten."
            )
        
        # 3. Mindestens ein Kleinbuchstabe (a-z)
        if not re.search(r"[a-z]", v):
            raise ValueError(
                "Das Passwort muss mindestens einen Kleinbuchstaben enthalten."
            )

        # 4. Mindestens eine Zahl (0-9)
        if not re.search(r"\d", v):
            raise ValueError(
                "Das Passwort muss mindestens eine Zahl enthalten."
            )
        
        # 5. Mindestens ein Sonderzeichen (alles außer Alphanumerisch)
        if not re.search("[^a-zA-Z0-9]", v):
            raise ValueError(
                "Das Passwort muss mindestens ein Sonderzeichen enthalten."
            )

        return v


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