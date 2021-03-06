import copy
import logging
import sys

from game.player.DirectionOfLooking import DirectionOfLooking

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()


class Playground(object):
    def __init__(self, coordinateSystem, players):
        self.coordinateSystem = coordinateSystem
        self.players = players
        self.turn = 1

    def update(self, coordinateSystem, players):
        """
        Updates the playground
        :param coordinateSystem: all coordinates
        :param players: all players
        """
        self.coordinateSystem = coordinateSystem
        for player in self.players:
            player.x = players[player.id - 1].x
            player.y = players[player.id - 1].y
            player.active = players[player.id - 1].active
            player.speed = players[player.id - 1].speed
            player.directionOfLooking = players[player.id - 1].directionOfLooking

    def killPlayer(self, player):
        """
        Player must have run into something so he dies.
        :param player: player that dies
        """
        player.die()

    def addTurn(self):
        """
        Adds one each turn to the turn counter, to keep track when a jump takes place
        """
        if self.turn == 6:
            self.turn = 1
        else:
            self.turn += 1

    def getTurn(self):
        """
        Returns the current turn counter
        :return: turn counter
        """
        return self.turn

    def lookInInStraightLine(self, player, direction: DirectionOfLooking, howFarToLook) -> int:
        """
        Returns how far away a wall is within a given range in the direction defined
        by :param direction. Returns -1 if there is no wall within the given Range
        :param player: player
        :param direction: direction to look
        :param howFarToLook: amount of blocks to check
        :return: amount of free blocks in the direction
        """
        nextX, nextY = direction.value
        currentX, currentY = player.x, player.y

        for i in range(howFarToLook):
            currentX += nextX
            currentY += nextY

            # out of range
            if (currentX < 0 or currentY < 0 or currentX >= len(self.coordinateSystem[0]) or currentY >= len(
                    self.coordinateSystem)):  # 46 x 75
                return i + 1
            else:
                if self.coordinateSystem[currentY][currentX] != 0:
                    return i + 1
        return -1

    def countBlocksInStraightLine(self, ownplayer, direction: DirectionOfLooking) -> int:
        """
        Returns the amount of cells that are free in a direction of looking from the position of the given player.
        Returns zero if there is an obstacle directly adjacent to the player
        :param ownplayer: player
        :param direction: direction in that the blocks shall be counted
        :return: amount of free blocks
        """
        player = copy.deepcopy(ownplayer)
        nextX, nextY = direction.value
        currentX, currentY = player.x, player.y

        blockIsFree = True
        blocksFree = 0
        while blockIsFree:
            currentX += nextX
            currentY += nextY

            # check if out of range
            if (currentX < 0 or currentY < 0 or currentX >= len(self.coordinateSystem[0]) or currentY >= len(
                    self.coordinateSystem)):  # 46 x 75
                blockIsFree = False
            else:
                if self.turn == 6 and player.speed != (blocksFree + 1) and (blocksFree + 1) <= (player.speed - 2):
                    blocksFree += 1
                else:
                    if self.coordinateSystem[currentY][currentX] != 0:
                        blockIsFree = False
                    else:
                        blocksFree += 1
        return blocksFree

    def getPlayerForId(self, id):
        """
        Returns the Player for the given Id by iterating over all players
        :param id: The id of the Player to return
        :return: The Player or None if none matches the given id
        """
        for player in self.players:
            if player.id == id:
                return player
        return None

    def movePlayer(self):
        """
        Move all player in game
        """
        # read speed,direction, position and activity of player
        # determine whether player would colide with a wall
        # move player to new position
        # create walls where the player moved
        # move on to the next player
        allPlayerCoordinates = []
        for player in self.players:
            if player.active:
                died = False
                xCoordinateOfPlayer = player.x
                yCoordinateOfPlayer = player.y
                speedOfPlayer = player.speed
                directionOfPlayer = player.directionOfLooking

                nextX, nextY = directionOfPlayer.value

                playerCoordinates = []
                # draws a line for each speed point
                for speed in range(1, speedOfPlayer + 1):

                    xCoordinateOfPlayer += nextX
                    yCoordinateOfPlayer += nextY

                    for allPlayerCoordinate in allPlayerCoordinates:
                        if (
                            allPlayerCoordinate[0][0] == xCoordinateOfPlayer
                            and allPlayerCoordinate[0][1] == yCoordinateOfPlayer
                        ):
                            died = True
                            self.killPlayer(self.players[self.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer] - 1])
                            self.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer] = -1

                    playerCoordinates.append((xCoordinateOfPlayer, yCoordinateOfPlayer))

                    #   6. turn & not the last move position (head) &
                    if not (self.turn == 6 and speed != 1 and speed != speedOfPlayer):
                        # determine whether player would collide with a wall
                        # determine whether coordinates are within coordinatesystem
                        if (0 <= xCoordinateOfPlayer < len(self.coordinateSystem[0]) and
                                0 <= yCoordinateOfPlayer < len(self.coordinateSystem)):
                            if self.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer] == 0:
                                # Player did not collide with wall

                                # update player coords
                                player.x = xCoordinateOfPlayer
                                player.y = yCoordinateOfPlayer

                                # update coordinate system
                                if not died:
                                    self.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer] = int(player.id)
                            else:
                                died = True
                                break
                        else:
                            died = True
                            break
                allPlayerCoordinates.append(playerCoordinates)
                if died:
                    self.killPlayer(player)
