# src/wh40kgame/__init__.py

# version number
__version__ = "0.1.0"

# expose the things we think of as top-level
from .game      import Game
from .data      import DatasheetLoader
from .objects   import Board, Unit, Player

# you can also set __all__ if you like:
__all__ = ["Game", "DatasheetLoader", "Board", "Unit", "Player"]
