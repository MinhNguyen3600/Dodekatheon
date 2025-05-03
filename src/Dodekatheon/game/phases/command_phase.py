# game/command_phase.py
import math

from objects.dice import roll_d6
from ..objective import Objective

from data.keywords import has_keyword
from data.unit_abilities import ChoiceAbility


# Deployment Zone border display - REUSE AND UNCOMMENT FOR WHEN IMPLEMENTING RESERVE UNITS & DEPLOYMENT: 
# game.board.display(flip=True, highlight=zone_line)


def command_phase(game):
    # STEP 0: first, let each unit pick any command‑phase choices
    game.run_choice_abilities('command')

    # STEP 1: both players gain 1 CP
    for p in game.players:
        p.gain_cp(1)

    # STEP 1.5: units with "Masterful Tactician" ability gains an additional CP
    for u in game.current_player().units:
        for a in u.unit_abilities:
            if isinstance(a, ChoiceAbility) and 'command' in a.phase:
                a.apply(game, u)
            if isinstance(a, MasterfulTactician):
                a.at_start_of_command(game, u)

    # STEP 2: Battle-shock tests for current player
    print(f"\n-- Battle-shock tests for {game.current_player().name} --")
    # clear any old battle_shocked flags on your units
    for u in game.current_player().units:
        u.battle_shocked = False

    # test each unit that is below half-strength
    for u in game.current_player().units:

        # Characters ignore battle‑shock tests
        if not u.is_alive() or not u.below_half_strength \
           or has_keyword(u, 'unit', 'Character'):
            continue

        # roll 2D6
        dice = roll_d6(2)
        total = sum(dice)

        leadership = u.datasheet['Ld']
        print(f"  {u.name} below half-strength -> roll {dice} = {total} vs Ld {leadership}", end=' ')
        if total < leadership:
            u.battle_shocked = True
            is_battle_shocked = True
            print(f"-> FAILED => {u.name} is Battle-shocked!")
        else:
            print("-> Passed.")

    # Check and update OC
    Objective.update_objective_control(game)

    # player indices are 0/1 but controllers are labeled "P1"/"P2"
    yours = sum(1 for o in game.objectives if o.controller == 'P'+str(game.current+1))
    
    # Uncomment if want max VP to be set to 3
    vp = min(yours, 100)
    game.current_player().vp += vp
    print(f"Scored {vp} VP for objectives controlled.")


    print()
