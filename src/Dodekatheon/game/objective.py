import json
from .utils import *

class Objective:
    def __init__(self, id, pos):
        self.id = id

        # pos may be a tuple or a string like "D13"
        if isinstance(pos, str):
            # split letters / digits
            col = ''.join(filter(str.isalpha, pos))
            row = ''.join(filter(str.isdigit, pos))
            x = parse_column_label(col)
            y = int(row) - 1
            self.position = (x, y)
        else:
            self.position = pos

        self.controller = None

    
    def place_objective(self, obj):
        """Place an objective marker on the grid."""
        x,y = obj.position
        # show the objective id (or “S” for “standard” objective)
        self.grid[y][x] = 'O'  # or str(obj.id) or '*' or whatever symbol you want
        
    def update_objective_control(game):
        for obj in game.objectives: 
            # count OC for each player
            levels = {'P1': 0, 'P2': 0}
            for player_key, player in [('P1', game.current_player()), ('P2', game.other_player())]:
                for u in player.units:
                    if not u.is_alive(): continue
                    # for each model in unit
                    for _ in range(u.current_models):
                        if game.board.distance_inches(u.position, obj.position) <= 3:
                            levels[player_key] += u.datasheet['OC']
            # decide controller
            if levels['P1'] > levels['P2']:
                obj.controller = 'P1'
            elif levels['P2'] > levels['P1']:
                obj.controller = 'P2'
            else:
                obj.controller = None

