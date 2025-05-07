# unit.py
from objects.dice import roll_d6, roll_d3
import math


class Unit:
    _id_counter = 1

    def __init__(self, name, symbol, x, y, datasheet):
        
        # set unit ID and increase it incrementally
        self.id = Unit._id_counter
        Unit._id_counter += 1

        # Set datasheet variable (to parse from datasheet.json)
        self.datasheet = datasheet  
        self.name = name

        self.symbol = symbol   # Check what symbol does, currently not defined in unit.py at least

        # Unit position (for unit deployement phase)
        self.position = (x, y)

        # squad size (1 for characters, >1 for multi-model units)
        # build model‑slots according to composition: each model gets actual profile dicts
        self.size = datasheet.get('size', 1)

        # wounds per individual model
        self.wounds_per_model = datasheet['W']

        # total pooled wounds for the squad
        self.max_wounds = self.size * self.wounds_per_model
        self.current_wounds = self.max_wounds

        # Phases set to false (before game starts)
        self.advanced = False
        self.fell_back = False
        self.charged = False
        self.battle_shocked = False

        # Get attachments holds other Unit instances (Characters)
        self.attachments = []

        # Set get wargear options 
        self.wargear_options   = datasheet.get('wargear_options', {})
        self.unit_composition  = datasheet.get('unit_composition', {})
        self.led_by            = datasheet.get('led_by', [])

        # Set unit stats for final scoreboard and statistic calculation, post-match
        self.stats = {
            'rng_fired':       0,
            'rng_hits':        0,
            'mle_attacks':   0,
            'mle_hits':      0,
            'mortal_wounds':   0,
            'damage_dealt':    0,
            'models_killed':   0,
            'cp_spent':        0
        }

        # copy them onto the unit for easier access:
        self.unit_abilities = list(datasheet.get('unit_abilities', []))

        # build initial models[] from “default_equipment” if present,
        # otherwise fall back to full datasheet pools
        # build initial models[] from “default_equipment” if present,
        # otherwise fall back to full datasheet pools
        default_equipment = datasheet.get('default_equipment')

        self.models = []
        for _ in range(self.size):
            slot = {
                'weapons': {'ranged':[], 'melee':[]},
                'abilities': list(self.datasheet.get('unit_abilities',[])),
                'wargear': []
            }
            if default_equipment:

                #native import
                from data.datasheet_loader import build_weapon 

                # only equip exactly those names
                for wname in default_equipment:
                    for pool_name, side in (('ranged_weapons','ranged'), ('melee_weapons','melee')):

                        for wg in self.datasheet.get(pool_name, []):
                            # if this is a built‑weapon dict (has a 'name' key and no 'profiles' list), just copy it
                            if isinstance(wg, dict) and wg.get('name') == wname and 'profiles' not in wg:
                                slot['weapons'][side].append(wg.copy())

                            # if it’s a JSON grouping dict, find the matching profile(s)
                            elif isinstance(wg, dict) and wg.get('name') == wname and 'profiles' in wg:
                                for prof in wg['profiles']:
                                    slot['weapons'][side].append(build_weapon(prof, side))
                                    
                            # if it’s the legacy list form
                            elif isinstance(wg, list) and wg[0] == wname:
                                slot['weapons'][side].append(build_weapon(wg, side))

            else:
                # full loadout: copy the built profiles
                slot['weapons']['ranged'] = [w.copy() for w in datasheet['ranged_weapons']]
                slot['weapons']['melee']  = [w.copy() for w in datasheet['melee_weapons']]

            self.models.append(slot)

    # Function for recording unit shooting and fighting stats per round for Scoreboard
    def register_damage_dealt(self, *, dmg, models_killed, is_ranged, is_melee, mortal_wounds=0):

        # update damage and kills
        self.stats['damage_dealt']  += dmg + mortal_wounds
        self.stats['models_killed'] += models_killed

        if is_ranged:
            self.stats['rng_fired'] += getattr(self, '_last_num_attacks', 0)
            self.stats['rng_hits']    += getattr(self, '_last_hits', 0)

        if is_melee:
            self.stats['mle_attacks'] += getattr(self, '_last_num_attacks', 0)
            self.stats['mle_hits']    += getattr(self, '_last_hits', 0)

        # clear last for next round
        self._last_num_attacks = self._last_hits = None

    # Search for attachable unit leaders (typically in units with size > 1)
    def attach_leader(self, leader_unit):

        if leader_unit.name in self.datasheet['attachable_leaders']:
            self.attachments.append(leader_unit)    # fetch leader unit from and add it to the 'attachements' list/dict

            # increase size & wounds to account for attaching leader unit to the current unit
            self.size += leader_unit.size
            self.max_wounds += leader_unit.max_wounds
            self.current_wounds += leader_unit.current_wounds

    # If unit's wound is not 0 -> unit is still alice
    def is_alive(self):
        return self.current_wounds > 0
    
    # define what "below hald strength" means for Leadership/Battleshock tests
    @property
    def below_half_strength(self):
        import math
        # characters (size=1): wounds < half their W characteristic
        if self.size == 1:
            # e.g. W=3 → half=1.5 → ceil(1.5)=2 → below if current_wounds<2
            return self.current_wounds < math.ceil(self.wounds_per_model / 2)

        # multi-model: models remaining < half starting models
        return self.current_models < math.ceil(self.size/2)

    def take_damage(self, d=1):
        # subtract from pooled wounds
        self.current_wounds = max(0, self.current_wounds - d)

    # Define what 'current models' actually are
    @property
    def current_models(self):
        # how many individual models remain (round up)
        return math.ceil(self.current_wounds / self.wounds_per_model)

    # Unit display stats for current player units
    def display_stats(self):
        ds = self.datasheet
        print(
            f"{self.name} (ID {self.id}) - Pos:{self.position} "
            f"Wounds:{self.current_wounds}/{self.max_wounds} "
            f"Models:{self.current_models}/{self.size} "
            f"M:{ds['M']} T:{ds['T']} Sv:{ds['Sv']} W:{ds['W']}"
        )



    # helper: pick out from a full pool only those whose profile‐name appears in defaults
    def pick_defaults(self, pool, default_names):
        picked = []
        for wg in pool:
            # wg may be either a dict profile (with 'name') or a built dict from build_weapon
            name = wg['name']
            if name in default_names:
                picked.append(wg.copy())
        return picked

    # Main wargear customization function
    def choose_wargear(self):
        """
        Prompt the user to apply wargear_options and unit_composition
        to self.models[] before the game starts.
        """
        # --- 1) UNIT COMPOSITION ---
        comp = self.unit_composition or {}
        size_opts = comp.get('size_options', [])    # Get unit size for unit composition customization

        # If it has size options 
        # Note: size_options = 1 means that unit's composition is unchangable and must stay default
        if len(size_opts) > 1:

            # Pick unit size options
            print(f"\nChoose size for {self.name}:")
            for i,opt in enumerate(size_opts):
                cnt = opt.get('count', self.size)
                mand = opt.get('mandatory',[])                  # Pass checks if unit size option has required unit to be attached
                print(f"  {i}: {cnt} models, mandatory: {mand}") # If size option has a mandatory, show player, otherwise empty

            # Player input with error handling
            while True:
                try:
                    # Player input 
                    choice = int(input("Size option #: "))

                    if 0 <= choice < len(size_opts):
                        sel = size_opts[choice]                 # sel = selection
                        new_size = sel.get('count', self.size)
                        break                                   # valid choice, exit loop
                    else:
                        print(f"Invalid choice. Please enter a number between 0 and {len(size_opts) - 1}.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    
            # DEFINITION OF UPDATED UNIT STATS
            # update the unit’s size and its pooled wounds
            self.size = new_size
            self.max_wounds = self.size * self.wounds_per_model
            
            # clamp current_wounds so it never exceeds max_wounds
            self.current_wounds = min(self.current_wounds, self.max_wounds)

            # REBUILD UNIT POST-UNIT COMP CUSTOMIZATION
            # now rebuild the per‑model slots array to match new_size
            old_models = self.models
            self.models = []
            for idx in range(self.size):
                if idx < len(old):
                    self.models.append(old_models[idx])
                else:
                    # fresh slot – use the same default_equipment logic
                    slot = {
                        'weapons': {
                            'ranged': self.pick_defaults(self.datasheet['ranged_weapons'],
                                                        self.datasheet.get('default_equipment', [])),

                            'melee':  self.pick_defaults(self.datasheet['melee_weapons'],
                                                        self.datasheet.get('default_equipment', []))
                        },
                        'abilities': list(self.datasheet.get('unit_abilities',[])),
                        'wargear': []
                    }
                    self.models.append(slot)

       # --- 2) WARGEAR OPTIONS ---
        for tag in list(self.wargear_options.keys()):
            opt = self.wargear_options[tag]
            # compute how many may take this option
            if opt.get('max_models') is not None:
                allowed = opt['max_models']
            else:
                per = opt.get('per_models')
                allowed = (self.current_models // per) if per else 0
            if allowed <= 0:
                self.wargear_options.pop(tag)
                continue

            print(f"\nOption “{tag}”: you may apply to up to {allowed} models.")
            count = int(input(f"How many models to equip with {tag}? (0–{allowed}): "))
            count = max(0, min(count, allowed))

            for n in range(count):
                # list each model’s current weapons
                print(f"Select model to apply {tag}, instance {n+1}:")
                for idx, m in enumerate(self.models):
                    rng_names   = [wp['name'] for wp in m['weapons']['ranged']]
                    melee_names = [wp['name'] for wp in m['weapons']['melee']]
                    print(f"  {idx}: Ranged={rng_names}, Melee={melee_names}")

                # pick a valid model index
                while True:
                    try:
                        model_idx = int(input(f"Pick model index (0–{len(self.models)-1}) for {tag}: "))
                        if 0 <= model_idx < len(self.models):
                            break
                    except ValueError:
                        pass
                    print("Invalid index; try again.")

                m = self.models[model_idx]

                # 1) remove any replaced weapons by name
                for r in opt.get('replaces',[]):
                    m['weapons']['ranged'] = [wp for wp in m['weapons']['ranged'] if wp['name'] != r]
                    m['weapons']['melee']  = [wp for wp in m['weapons']['melee']  if wp['name'] != r]

                # 2) add new weapons by matching the built datasheet list
                for aname in opt.get('adds', []):
                    # look in the datasheet’s built lists
                    for side in ('ranged','melee'):
                        for candidate in self.datasheet[f'{side}_weapons']:
                            if candidate['name'] == aname:
                                # append a fresh copy
                                m['weapons'][side].append(candidate.copy())

                # 3) add any abilities
                for abil in opt.get('adds_abilities', []):
                    m['abilities'].append(abil)

                # 4) tag the model
                m['wargear'].append(tag)

                # debug print after each swap
                print("\n=== DEBUG: Updated Loadouts ===")
                for j, mm in enumerate(self.models):
                    rn = [wp['name'] for wp in mm['weapons']['ranged']]
                    mn = [wp['name'] for wp in mm['weapons']['melee']]
                    wg = mm['wargear']
                    print(f"  Model {j}: Ranged={rn}, Melee={mn}, Wargear Tags={wg}")
                print("================================\n")