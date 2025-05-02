# src/wh40kgame/game/utils.py
import json, os

def parse_column_label(label):
    """Convert Excel-style column label (A, B, ..., Z, AA, AB...) to 0-based index"""
    total = 0
    for c in label:
        if not ('A' <= c <= 'Z'):
            raise ValueError("Invalid column letter")
        total = total * 26 + (ord(c) - ord('A') + 1)
    return total - 1

def reachable_squares(unit, board, max_dist):
    """
    Return set of (x,y) on board within Euclidean distance ≤ max_dist from unit.position.
    """
    cx, cy = unit.position
    valid = set()
    for x in range(board.width):
        for y in range(board.height):
            # only consider empty squares or the unit’s own square
            if board.grid[y][x] == ' ' or (x, y) == unit.position:
                if board.distance_inches((cx, cy), (x, y)) <= max_dist:
                    valid.add((x, y))
    return valid

def load_json(relpath):
    here = os.path.dirname(__file__)
    full = os.path.abspath(os.path.join(here, '..', relpath))
    with open(full) as f: return json.load(f)

def print_table(headers, rows):
    # simple column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i,cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    # format string
    fmt = "  ".join(f"{{:{w}}}" for w in widths)
    # header
    print(fmt.format(*headers))
    print(fmt.format(*["─"*w for w in widths]))
    # rows
    for row in rows:
        print(fmt.format(*[str(c) for c in row]))

def bdr_s():
    print("---------------") # 15 dashes

def bdr_m():
    print("------------------------------") # 30 dashes

def bdr_l():
    print("----------------------------------------") # 40 dashes
