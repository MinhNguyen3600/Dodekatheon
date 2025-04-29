# unit.py
from objects.dice import roll_d6, roll_d3
import math

class Unit:
    _id_counter = 1

    def __init__(self, name, symbol, x, y, datasheet):
        self.id = Unit._id_counter
        Unit._id_counter += 1
        self.name = name
        self.symbol = symbol
        
        self.position = (x, y)
        self.datasheet = datasheet

        # squad size (1 for characters, >1 for multi-model units)
        self.size = datasheet.get('size', 1)

        # wounds per individual model
        self.wounds_per_model = datasheet['W']

        # total pooled wounds for the squad
        self.max_wounds = self.size * self.wounds_per_model
        self.current_wounds = self.max_wounds

        self.advanced = False
        self.fell_back = False
        self.charged = False

    def is_alive(self):
        return self.current_wounds > 0

    def take_damage(self, d=1):
        # subtract from pooled wounds
        self.current_wounds = max(0, self.current_wounds - d)

    @property
    def current_models(self):
        # how many individual models remain (round up)
        return math.ceil(self.current_wounds / self.wounds_per_model)

    def display_stats(self):
        ds = self.datasheet
        print(
            f"{self.name} (ID {self.id}) - Pos:{self.position} "
            f"Wounds:{self.current_wounds}/{self.max_wounds} "
            f"Models:{self.current_models}/{self.size} "
            f"M:{ds['M']} T:{ds['T']} Sv:{ds['Sv']} W:{ds['W']}"
        )
