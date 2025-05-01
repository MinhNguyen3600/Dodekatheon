# unit_abilities.py

from math import hypot

class LoneOperative:
    """Once granted, this unit can only be shot at if attacker is within max_range."""
    def __init__(self, max_range=12):
        self.max_range = max_range

    def allows_targeting(self, attacker_pos, target_pos):
        # attacker can target only if within max_range
        return hypot(attacker_pos[0]-target_pos[0], attacker_pos[1]-target_pos[1]) <= self.max_range


class DarkAngelsBodyguard:
    """
    While this model is within `radius` inches of any friendly unit,
    it gains LoneOperative.
    """
    def __init__(self, radius=3):
        self.radius = radius

    def grants_lone(self, unit, friendly_units, board):
        # check any other friendly unit within self.radius
        for u in friendly_units:
            if u is not unit and u.is_alive():
                if board.distance_inches(unit.position, u.position) <= self.radius:
                    return True
        return False

class Leader:
    """Marks a Character that can attach to another unit."""
    pass

class MasterOfTheStances:
    def __init__(self, once_per):
        self.once_per = once_per

class StrategicMastery:
    def __init__(self, once_per):
        self.once_per = once_per

class ResoluteWill:
    """-1 to wound rolls when Character leads and S > T."""
    pass

class LivingFortress:
    def __init__(self, grants):
        self.grants = grants  # e.g. "feel_no_pain_4"

class DeepStrike:
    """Unit may start the game in reserve and deep strike later."""
    # you already handle setup in movement/command phase

class FightsFirst: ...
class MeleeSaveRetaliate: ...
class AllSecretsRevealed: ...
class MartialExemplar: ...
class NoHidingFromTheWatchers: ...
class DeadlyDemise:     # handles D6 explosion
    def __init__(self, dice): self.dice = dice
class FeelNoPain:
    def __init__(self, threshold): self.threshold = threshold
class BeguilingForm: ...
class DaemonicSpeed: ...
class EnthrallingHypnosis:
    def __init__(self, aura): self.aura = aura
class TeleportHomer: ...
class FuryOfTheFirst: ...
class AuraBenefit:      # generic for Mortarion auras
    def __init__(self, aura, benefit): self.aura, self.benefit = aura, benefit
class AuraRerollWound1:
    def __init__(self, aura): self.aura = aura
class AuraContagionBonus:
    def __init__(self, aura, bonus): self.aura, self.bonus = aura, bonus


__all__ = [
    "LoneOperative", "DarkAngelsBodyguard", "Leader", "MasterOfTheStances",
    "StrategicMastery", "ResoluteWill", "LivingFortress", "DeepStrike",
    "FightsFirst", "MeleeSaveRetaliate", "AllSecretsRevealed", "MartialExemplar",
    "NoHidingFromTheWatchers", "DeadlyDemise", "FeelNoPain", "BeguilingForm",
    "DaemonicSpeed", "EnthrallingHypnosis", "TeleportHomer", "FuryOfTheFirst",
    "AuraBenefit", "AuraRerollWound1", "AuraContagionBonus"
]