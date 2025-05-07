# weapon_abilities.py
import random
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

        # boolean flags for simple abilities (core keywords)
        self.is_pistol = "PISTOL" in self.names
        self.is_assault = "ASSAULT" in self.names
        self.is_lethal_hits = "LETHAL HITS" in self.names
        self.is_blast = "BLAST" in self.names
        self.is_devastating = "DEVASTATING WOUNDS" in self.names

        
        self.is_ignores_cover = "IGNORES COVER" in self.names
        self.is_twin_linked   = "TWIN-LINKED"   in self.names
        self.is_torrent       = "TORRENT"       in self.names
        self.is_lance         = "LANCE"         in self.names
        self.is_indirect      = "INDIRECT FIRE" in self.names
        self.is_precision     = "PRECISION"     in self.names
        self.is_heavy         = "HEAVY"         in self.names
        self.is_hazardous     = "HAZARDOUS"     in self.names
        self.is_melta         = any(n.startswith("MELTA") for n in self.names)


        # parse parametric abilities
        self.sustained_hits = 0
        for n in self.names:
            if n.startswith("SUSTAINED HITS"):
                parts = n.split()
                last = parts[-1]
                try:
                    self.sustained_hits = int(last)
                except ValueError:
                    self.sustained_hits = last  # Keep as string like "D3"

        self.rapid_fire_bonus = 0
        for n in self.names:
            if n.startswith("RAPID FIRE"):
                try:
                    self.rapid_fire_bonus = int(n.split()[-1])
                except ValueError:
                    pass

        # parse Anti-X abilities into a dict, e.g. {"VEHICLE":4, "PSYKER":2}
        self.anti = {}
        for n in self.names:
            parts = n.split()
            if len(parts) == 2 and parts[0].startswith("ANTI-") and parts[1].endswith("+"):
                kw = parts[0][5:]  # text after "ANTI-"
                try:
                    th = int(parts[1].rstrip("+"))
                    self.anti[kw.upper()] = th
                except ValueError:
                    pass

    def __iter__(self):
        # allow: for abil in w['abilities']
        return iter(self.names)

    def __contains__(self, key):
        return key.upper() in self.names

    def extra_attacks(self, base_attacks, context):
        """
        Computes total attacks after accounting for Blast, Sustained Hits, etc.
        context must contain: 'target_model_count', 'distance', 'weapon_range'
        """
        try:
            a = int(base_attacks)
        except (TypeError, ValueError):
            if isinstance(base_attacks, str) and base_attacks.startswith('D6'):
                parts = base_attacks.split('+')
                bonus = int(parts[1]) if len(parts) > 1 else 0
                a = roll_d6()[0] + bonus
            else:
                a = 0

        # Apply Blast
        if self.is_blast:
            count = context.get("target_model_count", 0)
            if count >= 11:
                a += random.randint(1, 6)
            elif count >= 6:
                a += random.randint(1, 3)

        # Apply Rapid Fire
        if self.rapid_fire_bonus:
            dist = context.get("distance", 999)
            rng = context.get("weapon_range", 0)
            if dist <= rng / 2:
                a += self.rapid_fire_bonus

        return a

    
    # TORRENT → automatic hits
    def applies_torrent(self):
        """True means every attack automatically hits (no hit roll)."""
        return self.is_torrent

    # TWIN-LINKED → reroll one failed wound roll
    def twin_linked_reroll(self, wound_roll):
        """
        If this is twin-linked and wound_roll failed (not a crit 6),
        roll once more and take the new result.
        """
        if self.is_twin_linked and wound_roll != 6:
            return roll_d6()[0]
        return wound_roll

    # LANCE → 1 to wound when charging
    def lance_bonus(self, context):
        """
        context should include 'unit_charged': bool
        Returns 1 if applies, else 0.
        """
        return 1 if self.is_lance and context.get('unit_charged',False) else 0

    # IGNORE COVER → skip cover bonus
    def ignores_cover_bonus(self):
        """True means do not grant the target any cover bonus."""
        return self.is_ignores_cover

    # INDIRECT FIRE → hit penalty and cover still applies
    def indirect_fire_penalty(self, target_visible):
        """
        Returns (hit_penalty, cover_ignored_flag) per core rule.
        """
        if self.is_indirect and not target_visible:
            return -1, False   # -1 to hit, but cover still applies unless torrent
        return 0, False

    # PRECISION → can re-allocate wounds onto CHARACTERS
    def allows_precision(self):
        """True means you may re-allocate a wound to a visible CHARACTER."""
        return self.is_precision

    # HEAVY → 1 to hit if stationary
    def heavy_hit_bonus(self, context):
        """
        context should include 'unit_stationary': bool
        Returns 1 if applies, else 0.
        """
        return 1 if self.is_heavy and context.get('unit_stationary',False) else 0

    # HAZARDOUS → roll after firing
    def hazardous_tests(self, models_fired):
        """
        For each model_fired, roll D6. On a 1, that model suffers 3 mortal wounds.
        Returns total mortal wounds inflicted on firing unit.
        """
        mw = 0
        if self.is_hazardous:
            for _ in range(models_fired):
                if random.randint(1,6)==1:
                    mw += 3
        return mw

    @staticmethod
    def rapid_fire(base_attacks, distance, weapon_range):
        """
        If the firing model is within half the weapon's range,
        it makes double the number of attacks.
        Returns total attacks after applying rapid fire.
        """
        if distance <= weapon_range / 2:
            return base_attacks * 2
        return base_attacks

    @staticmethod
    def melta(base_damage, distance, weapon_range):
        """
        If the target is within half range, add +2 to the weapon's damage.
        Returns the final damage value.
        """
        if distance <= weapon_range / 2:
            return base_damage + 2
        return base_damage

    @staticmethod
    def hazardous(models_firing):
        """
        For each model firing a hazardous weapon, roll a D6.
        On a 1, that model is destroyed.
        Returns the number of self-inflicted model losses.
        """
        losses = 0
        for _ in range(models_firing):
            if random.randint(1, 6) == 1:
                losses += 1
        return losses

    @staticmethod
    def indirect_fire(target_visible):
        """
        If the target is not visible:
        - Attacks suffer a -1 to hit
        - Target does NOT benefit from cover
        Returns a tuple:
        - hit_penalty: int (typically -1 or 0)
        - ignore_cover: bool
        """
        if not target_visible:
            return -1, True
        return 0, False

    @staticmethod
    def blast(target_model_count):
        """
        Blast weapons get extra attacks based on the size of the target unit:
        - +D3 attacks if 6–10 models
        - +D6 attacks if 11+ models
        Returns an integer number of bonus attacks.
        """
        if target_model_count >= 11:
            return random.randint(1, 6)
        elif target_model_count >= 6:
            return random.randint(1, 3)
        else:
            return 0

    def hit_modifier(self, context):
        """
        Flat modifier to hit roll.
        context: dict with 'in_engagement', 'unit_advanced', 'is_monster'
        """
        mod = 0
        # Big Guns Never Tire rule
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

    def triggers_anti_x(self, target_keywords, wound_roll):
        """
        Returns True if any Anti-X entry applies:
        i.e. the target has keyword X and the unmodified wound_roll ≥ threshold.
        """
        for kw, th in self.anti.items():
            if any(kw.upper() == tk.upper() for tk in target_keywords):
                if wound_roll >= th:
                    return True
        return False

    @staticmethod
    def scores_crit_wound(wound_roll):
        """
        Core rule: A wound roll of 6 is a critical wound.
        """
        return wound_roll == 6
