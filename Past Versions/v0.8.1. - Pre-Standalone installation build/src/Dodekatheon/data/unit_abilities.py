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
