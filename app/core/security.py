from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.users import User, UserRole

# --- Konfiguration für JWT-Token-Signierung ---
# WICHTIG: In einer Produktionsumgebung sollte der SECRET_KEY aus einer .env-Datei geladen werden.
SECRET_KEY = "SUPER_SECRET_DND_KEY_CHANGE_ME_IN_PRODUCTION_12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2-Schema: Liest den 'Authorization: Bearer <token>' Header aus und aktiviert den Login-Button in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Passlib-Kontext: Nutzt Bcrypt für das sichere Hashing von Passwörtern
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- PASSWORT HASHING & VERIFIKATION ---


def hash_password(password: str) -> str:
    """Wandelt ein Klartext-Passwort mithilfe von Bcrypt in einen sicheren Hash um."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Prüft, ob ein eingegebenes Klartext-Passwort zum gespeicherten Hash passt."""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT TOKEN GENERIERUNG ---


def create_access_token(
    data: dict, expire_delta: Optional[timedelta] = None
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
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Ablaufdatum ('exp') in Payload eintragen
    to_encode.update({"exp": expire})

    # Token mit SECRET_KEY und HS256-Algorithmus signieren
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- AUTORISIERUNG (AuthZ) DEPENDENCY ---


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
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

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """Prüft, ob die Rolle des aktuellen Benutzers in der Liste der erlaubten Rollen enthalten ist.

        :raises HTTPException: Status 403 FORBIDDEN, wenn die Rolle nicht ausreicht.
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Zugriff verweigert: Unzureichende Berechtigungen.",
            )
        return current_user