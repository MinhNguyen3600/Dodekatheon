# Game/shooting_phase.py
import math as _math

from objects.dice import roll_d6
from data.unit_abilities import *
from data.weapon_abilities import *
from data.keywords import has_keyword

from ..utils import bdr_s, bdr_m, bdr_l
from ..objective import Objective

def shooting_phase(game):
    game.run_choice_abilities('shooting')

    for unit in [u for u in game.current_player().units if u.is_alive() and not u.fell_back]:
        all_weapons = unit.datasheet['ranged_weapons']

        # 0-0) Check if units that have charged if they have "Assault" weapon Keyword (to be eligible to shoot after advancing)
        if unit.advanced:
            weaps = [wp for wp in all_weapons if wp['abilities'].is_assault]
            if not weaps:
                print(f"{unit.name} advanced and has no Assault weapons. Cannot shoot.\n")
                continue
            else:
                print(f"{unit.name} advanced — only Assault weapons can be used.")
        else:
            weaps = all_weapons

        bdr_m()
        print(f"Shooting for {unit.name}:")
        bdr_m()

        # 2) build list of enemies in range of *any* of those weapons
        enemies = []
        for e in game.other_player().units:
            if not e.is_alive(): continue
            d = game.board.distance_inches(unit.position, e.position)
            if d <= max(wp['range'] for wp in weaps):
                enemies.append((e,d))
        if not enemies:
            print("  No targets in range.\n")
            continue

        # 3) lone‑operative filter (must compute is_lone first)
        legal = []
        for tgt_candidate, d in enemies:
            # compute is_lone
            abil = tgt_candidate.datasheet.get('unit_abilities', [])
            is_lone = any(isinstance(a, LoneOperative) for a in abil)
            for a in abil:
                if isinstance(a, DarkAngelsBodyguard) and a.grants_lone(
                        tgt_candidate,
                        game.current_player().units,
                        game.board
                    ):
                    is_lone = True
                    break
            # only keep if not (lone and out of 12")
            if not (is_lone and d > 12):
                legal.append((tgt_candidate, d))
        if not legal:
            print("  All targets illegal (Lone Operative).\n")
            continue

        # 4) ask player once: which target does *this unit* shoot at?

        # now we know tgt & dist, trim any dead‑model slots
        survivors = unit.current_models
        unit.models = unit.models[:survivors]

        for i,(e,d) in enumerate(legal):
            print(f"  {i}: {e.name} at {chr(ord('A')+e.position[0])}{e.position[1]+1} ({d:.1f}\")")
        choice = int(input("Pick target: "))
        tgt, dist = legal[choice]

        # — now handle each surviving model individually (all fire at the chosen tgt) —
        # 5) now that we have tgt & dist, loop each model and each weapon     
        for m_idx, slot in enumerate(unit.models):
            slot_weaps = unit.advanced and [wp for wp in slot['weapons']['ranged']
                                if wp['abilities'].is_assault] \
                or slot['weapons']['ranged']
            if not slot_weaps:
                print(f" Model {m_idx} has no valid ranged weapons to shoot.")
                continue

            print(f"\n Model {m_idx} weapons:")
            for i, wp in enumerate(slot_weaps):
                print(f"  {i}: {wp['name']}")
            pick = int(input(f"  Pick weapon for model {m_idx}: "))
            w = slot_weaps[pick]
            

            # now run your existing target‑selection & rolls for this single model/weapon
            # build context just for this weapon:
            ctx = {
                'distance':        dist,
                'weapon_range':    w['range'],
                'target_model_count': tgt.current_models,
                'in_engagement':   dist <= 1,
                'half_range':      dist <= w['range']/2,
                'unit_advanced':   unit.advanced,
                'is_monster':      False,
            }

            # determine attacks & damage profile
            num_attacks = w['abilities'].extra_attacks(w['A'], ctx)
            if w['abilities'].rapid_fire_bonus:
                num_attacks = WeaponAbility.rapid_fire(num_attacks, dist, w['range'])
            wD = w['abilities'].melta(w['D'], dist, w['range']) if w['abilities'].is_melta else w['D']

            # now hit→wound→save exactly as before, but scoped to this one model’s weapon
            failed_saves = 0
            total_damage = 0
            mw_total     = 0
            initial_models = tgt.current_models

            # 1) HIT ROLL
            hits = 0
            for _ in range(num_attacks):

                # TORRENT auto-hits
                if w['abilities'].applies_torrent():
                    hits += 1
                    continue

                # normal hit roll
                hit_die = roll_d6()[0]

                # 0.1) LETHAL HITS: unmodified 6 always wounds (mortal wound + normal hit)
                if w['abilities'].is_lethal_hits and hit_die == 6:
                    tgt.take_damage(1)  
                    mw_total += 1  
                    hits += 1
                    continue

                # HEAVY bonus
                hit_die += w['abilities'].heavy_hit_bonus({'unit_stationary': not unit.advanced and not unit.fell_back})

                # INDIRECT FIRE penalty
                # if w['abilities'].is_indirect:
                #     visible = game.board.has_line_of_sight(unit.position, tgt.position)
                # pen, ignore_cover = w['abilities'].indirect_fire_penalty(visible)  
                # hit_die += pen

                mod = w['abilities'].hit_modifier(ctx)
                skill = w.get('BS', w.get('WS'))
                if w['BS'] is None or hit_die == 6 or hit_die + mod >= skill:
                    hits += 1
                    hits += w['abilities'].on_crit_hit()

            # 2) WOUND ROLL
            wounds = 0
            for _ in range(hits):

                # Roll wounds die and check unit's weapon S stat vs targetted opponent unit's T stat
                wdie = roll_d6()[0]
                s, t = w['S'], tgt.datasheet['T']
                need = 2 if s >= 2*t else 3 if s > t else 4 if s == t else 5    
                
                # LANCE bonus on wound
                need += w['abilities'].lance_bonus({'unit_charged': unit.charged})

                # TWIN‐LINKED: if this wound roll failed (wdie < need), reroll once
                if w['abilities'].is_twin_linked and wdie < need:
                    wdie = w['abilities'].twin_linked_reroll(wdie)

                # 0) Trigger Anti‑X keyword
                if w['abilities'].triggers_anti_x(tgt.datasheet['keywords']['unit'], wdie):
                    wounds += 1
                    continue

                if wdie == 6 or wdie >= need:
                    wounds += 1

            # 3) SAVE ROLLS

            for _ in range(wounds):
                wound_die = roll_d6()[0]

                # 3.1) Devastating (mortal) wounds on a crit‑wound
                if w['abilities'].skip_saves_on_crit_wound() and wound_die == 6:
                    mw = w['abilities'].mortal_wounds_on_crit(wD)
                    tgt.take_damage(mw)
                    total_damage += mw
                    mw_total += mw
                    failed_saves += 1

                    # 5) HAZARDOUS tests (if any)
                    if w['abilities'].is_hazardous:
                        haz = w['abilities'].hazardous_tests(unit.current_models)
                        unit.take_damage(haz*3)  
                        mw_total += haz*3  
                        print(f"{unit.name} suffers {haz} mortal wounds from Hazardous tests.")

                    if not tgt.is_alive():
                        print(f"{tgt.name} is destroyed!")
                        game.board.clear_position(*tgt.position)
                        break
                    continue

                # 3.3) Otherwise roll save (armour vs invuln)
                save_roll = roll_d6()[0]
                armour_needed = tgt.datasheet['Sv'] - w['AP']
                
                # Cover bonus only if not IGNORES COVER 
                if has_keyword(tgt,'unit','Infantry') \
                and game.board.terrain_at(tgt.position).grants_cover() \
                and not w['abilities'].is_ignores_cover:
                    armour_needed -= 1


                invuln_needed = tgt.datasheet.get('Invul')

                if invuln_needed is not None and invuln_needed < armour_needed:
                    save_needed = invuln_needed
                    used_invuln = True
                else:
                    save_needed = armour_needed
                    used_invuln = False

                if used_invuln:
                    print(f"   Invuln Save Roll: {save_roll} vs {save_needed}+")
                else:
                    print(f"   Armour Save Roll: {save_roll} vs {save_needed}+")

                if save_roll < save_needed:
                    dmg = game.resolve_damage(wD)
                    tgt.take_damage(dmg)
                    total_damage += dmg
                    failed_saves += 1

                if not tgt.is_alive():
                    print(f"{tgt.name} is destroyed!")
                    game.board.clear_position(*tgt.position)
                    break

            # 4) summary & record stats
            bdr_s()
            print(f"Model {m_idx} — Hit/Wound/Saves: {hits}/{num_attacks}, failed {failed_saves}, dmg {total_damage}")
            bdr_s()
            unit._last_num_attacks = num_attacks
            unit._last_hits        = hits
            unit.register_damage_dealt(
                dmg              = total_damage,
                models_killed    = (initial_models - tgt.current_models),
                is_ranged        = True,
                is_melee         = False,
                mortal_wounds    = mw_total
            )

            # if target died, drop its slots and break out
            if not tgt.is_alive():
                print(f"{tgt.name} destroyed!")
                game.board.clear_position(*tgt.position)
                tgt.models = tgt.models[:tgt.current_models]
                break

        # end per‐model loop


