from app.models.characters import Character
from app.models.spells import Spell

def validate_spell_learning(character: Character, spell: Spell) -> None:
    """
    Prüft die D&D Regeln für das Erlernen eines Zauberspruchs.
    Wirft eine ValueError-Exception, wenn eine Regel verletzt wird.
    """
    if spell in character.spells:
        raise ValueError("Character kennt diesen Zauberspruch bereits.")

    if spell.lvl > character.lvl:
        raise ValueError("Character-Level ist zu niedrig für diesen Zauberspruch.")

    return None