"""Business Logic / Service Layer für Authentifizierung und Benutzerverwaltung."""
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_hash_password, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate, UserLogin


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    """Sucht einen Benutzer anhand des Benutzernamens in der Datenbank."""
    statement = select(User).where(User.username == username)
    result = await session.exec(statement)
    return result.first()


async def get_user_by_username_or_email(
    session: AsyncSession, username: str, email: str
) -> Optional[User]:
    """Sucht nach einem existierenden Benutzer mit gleichem Benutzernamen oder gleicher E-Mail."""
    statement = select(User).where(
        (User.username == username) | (User.email == email)
    )
    result = await session.exec(statement)
    return result.first()


async def register_user(session: AsyncSession, user_in: UserCreate) -> User:
    """Registriert einen neuen Benutzer und speichert ihn in der Datenbank.

    Raises:
        HTTPException (400): Wenn Benutzername oder E-Mail bereits vergeben ist.
    """
    existing_user = await get_user_by_username_or_email(
        session, user_in.username, user_in.email
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nutzername oder E-Mail-Adresse bereits vergeben.",
        )

    hashed_pwd = get_hash_password(user_in.password)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        role=user_in.role,
        is_active=user_in.is_active,
        hashed_password=hashed_pwd,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def authenticate_user(session: AsyncSession, user_in: UserLogin) -> User:
    """Authentifiziert einen Benutzer mit Benutzername und Passwort.

    Raises:
        HTTPException (401): Bei ungültigen Anmeldedaten.
        HTTPException (400): Wenn das Benutzerkonto deaktiviert ist.
    """
    user = await get_user_by_username(session, user_in.username)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Anmeldedaten (Benutzername oder Passwort falsch).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzerkonto ist deaktiviert.",
        )

    return user


async def get_user_for_refresh(session: AsyncSession, username: str) -> User:
    """Lädt einen Benutzer für einen Token-Refresh und prüft den Account-Status.

    Raises:
        HTTPException (401): Wenn der Benutzer nicht existiert oder inaktiv ist.
    """
    user = await get_user_by_username(session, username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Benutzer nicht gefunden oder deaktiviert.",
        )
    return user
