from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Zentrale Anwendungs- und Sicherheitskonfiguration.
    Liest Umgebungsvariablen typsicher aus der .env-Datei oder der Systemumgebung aus.
    """

    # --- Allgemeine Projekt-Metadaten ---
    PROJECT_NAME: str
    ENVIRONMENT: str

    # --- Sicherheits & JWT-Konfiguration ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Datenbank-Verbindung ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./dnd.db"

    # --- CORS / Security Konfiguration ---
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()   # type: ignore[call-arg]