# game/command_phase.py
import math
from objects.dice import roll_d6
from ..objective import Objective

def command_phase(game):
    # STEP 1: both players gain 1 CP
    for p in game.players:
        p.gain_cp(1)

    # STEP 2: Battle-shock tests for current player
    print(f"\n-- Battle-shock tests for {game.current_player().name} --")
    # clear any old battle_shocked flags on your units
    for u in game.current_player().units:
        u.battle_shocked = False

    # test each unit that is below half-strength
    for u in game.current_player().units:
        if not u.is_alive() or not u.below_half_strength:
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
    yours = sum(1 for o in game.objectives if o.controller == 'P'+str(game.current))
    
    # Uncomment if want max VP to be set to 3
    #vp = min(yours, 3)

    vp = min(yours)
    game.current_player().vp += vp
    print(f"Scored {vp} VP for objectives controlled.")


    print()
