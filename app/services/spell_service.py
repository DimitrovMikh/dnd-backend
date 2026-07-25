"""Business Logic / Service Layer für Zaubersprüche.
Enthält reine Python-Regelprüfungen ohne direkte Abhängigkeiten zu HTTP oder FastAPI.
"""
from app.core.exceptions import SpellAlreadyKnownError, SpellLevelTooLowError
from app.models.characters import Character
from app.models.spells import Spell


def validate_spell_learning(character: Character, spell: Spell) -> None:
    """Prüft die D&D-Regeln für das Erlernen eines Zauberspruchs.

    Raises:
        SpellAlreadyKnownError: Wenn der Zauberspruch bereits gelernt wurde.
        SpellLevelTooLowError: Wenn das Zauber-Level höher als das Charakter-Level ist.
    """

    if any(s.id == spell.id for s in character.spells):
        raise SpellAlreadyKnownError(spell_name=spell.name)

    if spell.lvl > character.lvl:
        raise SpellLevelTooLowError(character_lvl=character.lvl, spell_lvl=spell.lvl)

    return None