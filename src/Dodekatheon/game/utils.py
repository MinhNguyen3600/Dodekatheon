# src/wh40kgame/game/utils.py

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
