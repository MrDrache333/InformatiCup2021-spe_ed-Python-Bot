from game.players import player


class Playfield(object):
    def __init__(self, playfield: [int, int], players : [player]):
        self.playfield = playfield
        self.players = players


