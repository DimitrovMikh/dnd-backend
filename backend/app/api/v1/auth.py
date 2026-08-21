from typing import Annotated

import jwt
from app.core.config import settings
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from app.database import get_session
from app.db.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services import auth_service
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_in: UserCreate, session: Annotated[AsyncSession, Depends(get_session)]
):
    """Registriert einen neuen Benutzer im System."""
    return await auth_service.register_user(session, user_in)


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
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Authentifiziert einen Benutzer und stellt Token aus.

    - Validiert Benutzername und Passwort via Argon2 über auth_service.
    - Verhindert Anmeldungen deaktivierter Konten.
    - Gibt ein Access Token (15 Min.) zurück und setzt ein HttpOnly Refresh Cookie (7 Tage).
    """
    user = await auth_service.authenticate_user(session, user_in)

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Geschützter Endpunkt: Liefert das Profil des aktuell authentifizierten Benutzers zurück."""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    session: Annotated[AsyncSession, Depends(get_session)],
    refresh_token: str | None = Cookie(None, alias="refresh_token"),
):
    """Liest das HttpOnly Refresh-Cookie aus, entwertet/prüft es
    und stellt ein frisches Access Token aus.
    """
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token fehlt.",
        )

    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiges oder abgelaufenens Refresh Token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str | None = payload.get("sub")
    token_type: str | None = payload.get("type")

    if token_type != "refresh" or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Token-Typ.",
        )

    user = await auth_service.get_user_for_refresh(session, username)

    new_access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": new_access_token, "token_type": "bearer"}