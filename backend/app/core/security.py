from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.database import get_session
from app.db.models.user import User, UserRole

# OAuth2-Schema: Liest den 'Authorization: Bearer <token>' Header aus und aktiviert den Login-Button in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Konfiguration für Argon2id Hashing
password_hash = PasswordHash((Argon2Hasher(),))


# --- PASSWORT HASHING & VERIFIKATION ---


def get_hash_password(password: str) -> str:
    """Wandelt ein Klartext-Passwort mithilfe von Argon2 in einen sicheren Hash um."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Prüft, ob ein eingegebenes Klartext-Passwort zum gespeicherten Hash passt."""
    return password_hash.verify(plain_password, hashed_password)


# --- JWT TOKEN GENERIERUNG ---


def create_access_token(
    data: dict, expire_delta: timedelta | None = None
) -> str:
    """Erstellt ein digital signiertes JSON Web Token (JWT).

    :param data: Dictionary mit den Payload-Daten (z. B. 'sub' für Username & 'role').
    :param expires_delta: Optionales individuelles Ablaufdatum.
    :return: Der signierte JWT-String.
    """
    to_encode = data.copy()

    # Ablaufdatum berechnen (UTC Standard)
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Ablaufdatum ('exp') in Payload eintragen
    to_encode.update({"exp": expire, "type": "access"})

    # Token mit SECRET_KEY und HS256-Algorithmus signieren
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    data: dict, expire_delta: timedelta | None = None
) -> str:
    """Erstellt ein langlebiges Refresh Token (JWT) zur Erneuerung des Access Tokens.

    :param data: Dictionary mit den Payload-Daten (z. B. 'sub' für Username).
    :param expires_delta: Optionales individuelles Ablaufdatum.
    :return: Der signierte JWT-String.
    """
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# --- AUTORISIERUNG (AuthZ) DEPENDENCY ---


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    token: str = Depends(oauth2_scheme),
) -> User:
    """FastAPI-Dependency: Extrahiert das JWT aus dem Header, validiert die Signatur
    sowie das Ablaufdatum und lädt den zugehörigen Benutzer aus der Datenbank.

    :raises HTTPException: Status 401 bei ungültigem/abgelaufenem Token oder nicht gefundenem User.
    :raises HTTPException: Status 400 bei inaktivem Benutzerkonto.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Zugangsdaten konnten nicht validiert werden.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. JWT entschlüsseln und Signatur sowie 'exp'-Claim prüfen
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")

        if not username:
            raise credentials_exception

    except jwt.PyJWTError:
        # Fängt ungültige Tokens, falsche Schlüssel und abgelaufene Zeiten ab
        raise credentials_exception

    # 2. Benutzer aus der Datenbank abfragen
    statement = select(User).where(User.username == username)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        raise credentials_exception

    # 3. Account-Status verifizieren
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzerkonto ist deaktiviert.",
        )

    return user


# --- ROLE-BASED ACCESS CONTROL (RBAC) DEPENDENCY ---


class RoleChecker:
    """FastAPI-Dependency zur Überprüfung von Benutzerrollen (RBAC)."""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated[User, Depends(get_current_user)]) -> User:
        """Prüft, ob die Rolle des aktuellen Benutzers in der Liste der erlaubten Rollen enthalten ist.

        :raises HTTPException: Status 403 FORBIDDEN, wenn die Rolle nicht ausreicht.
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Zugriff verweigert: Unzureichende Berechtigungen.",
            )
        return current_user