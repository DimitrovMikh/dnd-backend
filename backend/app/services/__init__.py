"""
Zentrale Export-Schnittstelle für den Service-Layer.
Ermöglicht saubere Imports über `from app.services import auth_service, ...`.
"""

from app.services import auth_service, character_service, item_service, spell_service

# Definiert die explizit nach außen freigegebenen Module des Service-Layers
__all__ = [
    "auth_service",
    "character_service",
    "item_service",
    "spell_service",
]
