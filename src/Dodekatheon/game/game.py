# game.py
# Game/game.py
from objects.dice import roll_d6
from objects.board import Board

from .command_phase  import command_phase
from .movement_phase import movement_phase
from .shooting_phase import shooting_phase
from .charge_phase   import charge_phase
from .fight_phase    import fight_phase

class Game:
    def __init__(self, p1, p2, board_width=15, board_height=11):
        self.board = Board(board_width, board_height)
        self.players = [p1, p2]
        self.current = 0
        self.round = 1
        # place all units initially
        self._refresh_board()

    def other_player(self):
        return self.players[1 - self.current]

    def current_player(self):
        return self.players[self.current]

    def display_state(self):
        print(f"-- Round {self.round}: {self.current_player().name}'s turn --")
        self.board.display(flip=True)
        for u in self.current_player().units:
            u.display_stats()
        print(f"CP: {self.current_player().cp}\n")

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