# Game/game.py
import json
from game.utils import *   # or define load_json inline
from .objective import Objective
from objects.dice import roll_d6
from objects.board import Board

from .phases.command_phase  import command_phase
from .phases.movement_phase import movement_phase
from .phases.shooting_phase import shooting_phase
from .phases.charge_phase   import charge_phase
from .phases.fight_phase    import fight_phase

from game.objective import Objective

class Game:
    def __init__(game, p1, p2, board_width=30, board_height=15, mission="Only War"):
        game.board = Board(board_width, board_height)

        game.players = [p1, p2]
        game.current = 0
        game.round = 1
        # place all units initially
        # game._refresh_board()

        # 1) load the entire mission dict
        mission_data = load_json('data/objectives.json')[mission]

        # 2) pull off deploy_zones and store for later
        #    (so main_menu can reference game.deploy_zones)
        game.deploy_zones = mission_data.get('deploy_zones', {})

        # build our Objective instances
        game.objectives = [
            Objective(o['id'], o['pos'])
            for o in mission_data.get('objectives', [])
        ]
        #         game.objectives.append( Objective(o['id'], o['pos']) )
                
        #         # now that game.objectives is a list of Objective instances,
        #         # _refresh_board (called later) will place them on the grid
        #         # now iterate only the actual objectives list
        #         if isinstance(o, dict):
        #             oid = o['id']
        #             if 'pos' in o:
        #                 code = o['pos']
        #             else:
        #                 # o['pos'] is a string like "H6"
        #                 game.objectives.append(Objective(o['id'], o['pos']))
        #                 continue
        #         else:
        #             oid = len(game.objectives)+1
        #             code = o

        #     for i in range(1, len(code)):
        #         letters, digits = code[:i], code[i:]
        #         if digits.isdigit():
        #             x = parse_column_label(letters)
        #             y = int(digits) - 1
        #             break
        #     else:
        #         raise ValueError(f"Bad objective pos: {code}")

        #     game.objectives.append(Objective(oid, (x, y)))
        # ]



    def other_player(game):
        return game.players[1 - game.current]

    def current_player(game):
        return game.players[game.current]

    def display_state(game):
        # show the map with objectives  units
        game.board.display(flip=True)
        for obj in game.objectives:
            ctrl = obj.controller or "Contested"
            # use obj.position, not obj.pos
            print(f"Objective {obj.id} at {obj.position}: {ctrl}")


        for u in game.current_player().units:
            # 1) show the normal unit stats
            u.display_stats()
            
            print(f"CP: {game.current_player().cp}   VP: {game.current_player().vp}\n")
            # 2) then enumerate its ranged weapon-groups and their profiles
            print(f"    Ranged Weapons: ")
            for wg in u.datasheet['ranged_weapons']:
                # if it's a group-with-profiles, use that; otherwise single-profile
                profiles = wg.get('profiles') if isinstance(wg, dict) else None
                if profiles:
                    print(f"    Ranged Weapon Group: {wg['name']}")
                else:
                    # old format: wg itgame is a profile
                    profiles = [wg]
            
                for prof in profiles:
                    abil = ",".join(prof['abilities'].names) or "-"
                    rng = prof.get('range', 'N/A')
                    bsws = prof.get('BS', prof.get('WS', ''))
                    print(f"      • {prof['name']}: Range {prof['range']}\"  A={prof['A']}  BS={prof.get('BS', prof.get('WS'))}"
                          f"S={prof['S']}  AP={prof['AP']}  D={prof['D']}  Abils=[{abil}]") 
                    
            # 3) same for melee
            print(f"    Melee Weapons:")
            for wg in u.datasheet['melee_weapons']:
                profiles = wg.get('profiles') if isinstance(wg, dict) else None
                if profiles:
                    print(f"    Melee Weapon Group: {wg['name']}")
                else:
                    profiles = [wg]
                for prof in profiles:
                    abil = ",".join(prof['abilities'].names) or "-"
                    ws = prof.get('WS','')
                    print(f"      • {prof['name']}: A={prof['A']}  WS={ws}  "
                          f"S={prof['S']}  AP={prof['AP']}  D={prof['D']}  Abils=[{abil}]")
            print()


    # now each phase just delegates:
    def command_phase(game):
        return command_phase(game)

    def movement_phase(game):
        return movement_phase(game)

    def shooting_phase(game):
        return shooting_phase(game)

    def charge_phase(game):
        return charge_phase(game)

    def fight_phase(game):
        return fight_phase(game)

    def resolve_damage(game,D):
        if isinstance(D,int): return D
        if isinstance(D,str):
            if D.startswith('D6'):
                parts=D.split('+')
                bonus=int(parts[1]) if len(parts)>1 else 0
                return roll_d6()[0]+bonus
            try: return int(D)
            except: return 0
        return 0

    def play_turn(game):
        # redraw everything (objectives  units) before showing
        game._refresh_board()
        game.display_state()
        game.command_phase()
        game.movement_phase()
        game.shooting_phase()
        if not game.charge_phase(): return
        if not game.fight_phase(): return

        # refresh for next turn
        game._refresh_board()
        game.other_player().remove_dead()
        for u in game.current_player().units:
            u.advanced = u.fell_back = u.charged = False


        # check for end
        if game.round > 5:
            game.is_over()
            print("Round 5 - Game Over!")
            game.show_scoreboard()
            return

        game.current = 1 - game.current
        game.round  += 1

    def is_over(game):
        return game.round > 5 or not all(p.has_units() for p in game.players)

    def _refresh_board(game):
        # clear board
        game.board.grid = [[' ' for _ in range(game.board.width)] for _ in range(game.board.height)]

        # first, draw objectives
        for obj in game.objectives:
            game.board.place_objective(obj)
            
        # then draw units on top…
        for p in game.players:
            for u in p.units:
                if u.is_alive():
                    game.board.place_unit(u)

    def show_scoreboard(game):
        print("\n===== Final Scoreboard =====\n")
        for idx,pl in enumerate(game.players, start=1):
            print(f"P{idx} - {pl.name}")
            print(f"VP: {pl.vp}   CP: {pl.cp}   Total Damage: {pl.total_damage()}   Models Killed: {pl.total_models_killed()}")
            # per-unit breakdown
            headers = ["Unit","Dmg","Rng %","Melee %","Kills"]
            rows = []
            for u in pl.units:
                rows.append([
                    u.name,
                    u.stats['damage_dealt'],
                    f"{u.stats['ranged_hits']}/{u.stats['ranged_attacks']}"
                      if u.stats['ranged_attacks']>0 else "-",
                    f"{u.stats['melee_hits']}/{u.stats['melee_attacks']}"
                      if u.stats['melee_attacks']>0 else "-",
                    u.stats['models_killed'],
                ])
            print_table(headers, rows)
            print()
        # decide winner
        if game.players[0].vp > game.players[1].vp:
            winner = game.players[0]
            pnum   = 1
        elif game.players[1].vp > game.players[0].vp:
            winner = game.players[1]
            pnum   = 2
        else:
            print("The game is a tie!")
            return
        print(f"Winner: P{pnum} - {winner.name}!\n")

        

