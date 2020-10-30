import logging

from game.player.DirectionOfLooking import DirectionOfLooking


class Playground(object):

    def __init__(self, coordinateSystem, players):
        self.coordinateSystem = coordinateSystem
        self.players = players

    def lookInInStraightLine(self, player, direction, howFarToLook) -> bool:  # TODO make direction ENUM
        """Returns whether something is within the range :param howFarToLook in the direction defined by :param
            direction """
        pass

    def movePlayer(self, turn):
        for player in self.players:
            # read speed,direction, position and activity of player
            # determine whether player would colide with a wall
            # move player to new position
            # create walls where the player moved
            # move on to the next player

            if (player.active):
                xCoordinateOfPlayer = player.x
                yCoordinateOfPlayer = player.y
                speedOfPlayer = player.speed
                directionOfPlayer = player.directionOfLooking

                #draws a line for each speed point
                for speed in range(speedOfPlayer):
                    if directionOfPlayer == DirectionOfLooking.LEFT:
                        xCoordinateOfPlayer -= 1
                    elif directionOfPlayer == DirectionOfLooking.UP:
                        yCoordinateOfPlayer -= 1
                    elif directionOfPlayer == DirectionOfLooking.RIGHT:
                        xCoordinateOfPlayer += 1
                    elif directionOfPlayer == DirectionOfLooking.DOWN:
                        yCoordinateOfPlayer += 1

                    if turn == 6 and speedOfPlayer >= 3 and speed+1 != speedOfPlayer and speed+1 >= speedOfPlayer -2:
                        logging.debug("Ima skip dat field")
                    else:
                        # determine whether player would collide with a wall
                        # determine whether coordinates are within coordinatesystem
                        if (0 <= xCoordinateOfPlayer < len(self.coordinateSystem[0]) and
                                0 <= yCoordinateOfPlayer < len(self.coordinateSystem)):
                            if (self.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer] == 0):
                                # Player did not collide with wall

                                # update player coords
                                player.x = xCoordinateOfPlayer
                                player.y = yCoordinateOfPlayer

                                # update coordinate system
                                self.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer] = int(player.id)
                                # TODO draw walls where the player moved
                            else:
                                self.killPlayer(player)
                                break
                        else:
                            self.killPlayer(player)
                            break

    def killPlayer(self, player):
        print("Player: " + str(player.id) + " died at X: " + str(player.x) + " and Y: " + str(player.y))
        player.die()