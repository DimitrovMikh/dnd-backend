from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_hash_password,
    verify_password,
)
from app.core.limiter import limiter
from app.database import get_session
from app.models.users import Token, User, UserCreate, UserLogin, UserResponse
from app.core.config import settings

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
    - Hasht das Passwort sicher mit Argon2id.
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
    hashed_pwd = get_hash_password(user_in.password)

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
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    response: Response,
    user_in: UserLogin,
    session: AsyncSession = Depends(get_session)
):
    """Authentifiziert einen Benutzer und stellt Token aus.

    - Validiert Benutzername und Passwort via Argon2.
    - Verhindert Anmeldungen deaktivierter Konten.
    - Gibt ein Access Token (15 Min.) zurück und setzt ein HttpOnly Refresh Cookie (7 Tage).
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
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {"access_token": access_token, "token_type": "bearer"}


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


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str | None = Cookie(None, alias="refresh_token"),
    session: AsyncSession = Depends(get_session)
):
    """Liest das HttpOnly Refresh-Cookie aus, entwertet/prüft es
    und stellt ein frisches Access Token aus.
    """
    # 1. Cookie-Prüfung: Ist das Token vorhanden?
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token fehlt."
        )

    # 2. JWT-Decoding & Fehlerabfang (Signatur & Ablaufdatum)
    try:
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiges oder abgelaufenens Refresh Token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Payload auslesen & Token-Typ validieren
    username: str | None = payload.get("sub")
    token_type: str | None = payload.get("type")

    if token_type != "refresh" or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Token-Typ.",
        )

    # 4. Nutzer aus der Datenbank laden & Account-Status prüfen
    statement = select(User).where(User.username == username)
    result = await session.exec(statement)
    user = result.first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Benutzer nicht gefunden oder deaktiviert.",
        )

    # 5. Frisches Access Token generieren & zurückgeben
    new_access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": new_access_token, "token_type": "bearer"}