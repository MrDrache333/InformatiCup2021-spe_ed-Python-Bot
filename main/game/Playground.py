from game.player.Player import Player

class Playground(object):

        def __init__(self, cordinateSystem: [int, int], players: [Player]):
            self.coordinateSystem = cordinateSystem
            self.players = players

        def lookInInStraightLine(self, player: Player, direction, howFarToLook: int): #TODO make direction ENUM
            """Returns whether something is within the range :param howFarToLook in the direction defined by :param
            direction """
            pass


