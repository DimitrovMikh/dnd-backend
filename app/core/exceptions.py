"""
Zentrales Fehlersystem für Domain Exceptions (Fachliche D&D-Regelverstöße).
Alle spezifischen Fehler erben von DNDGameException.
"""

class DNDGameException(Exception):
    """
    Basisklasse für alle fachlichen Fehler im D&D-Backend.
    Wird vom globalen FastAPI Exception Handler in main.py abgefangen.
    """
    def __init__(self, message: str, status_code: int = 400, error_code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

        super().__init__(message)

class SpellLevelTooLowError(DNDGameException):
    """Wird geworfen, wenn das Charakter-Level für einen Zauberspruch zu niedrig ist."""
    def __init__(self, character_lvl: int, spell_lvl: int):
        custom_message = f"Charakter-Level ({character_lvl}) ist zu niedrig für diesen Zauberspruch (Level {spell_lvl})."
        
        super().__init__(
            message=custom_message,
            status_code=400,
            error_code="SPELL_LEVEL_TOO_LOW"
        )

class SpellAlreadyKnownError(DNDGameException):
    """Wird geworfen, wenn ein Charakter einen Zauberspruch bereits gelernt hat."""
    def __init__(self, spell_name: str):        
        custom_message = f"Der Zauberspruch '{spell_name}' ist bereits bekannt."
        
        super().__init__(
            message=custom_message,
            status_code=400,
            error_code="SPELL_ALREADY_KNOWN"
        )