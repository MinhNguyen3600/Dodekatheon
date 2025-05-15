# data/datasheet_loader.py
import os
import fnmatch
import json

from data.weapon_abilities import *
from data.unit_abilities import *

def build_weapon(entry, kind):
    *base, maybe_abils = entry
    if isinstance(maybe_abils, list):
        core, abil_keys = base, maybe_abils
    else:
        core, abil_keys = entry, []
    if kind == 'ranged':
        name, rng, A, Skill, S, AP, D = core
        rng_val = int(rng.rstrip('"')) if isinstance(rng,str) else int(rng)
        try:
            BS = int(str(Skill).rstrip('+'))
        except ValueError:
            BS = None  # For auto-hit weapons like Flamers

        return {
            'name': name,
            'range': rng_val,
            'A': A, 'BS': BS, 'S': S, 'AP': AP, 'D': D,
            'type': 'ranged',
            'abilities': WeaponAbility(abil_keys)
        }
    
    else:
        name, A, Skill, S, AP, D = core

        WS = None if str(Skill).upper() == "N/A" else int(str(Skill).rstrip('+'))
        
        return {
            'name': name,
            'range': None,
            'A': A, 'WS': WS, 'S': S, 'AP': AP, 'D': D,
            'type': 'melee',
            'abilities': WeaponAbility(abil_keys)
        }

def build_weapon_group(entry, kind):
    """
    Supports two formats:
      1) Legacy single-profile: entry is a list [ name, … , [abils] ]
      2) New grouping form: entry is { "name":…, "profiles":[ [ … ], … ] }
    """
    # legacy single-profile format?
    if isinstance(entry, list):
        w = build_weapon(entry, kind)
        return { 'name': w['name'], 'profiles': [ w ] }

    # new dict format
    wg = {'name': entry['name'], 'profiles': []}
    for prof in entry.get('profiles', []):
        wg['profiles'].append(build_weapon(prof, kind))
    return wg

def build_unit_ability(name, cfg):
    t = cfg['type']
    if t == 'choice':
        # build each sub‑ability
        choices = {k: build_unit_ability(k, sc) for k, sc in cfg['choices'].items()}
        return ChoiceAbility(name, cfg.get('phase'), choices, cfg.get('once_per'))

    if t == 'deep_strike':            return DeepStrike()
    if t == 'dark_angels_bodyguard':  return DarkAngelsBodyguard(radius=cfg.get('radius',3))
    if t == 'lone_operative':         return LoneOperative(max_range=cfg.get('max_range',12))
    if t == 'leader':                 return Leader()
    if t == 'master_of_the_stances':  return MasterOfTheStances(cfg.get('once_per'))
    if t == 'strategic_mastery':      return StrategicMastery(cfg.get('once_per'))
    if t == 'resolute_will':          return ResoluteWill()
    if t == 'living_fortress':        return LivingFortress(cfg.get('grants'))
    if t == 'fights_first':           return FightsFirst()
    if t == 'melee_save_retaliate':    return MeleeSaveRetaliate()
    if t == 'all_secrets_revealed':    return AllSecretsRevealed()
    if t == 'martial_exemplar':        return MartialExemplar()
    if t == 'no_hiding_from_watchers': return NoHidingFromTheWatchers()
    if t == 'deadly_demise':           return DeadlyDemise(cfg.get("dice"))
    if t == 'feel_no_pain':            return FeelNoPain(cfg.get("threshold"))
    if t == 'beguiling_form':          return BeguilingForm()
    if t == 'daemonic_speed':          return DaemonicSpeed()
    if t == 'enthralling_hypnosis':    return EnthrallingHypnosis(cfg.get("aura"))
    if t == 'teleport_homer':          return TeleportHomer()
    if t == 'fury_of_the_first':       return FuryOfTheFirst()
    if t == 'aura_benefit':            return AuraBenefit(cfg["aura"], cfg["benefit"])
    if t == 'aura_reroll_wound_1':     return AuraRerollWound1(cfg["aura"])
    if t == 'aura_contagion_bonus':    return AuraContagionBonus(cfg["aura"], cfg["bonus"])
    return None

class DatasheetLoader:
    """
    Recursively load every .json file under data/datasheets,
    merge them into self.data, and provide get_unit().
    """
    def __init__(self, base_path='data/datasheets'):
        self.data = {}
        for root, dirs, files in os.walk(base_path):
            for fname in fnmatch.filter(files, '*.json'):
                path = os.path.join(root, fname)
                with open(path, encoding='utf-8') as f:
                    frag = json.load(f)
                # detect duplicates if you wish:
                for k in frag:
                    if k in self.data:
                        raise ValueError(f"Duplicate unit '{k}' in {path}")
                self.data.update(frag)

    def get_unit(self, key):
        entry = self.data[key]
        M, T, Sv_raw, Invul_raw, W, Ld_raw, OC_raw = entry['statline']
        Sv = int(str(Sv_raw).rstrip('+'))
        Invul = None if Invul_raw == "-" else int(str(Invul_raw).rstrip('+'))
        Ld = int(str(Ld_raw).rstrip('+'))
        OC = int(str(OC_raw).rstrip('+'))

        pts_model  = entry.get('points_model', 0)
        pts_leader = entry.get('points_leader', 0)

        ranged = []
        for wg in entry.get('ranged_weapons', []):
            if isinstance(wg, list):
                ranged.append(build_weapon(wg, 'ranged'))
            else:
                for prof in wg.get('profiles', []):
                    ranged.append(build_weapon(prof, 'ranged'))

        melee = []
        for wg in entry.get('melee_weapons', []):
            if isinstance(wg, list):
                melee.append(build_weapon(wg, 'melee'))
            else:
                for prof in wg.get('profiles', []):
                    melee.append(build_weapon(prof, 'melee'))

        # merge sheet-level and unit_abilities
        all_abils = {}
        all_abils.update(entry.get('abilities', {}))
        all_abils.update(entry.get('unit_abilities', {}))
        unit_abils = [build_unit_ability(n, c) for n, c in all_abils.items() if build_unit_ability(n,c)]

        return {
            'size': entry.get('size', 1),
            'M': M, 'T': T, 'Sv': Sv, 'Invul': Invul, 'W': W,
            'Ld': Ld, 'OC': OC,
            'points_model': pts_model,
            'points_leader': pts_leader,
            'ranged_weapons': ranged,
            'melee_weapons': melee,
            'default_equipment': entry.get('default_equipment', []),
            'wargear_options': entry.get('wargear_options', {}),
            'unit_composition': entry.get('unit_composition', {}),
            'attachable_leaders': entry.get('attachable_leaders', []),
            'unit_abilities': unit_abils,
            'specialRules': entry.get('specialRules', {}),
            'keywords': entry.get('keywords', {}),
            'led_by': entry.get('led_by', [])
        }
