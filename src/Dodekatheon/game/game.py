# game.py
# Game/game.py
from objects.dice import roll_d6
from objects.board import Board

from .phases.command_phase  import command_phase
from .phases.movement_phase import movement_phase
from .phases.shooting_phase import shooting_phase
from .phases.charge_phase   import charge_phase
from .phases.fight_phase    import fight_phase

class Game:
    def __init__(self, p1, p2, board_width=15, board_height=11):
        self.board = Board(board_width, board_height)

        self.players = [p1, p2]
        self.current = 0
        self.round = 1
        # place all units initially
        # self._refresh_board()
        

    def other_player(self):
        return self.players[1 - self.current]

    def current_player(self):
        return self.players[self.current]

    def display_state(self):
        for u in self.current_player().units:
            # 1) show the normal unit stats
            u.display_stats()

            # 2) then enumerate its ranged weapon-groups and their profiles
            print(f"    Ranged Weapons: ")
            for wg in u.datasheet['ranged_weapons']:
                # if it's a group-with-profiles, use that; otherwise single-profile
                profiles = wg.get('profiles') if isinstance(wg, dict) else None
                if profiles:
                    print(f"    Ranged Weapon Group: {wg['name']}")
                else:
                    # old format: wg itself is a profile
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
    def command_phase(self):
        return command_phase(self)

    def movement_phase(self):
        return movement_phase(self)

    def shooting_phase(self):
        return shooting_phase(self)

    def charge_phase(self):
        return charge_phase(self)

    def fight_phase(self):
        return fight_phase(self)

    def resolve_damage(self,D):
        if isinstance(D,int): return D
        if isinstance(D,str):
            if D.startswith('D6'):
                parts=D.split('+')
                bonus=int(parts[1]) if len(parts)>1 else 0
                return roll_d6()[0]+bonus
            try: return int(D)
            except: return 0
        return 0

    def play_turn(self):
        self.display_state()
        self.command_phase()
        self.movement_phase()
        self.shooting_phase()
        if not self.charge_phase(): return
        if not self.fight_phase(): return
        self._refresh_board()
        self.other_player().remove_dead()
        for u in self.current_player().units:
            u.advanced=u.fell_back=u.charged=False
        self.current=1-self.current; self.round+=1

    def is_over(self):
        return not all(p.has_units() for p in self.players)

    def _refresh_board(self):
        self.board.grid = [[' ' for _ in range(self.board.width)]
                           for _ in range(self.board.height)]
        for p in self.players:
            for u in p.units:
                if u.is_alive(): self.board.place_unit(u)