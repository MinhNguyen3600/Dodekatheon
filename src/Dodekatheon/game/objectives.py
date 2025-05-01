import json

class Objective:
    def __init__(self, id, pos):
        self.id = id
        self.position = pos
        self.controller = None  # ‘P1’, ‘P2’ or None

