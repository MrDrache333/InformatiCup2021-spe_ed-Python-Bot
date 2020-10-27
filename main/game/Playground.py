from game.player.Player import Player

class Playground(object):

        def __init__(self, coordinateSystem, players):
            self.coordinateSystem = coordinateSystem
            self.players = players

        def lookInInStraightLine(self, player, direction, howFarToLook) -> bool: #TODO make direction ENUM
            """Returns whether something is within the range :param howFarToLook in the direction defined by :param
            direction """
            pass


