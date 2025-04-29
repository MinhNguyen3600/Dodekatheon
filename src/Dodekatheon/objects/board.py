# board.py
import math

class Board:
    def __init__(self, width=15, height=11, terrain=None):
        self.width  = width
        self.height = height
        self.grid   = [[' ' for _ in range(width)] for _ in range(height)]
        self.terrain = terrain or []
        self.terrain = terrain or []

    def _expand_width(self, new_width):
        """Grow every row to new_width columns."""
        for row in self.grid:
            row.extend(' ' for _ in range(new_width - self.width))
        self.width = new_width

    def _expand_height(self, new_height):
        """Add new rows up to new_height."""
        for _ in range(new_height - self.height):
            self.grid.append([' ' for _ in range(self.width)])
        self.height = new_height

    def place_unit(self, unit):
        x, y = unit.position
        # if unit is outside current bounds, grow to fit
        if x < 0 or y < 0:
            raise ValueError(f"Cannot place at negative coordinate {(x,y)}")
        if x >= self.width:
            self._expand_width(x + 1)
        if y >= self.height:
            self._expand_height(y + 1)
        self.grid[y][x] = unit.symbol

    def clear_position(self, x, y):
        # Safely clear even if out-of-bounds
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = ' '

    def move_unit(self, unit, new_x, new_y):
        old_x, old_y = unit.position
        self.clear_position(old_x, old_y)
        unit.position = (new_x, new_y)
        self.place_unit(unit)

    def distance_inches(self, pos1, pos2):
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.hypot(dx, dy)

    def display(self, flip=False, highlight=None):
        """
        highlight: optional set of (x,y) tuples.  Only those cells will show internal grid lines.
        """
        highlight = highlight or set()

        # header
        cols = '   '.join(chr(ord('A') + i) for i in range(self.width))
        print("   ", cols)

        # build top border
        def row_border(y):
            # for each x, if (x,y) or (x,y+1) in highlight then draw +---+ else +   +
            pieces = []
            for x in range(self.width):
                up   = (x, y)     in highlight
                down = (x, y-1)   in highlight
                if up or down:
                    pieces.append("---")
                else:
                    pieces.append("   ")
            return "+" + "+".join(pieces) + "+"

        row_range = range(self.height-1, -1, -1) if flip else range(self.height)
        # topmost border
        print("  " + row_border(self.height-1))
        for y in row_range:
            # row contents: show vertical bars only if that cell is highlighted
            row_cells = []
            for x in range(self.width):
                cell = self.grid[y][x]
                if (x,y) in highlight:
                    row_cells.append(f"| {cell} ")
                else:
                    row_cells.append(f"  {cell} ")
            print(f"{y+1:2}" + "".join(row_cells) + "|")
            print("  " + row_border(y))
