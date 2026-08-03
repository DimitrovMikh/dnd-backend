from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_session
from app.models.users import Token, User, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserCreate, session: AsyncSession = Depends(get_session)
):
    """Registriert einen neuen Benutzer im System.

    - Prüft auf Duplikate bei Username und E-Mail-Adresse.
    - Hasht das Passwort sicher mit Bcrypt.
    - Speichert den Benutzer in der Datenbank und gibt die Benutzerdaten ohne Passwort zurück.
    """
    # 1. Prüfen, ob Username oder Email bereits existieren
    statement = select(User).where(
        (User.username == user_in.username) | (User.email == user_in.email)
    )

    result = await session.exec(statement)
    existing_user = result.first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nutzername oder E-Mail-Adresse bereits vergeben.",
        )

    # 2. Passwort hashen
    hashed_pwd = hash_password(user_in.password)

    # 3. Datenbank-Objekt instanziieren
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        role=user_in.role,
        is_active=user_in.is_active,
        hashed_password=hashed_pwd,
    )

    # 4. In der Datenbank speichern (asynchron)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
async def login_user(
    user_in: UserLogin, session: AsyncSession = Depends(get_session)
):
    """Authentifiziert einen Benutzer und stellt ein JWT Access Token aus.

    - Validiert Benutzername und Passwort.
    - Verhindert Anmeldungen deaktivierter Konten.
    - Gibt einen Bearer Token mit 30 Minuten Gültigkeit zurück.
    """
    # 1. Benutzer in Datenbank suchen
    statement = select(User).where(User.username == user_in.username)
    result = await session.exec(statement)
    user = result.first()

    # 2. Existenz und Passwort überprüfen (Generische Fehlermeldung aus Sicherheitsgründen)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Anmeldedaten (Benutzername oder Passwort falsch).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Prüfen, ob das Benutzerkonto aktiv ist
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzerkonto ist deaktiviert.",
        )

    # 4. Access Token mit Username ('sub') und Rolle ('role') generieren
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Geschützter Endpunkt: Liefert das Profil des aktuell authentifizierten Benutzers zurück.
    Erfordert einen gültigen Bearer Token im 'Authorization'-Header.
    """
    return current_user