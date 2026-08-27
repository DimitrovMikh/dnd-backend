"""Zentrales Fehlersystem für Domain Exceptions (Fachliche D&D-Regelverstöße).
Alle spezifischen Fehler erben von DNDGameException.
"""

from fastapi import status


class DNDGameException(Exception):
    """Basisklasse für alle fachlichen Fehler im D&D-Backend.
    Wird vom globalen FastAPI Exception Handler in main.py abgefangen.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "BAD_REQUEST",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class SpellLevelTooLowError(DNDGameException):
    """Wird geworfen, wenn das Charakter-Level für einen Zauberspruch zu niedrig ist."""

    def __init__(self, character_lvl: int, spell_lvl: int):
        custom_message = (
            f"Charakter-Level ({character_lvl}) ist zu niedrig für diesen "
            f"Zauberspruch (Level {spell_lvl})."
        )
        super().__init__(message=custom_message, error_code="SPELL_LEVEL_TOO_LOW")


class SpellAlreadyKnownError(DNDGameException):
    """Wird geworfen, wenn ein Charakter einen Zauberspruch bereits gelernt hat."""

    def __init__(self, spell_name: str):
        custom_message = f"Der Zauberspruch '{spell_name}' ist bereits bekannt."
        super().__init__(message=custom_message, error_code="SPELL_ALREADY_KNOWN")
