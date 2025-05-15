# Game/fight_phase.py
import math as _math

from objects.dice import roll_d6
from data.keywords import has_keyword

from ..utils import bdr_s, bdr_m, bdr_l
from ..objective import Objective

def fight_phase(game):
    game.run_choice_abilities('fight')

    for attacker in [u for u in game.current_player().units if u.is_alive() and u.charged]:
        bdr_m()
        print(f"Fighting for {attacker.name}:")
        bdr_m()

        # pick melee weapon once for the unit
        all_weaps = attacker.datasheet['melee_weapons']
        if not all_weaps or input("Make melee attack? (y/n): ").lower() != 'y':
            continue

        bdr_l()

        # weapon choice
        # idx = 0
        # if len(all_weaps) > 1:
        #     for i, w in enumerate(all_weaps):
        #         print(f"{i}: {w['name']}")
        #     idx = int(input("Select melee weapon: "))
        # w = all_weaps[idx]
        
        bdr_l()

        enemies = []
        for e in game.other_player().units:
            if not e.is_alive(): continue
            d = game.board.distance_inches(attacker.position, e.position)
            if d <= 1.5:
                enemies.append((e, d))

        if not enemies:
            print("No enemies in melee range.\n")
            continue

        for i, (e, d) in enumerate(enemies):
            cx, cy = e.position
            print(f"{i}: {e.name} at {chr(ord('A') + cx)}{cy+1} ({d:.1f}\")")
        pick = int(input("Pick target: "))
        defender, dist = enemies[pick]
        bdr_l()

        # 2) Now each model in the unit fights with its own melee loadout
        # trim dead models first
        attacker.models = attacker.models[:attacker.current_models]
        for m_idx, slot in enumerate(attacker.models):
            slot_weaps = slot['weapons']['melee']
            if not slot_weaps:
                print(f" Model {m_idx} has no melee weapons.")
                continue

            print(f"\n Model {m_idx} weapons:")
            for j, w in enumerate(slot_weaps):
                print(f"  {j}: {w['name']}")
            pick = int(input(f"  Pick weapon for model {m_idx}: "))
            w = slot_weaps[pick]

            # build context & attack count
            context = {
                'half_range': False,
                'in_engagement': dist <= 1,
                'target_models': defender.current_models,
                'unit_advanced': attacker.advanced,
                'is_monster': False,
            }

            rawA = w['A']
            if isinstance(rawA, str) and rawA.startswith('D6'):
                parts = rawA.split('+')
                bonus = int(parts[1]) if len(parts) > 1 else 0
                num_attacks = roll_d6()[0] + bonus
            else:
                num_attacks = int(rawA)

            num_attacks = w['abilities'].extra_attacks(num_attacks, context)

            hits = 0
            for _ in range(num_attacks):
                die = roll_d6()[0]
                mod = w['abilities'].hit_modifier(context)
                ws = w.get('WS', attacker.datasheet['T'])
                if die == 6 or die + mod >= ws:
                    hits += 1
                    hits += w['abilities'].on_crit_hit()

            wounds = 0
            for _ in range(hits):
                wdie = roll_d6()[0]
                s, t = w['S'], defender.datasheet['T']
                need = 2 if s >= 2*t else 3 if s > t else 4 if s == t else 5
                if wdie == 6 or wdie >= need:
                    wounds += 1

            # before the save loop:
            failed_saves = 0
            total_damage = 0
            mw_total = 0
            initial_models = defender.current_models

            for _ in range(wounds):
                wound_die = roll_d6()[0]

                
                # 0) Anti‑X: if this weapon is anti‑something and defender has that keyword,
                #    an unmodified wound_die ≥ threshold is a critical wound (i.e. auto‑wound).
                if w['abilities'].triggers_anti_x(
                    defender.datasheet['keywords']['unit'],
                    wound_die):
                    # auto‑wound, count one wound and skip saves
                    defender.take_damage(1)
                    total_damage = 1
                    failed_saves = 1
                    # if the unit died, stop
                    if not defender.is_alive():
                        print(f"{defender.name} is destroyed!")
                        game.board.clear_position(*defender.position)
                        break
                    continue

                # 1) Devastating (mortal) wounds on a crit‑wound
                if w['abilities'].skip_saves_on_crit_wound() and wound_die == 6:
                    mw = w['abilities'].mortal_wounds_on_crit(w['D'])
                    defender.take_damage(mw)
                    total_damage += mw
                    mw_total += mw
                    failed_saves += 1
                    if not defender.is_alive():
                        print(f"{defender.name} is destroyed!")
                        game.board.clear_position(*defender.position)
                        break
                    continue

                # 2) Otherwise roll save (armour vs invuln)
                save_roll = roll_d6()[0]
                armour_needed = defender.datasheet['Sv'] - w['AP']


                # COVER/TERRAIN MECHANICS TO BE IMPLEMENTED, uncomment when it is
                # Cover bonus only to Infantry
                # if has_keyword(defender,'unit','Infantry') \
                # and game.board.terrain_at(defender.position).grants_cover():
                #     armour_needed -= 1

                # Parse Invul stat of unit from datasheet
                invuln_needed = defender.datasheet.get('Invul')

                # Check if Invulnerable save was used, if unit has the ability to use it
                # Roll Invuln save if lower than rolls needed for wound rolls, automatically use it (for higher chance of survival)
                if invuln_needed is not None and invuln_needed < armour_needed:
                    save_needed = invuln_needed
                    used_invuln = True
                    print(f"   Invuln Save Roll: {save_roll} vs {save_needed}+")
                else:
                    save_needed = armour_needed
                    used_invuln = False
                    print(f"   Armour Save Roll: {save_roll} vs {save_needed}+")

                # If opponent unit failed save roll, deal damage
                if save_roll < save_needed:
                    dmg = game.resolve_damage(w['D'])
                    defender.take_damage(dmg)
                    total_damage += dmg
                    failed_saves += 1

                # Unit is destroyed and removed from board
                if not defender.is_alive():
                    print(f"{defender.name} is destroyed!")
                    game.board.clear_position(*defender.position)
                    break

            # per‑model mini‑summary:
            print(f" Model {m_idx} — Attacks: {num_attacks}, Hits: {hits}, Wounds: {wounds}, Failed Saves: {failed_saves}, Damage: {total_damage}")

        # 3) summary
        bdr_s()
        print(f"Hit Rolls: {hits}/{num_attacks}")
        print(f"Wound Rolls: {wounds}/{hits}")
        print(f"Failed Saves: {failed_saves}/{wounds}")
        print(f"Total Damage: {total_damage}, Wounds now {defender.current_wounds}/{defender.max_wounds}")
        bdr_s()

        # 4) record stats properly
        attacker._last_num_attacks = num_attacks
        attacker._last_hits        = hits
        attacker.register_damage_dealt(
            dmg=total_damage,
            models_killed=(initial_models - defender.current_models),
            is_ranged=False,
            is_melee=True,
            mortal_wounds=mw_total
        )

    Objective.update_objective_control(game)
    return True
    