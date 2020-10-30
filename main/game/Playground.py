from game.player.DirectionOfLooking import DirectionOfLooking
from game.player.Player import Player


class Playground(object):

    def __init__(self, coordinateSystem, players):
        self.coordinateSystem = coordinateSystem
        self.players = players

    def lookInInStraightLine(self, player, direction, howFarToLook) -> bool:  # TODO make direction ENUM
        """Returns whether something is within the range :param howFarToLook in the direction defined by :param
            direction """
        pass

    def movePlayer(self):
        for player in self.players:
            # read speed,direction, position and activity of player
            # determine whether player would colide with a wall
            # move player to new position
            # create walls where the player moved
            # move on to the next player

            if (player.active):
                xCoordinateOfPlayer = player.x
                yCoodinateOfPlayer = player.y
                speedOfPlayer = player.speed
                directionOfPlayer = player.directionOfLooking

                if (directionOfPlayer == DirectionOfLooking.LEFT):
                    xCoordinateOfPlayer -= speedOfPlayer
                elif (directionOfPlayer == DirectionOfLooking.UP):
                    yCoodinateOfPlayer -= speedOfPlayer
                elif (directionOfPlayer == DirectionOfLooking.RIGHT):
                    xCoordinateOfPlayer += speedOfPlayer
                elif (directionOfPlayer == DirectionOfLooking.DOWN):
                    yCoodinateOfPlayer += speedOfPlayer

                # determine whether player would collide with a wall
                # determine whether coordinates are within coordinatesystem
                if (xCoordinateOfPlayer <= len(self.coordinateSystem[0]) and yCoodinateOfPlayer <= len(
                        self.coordinateSystem)):
                    if (self.coordinateSystem[xCoordinateOfPlayer][yCoodinateOfPlayer] == 0):
                        # Player did not collide with wall

                        # update player coords
                        player.x = xCoordinateOfPlayer
                        player.y = yCoodinateOfPlayer

                        # update coordinate system
                        self.coordinateSystem[xCoordinateOfPlayer][yCoodinateOfPlayer] = player.id
                        # TODO draw walls where the player moved
