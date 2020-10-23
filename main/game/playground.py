from main.game.player.player import Player


class Playground(object):
    def __init__(self, cordinateystem: [int, int], players: [Player]):
        self.cordinatesystem = cordinateystem
        self.players = players
