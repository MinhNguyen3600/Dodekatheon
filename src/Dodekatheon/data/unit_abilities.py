# unit_abilities.py

from math import hypot

class ChoiceAbility:
    """
    Wraps a named group of sub‑abilities from which the player must pick one
    at the start of the specified phase.
    """
    def __init__(self, name, phase, choices: dict, once_per=None):
        self.name       = name
        self.phase      = phase            # e.g. "command", "charge", "round_start"
        self.once_per   = once_per
        self.choices    = choices          # dict: key→Ability instance
        self.selected   = None

    def prompt(self, game, unit):
        # only once per phase if once_per set
        if self.selected is not None and self.once_per:
            return
        print(f"\n- {unit.name}: choose one option for {self.name}:")
        opts = list(self.choices.keys())
        for i,o in enumerate(opts):
            print(f"  {i}: {o.replace('_',' ').title()}")
        pick = None
        while pick is None:
            inp = input(f"Select 0-{len(opts)-1}: ")
            if inp.isdigit() and 0 <= int(inp) < len(opts):
                pick = opts[int(inp)]
        self.selected = self.choices[pick]
        print(f"=> {unit.name} gains {pick.replace('_',' ').title()} for this {self.phase}.\n")

    def apply(self, game, unit):
        # delegate to the selected sub‑ability if it has any hooks
        if self.selected and hasattr(self.selected, self.phase):
            getattr(self.selected, self.phase)(game, unit)


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

class Necrodermis:
    """
    Each time an attack is allocated to this model,
    halve the Damage characteristic of that attack.
    """
    def modify_incoming_damage(self, damage):
        # round down half
        return damage // 2

    # hook for your combat resolver:
    def apply(self, defender, damage):
        return self.modify_incoming_damage(damage)

class MasterfulTactician:
    """At the start of your Command phase, if this model is on the battlefield, you gain 1 CP."""
    def at_start_of_command(self, game, model):
        if model in game.current_player().units and model.is_alive():
            game.current_player().gain_cp(1)

class LionHelm:
    """
    Wargear ability:
     • Models in bearer's unit have 4+ invulnerable save.
     • Once per battle, may summon watcher → grant FNP.
    """
    def __init__(self):
        self.used = False

    def apply_invul(self, unit):
        # override each model's invul to min(current,4)
        for m in unit.models:
            if m.datasheet['Invul'] is None or m.datasheet['Invul']>4:
                m.datasheet['Invul'] = 4

    def summon_watcher(self, game, unit):
        if not self.used:
            self.used = True
            # implement your “summon watcher” effect here…
            # then grant FNP to unit.models


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
    "ChoiceAbility","LoneOperative", "DarkAngelsBodyguard", "Leader", "MasterOfTheStances",
    "StrategicMastery", "ResoluteWill", "LivingFortress", "DeepStrike",
    "FightsFirst", "MeleeSaveRetaliate", "AllSecretsRevealed", "MartialExemplar",
    "NoHidingFromTheWatchers", "DeadlyDemise", "FeelNoPain", "BeguilingForm",
    "DaemonicSpeed", "EnthrallingHypnosis", "TeleportHomer", "FuryOfTheFirst",
    "AuraBenefit", "AuraRerollWound1", "AuraContagionBonus", "Necrodermis", "MasterfulTactician", "LionHelm"
]