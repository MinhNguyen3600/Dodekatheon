# weapon_abilities.py
from objects.dice import roll_d6

class WeaponAbility:
    """
    Encapsulates the list of ability-keywords attached to a weapon,
    and provides helper methods to query and apply them.
    """
    def __init__(self, names):
        # names: list of ability-keywords (strings)
        # store uppercase for case-insensitive matching
        self.names = set(n.upper() for n in (names or []))

        # boolean flags for simple abilities
        self.is_pistol = "PISTOL" in self.names
        self.is_assault = "ASSAULT" in self.names
        self.is_lethal_hits = "LETHAL HITS" in self.names
        self.is_blast = "BLAST" in self.names
        self.is_devastating = "DEVASTATING WOUNDS" in self.names

        # parse parametric abilities
        self.sustained_hits = 0
        for n in self.names:
            if n.startswith("SUSTAINED HITS"):
                # could be "SUSTAINED HITS 2" or "SUSTAINED HITS D3"
                parts = n.split()
                last = parts[-1]
                try:
                    self.sustained_hits = int(last)
                except ValueError:
                    # keep string if e.g. "D3"
                    self.sustained_hits = last

        self.rapid_fire_bonus = 0
        for n in self.names:
            if n.startswith("RAPID FIRE"):
                try:
                    self.rapid_fire_bonus = int(n.split()[-1])
                except ValueError:
                    pass

    def __iter__(self):
        # allow: for abil in w['abilities']
        return iter(self.names)

    def __contains__(self, key):
        return key.upper() in self.names

    def extra_attacks(self, base_attacks, context):
        # ensure we have an integer to start with
        try:
            a = int(base_attacks)
        except (TypeError, ValueError):
            # if it's something like "D6+3", roll it now:
            if isinstance(base_attacks, str) and base_attacks.startswith('D6'):
                parts = base_attacks.split('+')
                bonus = int(parts[1]) if len(parts)>1 else 0
                a = roll_d6()[0] + bonus
            else:
                a = 0

        # rapid fire
        if self.rapid_fire_bonus and context.get("half_range", False):
            a += self.rapid_fire_bonus

        # blast: +1 attack per 5 models in target
        if self.is_blast and "target_models" in context:
            a += (context["target_models"] // 5)

        return a

    def hit_modifier(self, context):
        """
        Flat modifier to hit roll.
        context: dict with 'in_engagement', 'unit_advanced', 'is_monster'
        """
        mod = 0
        # Big Guns Never Tire
        if context.get("in_engagement", False) and not self.is_pistol:
            mod -= 1
        return mod

    def on_crit_hit(self):
        """
        Extra hits granted by sustained hits on a critical hit.
        """
        return self.sustained_hits

    def skip_saves_on_crit_wound(self):
        """
        True if Devastating Wounds means no saves on a crit wound.
        """
        return self.is_devastating

    def mortal_wounds_on_crit(self, damage):
        """
        If devastating, returns how many mortal wounds on a crit wound.
        """
        return damage if self.is_devastating else 0
