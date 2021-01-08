import copy
import logging
import random
import sys

import numpy as np

from game.Playground import Playground
from game.player import FreePlaceFinder
from game.player.DirectionOfLooking import DirectionOfLooking
from game.player.Pathfinding import AStar

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger()
logger.disabled = True


def checkIfCoordinateIsInCoordinateSystem(givenX, givenY, coordinateSystem):
    return (
            len(coordinateSystem) > givenY >= 0
            and len(coordinateSystem[0]) > givenX >= 0
    )


def printMatrix(matrix):
    for y in matrix:
        line = "".join(
            ((str(x) if len(str(x)) == 2 else "0" + str(x)) + " ") for x in y
        )

        print(line)


class Player(object):
    def __init__(self, id: int, x: int, y: int, directionOfLooking: str, active: bool, speed: int):
        self.id = id
        self.x = x
        self.y = y
        self.directionOfLooking = DirectionOfLooking[directionOfLooking.upper()]
        self.active = active
        self.speed = speed
        self.path = []
        self.fitness = 0
        self.choosenTurn = "change_nothing"
        self.followPath = False
        self.nextTurn = None

    def isCoordinateFree(self, x, y, playground):
        return playground.coordinateSystem[y][x] == 0

    def turnDirectionOfLooking(self, directionOfLooking: DirectionOfLooking):
        """Turns current direction to given direction if possible"""
        if directionOfLooking == self.directionOfLooking or directionOfLooking.value == self.directionOfLooking.value * -1:
            logging.debug(
                'Cant change direction, reason: Input direction is in opposite or same direction as previous one ')
        else:
            if self.directionOfLooking == DirectionOfLooking.UP:
                if directionOfLooking == DirectionOfLooking.LEFT:
                    self.choosenTurn = "turn_left"
                elif directionOfLooking == DirectionOfLooking.RIGHT:
                    self.choosenTurn = "turn_right"
            if self.directionOfLooking == DirectionOfLooking.DOWN:
                if directionOfLooking == DirectionOfLooking.RIGHT:
                    self.choosenTurn = "turn_left"
                elif directionOfLooking == DirectionOfLooking.LEFT:
                    self.choosenTurn = "turn_right"
            if self.directionOfLooking == DirectionOfLooking.LEFT:
                if directionOfLooking == DirectionOfLooking.DOWN:
                    self.choosenTurn = "turn_left"
                elif directionOfLooking == DirectionOfLooking.UP:
                    self.choosenTurn = "turn_right"
            if self.directionOfLooking == DirectionOfLooking.RIGHT:
                if directionOfLooking == DirectionOfLooking.UP:
                    self.choosenTurn = "turn_left"
                elif directionOfLooking == DirectionOfLooking.DOWN:
                    self.choosenTurn = "turn_right"
            self.directionOfLooking = directionOfLooking

    def simulateNextTurn(self, playground: Playground, playerId, directionOfLooking: DirectionOfLooking = None,
                         speedChange=0):
        """
        Simulates if the next Turn could possibly kill us by checking every possible Combination of all Players in a
        10 Block Radius for the next Turn.
        :param playground: The Playground to simulate the Game on
        :param playerId: The Id of the Player to Simulate
        :param directionOfLooking: The new direction of looking if set, to be used
        :param speedChange: The Speedchange relative to the current Speed
        :return: If the Chance to be alive is over 70%
        """
        if directionOfLooking is not None and speedChange != 0:
            print("Invalid Parameters")
            return None
        nextPlayground = copy.deepcopy(playground)

        if speedChange != 0:
            if speedChange < 0:
                nextPlayground.players[playerId - 1].speedDown()
            elif speedChange > 0:
                nextPlayground.players[playerId - 1].speedUp()
        elif directionOfLooking is not None:
            nextPlayground.players[playerId - 1].turnDirectionOfLooking(directionOfLooking)

        # Filter nearest Players to avoid irrelevant calculations
        nearestPlayers = []
        ownPlayer = nextPlayground.players[playerId - 1]
        for player in nextPlayground.players:
            if player.id == ownPlayer.id:
                continue
            if abs(ownPlayer.x - player.x) + abs(ownPlayer.y - player.y) < 10:
                nearestPlayers.append(player)

        # Create Array to store current Turn
        playerTurnCountArray = [0 for _ in nearestPlayers]
        if not playerTurnCountArray:
            return True
        # Iterate over all possible Combinations of enemy Turns
        IterationsDone = False
        # Alive Iterations
        alive = 0
        # Iteration Cout
        iterations = 0
        while not IterationsDone:

            for nearestPlayer in nearestPlayers:
                playgroundPlayer = nextPlayground.getPlayerForId(nearestPlayer.id)
                if playgroundPlayer is not None:
                    """Turns:
                    0: Go Left
                    1: Go Right
                    2: Change Nothing
                    3: Slow Down
                    4: Speed Up
                    """
                    if playerTurnCountArray is 0:
                        if playgroundPlayer.directionOfLooking == DirectionOfLooking.UP:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.LEFT)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.DOWN:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.LEFT:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.DOWN)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.RIGHT:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.UP)
                    elif playerTurnCountArray is 1:
                        if playgroundPlayer.directionOfLooking == DirectionOfLooking.UP:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.DOWN:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.LEFT)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.LEFT:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.UP)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.RIGHT:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.DOWN)
                    elif playerTurnCountArray is 3:
                        playgroundPlayer.speedDown()
                    elif playerTurnCountArray is 4:
                        playgroundPlayer.speedUp()

            # Move every player and check if own player is alive
            for player in nextPlayground.players:
                nextPlayground.movePlayer(player.id - 1)
            if nextPlayground.players[playerId - 1].active:
                alive += 1

            # Count up the Iterations
            iterations += 1
            playerTurnCountArray[0] += 1

            # Count up if current turn is >= 4 and stop if its last entry in list
            for index in range(len(playerTurnCountArray)):
                current = playerTurnCountArray[index]
                if current > 4 and index < len(playerTurnCountArray) - 1:
                    playerTurnCountArray[index] = 0
                    playerTurnCountArray[index + 1] += 1

            # Check if all Turns have been calculated
            for playerTurnCount in playerTurnCountArray:
                IterationsDone = True
                if playerTurnCount <= 4:
                    IterationsDone = False
        if alive == 0:
            return False
        return (iterations / alive) > 0.7

    def speedUp(self):
        """Accelerate one speed"""
        if self.speed == 10:
            logging.debug('Cant accelerate, reason: I Am Speed! (Speed = 10)')
        else:
            self.choosenTurn = "speed_up"
            self.speed += 1

    def speedDown(self):
        """Decelerates one speed"""
        if self.speed == 1:
            logging.debug('Cant decelerate, reason: Don\'t stop me now! (Speed =1 )')
        else:
            self.choosenTurn = "slow_down"
            self.speed -= 1

    def updatePlayer(self, id: int, x: int, y: int, directionOfLooking: DirectionOfLooking, active: bool, speed: int):
        """Updates the player"""
        if id != self.id:
            logging.debug('No matching ID of player')
        else:
            self.x = x
            self.y = y
            self.directionOfLooking = directionOfLooking
            self.active = active
            self.speed = speed

    def die(self):
        """Player cant move any further so it dies"""
        self.speed = 0
        self.path = []
        self.active = False

    def doesSpeedUpMakeSense(self, playground, speedchange):
        if speedchange <= 0:
            return None
        nextPlayground = copy.deepcopy(playground)

        # Spieler und eigenen Spieler virtuell weiter bewegen
        alive = 0
        for _ in range(speedchange):
            alive = (alive + 1) if self.simulateNextTurn(nextPlayground, self.id, None, 1) else alive
            nextPlayground.players[self.id - 1].speedUp()
            for player in nextPlayground.players:
                nextPlayground.movePlayer(player.id - 1)
            nextPlayground.addTurn()

        # Prüfen, ob virtuelle Bewegung eigenen Spieler schadet
        if alive is speedchange:
            temp_maxval, temp_maxvalX, temp_maxvalY, temp_tempCS = self.findFurthestField(
                nextPlayground, self.speed + speedchange)

            # Iteriere über größtes feld, prüfe ob punkt erreichbar, merke, siehe nächsten bis alle fertig
            freeMap = FreePlaceFinder.generateFreePlaceMap(playground.coordinateSystem)
            freeMapValues = FreePlaceFinder.getFreePlaceValues(freeMap)
            maxFreePlaceIndex = freeMapValues.index(max(freeMapValues))
            ownFreePlaceIndex = FreePlaceFinder.getRelativeFreePlaceIndexForCoordinate(freeMap, self.x, self.y)

            moveMap = FreePlaceFinder.convertFindFurthestFieldMapToFreePlaceFormat(temp_tempCS)

            nearestCoordinateOnFurthestFieldMap = FreePlaceFinder.findNearestCoordinateOnFurthestFieldMap(freeMap,
                                                                                                          moveMap,
                                                                                                          maxFreePlaceIndex + 1,
                                                                                                          self.speed + speedchange,
                                                                                                          self.x,
                                                                                                          self.y)

            if nearestCoordinateOnFurthestFieldMap is not None and freeMapValues[maxFreePlaceIndex] - freeMapValues[
                ownFreePlaceIndex] > 30:

                # Neuen Pfad berechnen
                finder = AStar(nextPlayground.coordinateSystem, nextPlayground.players[self.id - 1].x,
                               nextPlayground.players[self.id - 1].y, self.speed + speedchange,
                               nextPlayground.getTurn())
                self.path = finder.solve(nearestCoordinateOnFurthestFieldMap)
                self.followPath = True
                self.speedUp()
                # Falls Doppelsprung -> nächsten Zug als SpeedUp festlegen
                if speedchange > 1:
                    self.nextTurn = "speed_up"
                return True

        return False

    def tryToSurvive(self, playground):
        """Different strategies to keep the player alive"""
        if not self.active:
            return
        self.choosenTurn = "change_nothing"
        if self.nextTurn is not None:
            # TODO Nächten Zug überprüfen auf andere Umgebungsbedingungen
            if self.nextTurn == "speed_up":

                if self.simulateNextTurn(playground, self.id, None, 1):
                    self.choosenTurn = copy.deepcopy(self.nextTurn)
                    self.nextTurn = None
                    return
                else:
                    logger.disabled = False
                    logger.debug("[" + str(self.id) + "]: Doppelter Speedup abgebrochen! Hindernis erkannt.")
                    self.nextTurn = None

        if self.followPath and self.path is not None and len(self.path) > 0:
            # Teste nächsten Pfadpunkt einmal und prüfe, ob noch lebend. -> Wenn ja, dann übernehmen.
            nextCoord = self.path.pop(0)
            while nextCoord[0] == self.x and nextCoord[1] == self.y:
                nextCoord = self.path.pop(0)

            # Neuen Pfad berechnen
            finder = AStar(playground.coordinateSystem, playground.players[self.id - 1].x,
                           playground.players[self.id - 1].y, self.speed,
                           playground.getTurn())
            path = finder.solve(nextCoord)
            if path is not None and len(path) > 0:
                nextDirection = None
                if nextCoord[0] > self.x:
                    nextDirection = DirectionOfLooking.RIGHT
                elif nextCoord[0] < self.x:
                    nextDirection = DirectionOfLooking.LEFT
                elif nextCoord[1] > self.y:
                    nextDirection = DirectionOfLooking.DOWN
                elif nextCoord[1] < self.y:
                    nextDirection = DirectionOfLooking.UP

                # Simulate Turn
                if self.simulateNextTurn(playground, self.id, nextDirection):
                    self.turnDirectionOfLooking(nextDirection)
                    return
            self.path = None
            self.followPath = False
        elif self.followPath:
            self.followPath = False

        # Strategie: Weit entferntestes Feld finden
        maxval, maxvalX, maxvalY, tempCS = self.findFurthestField(playground, self.speed)

        # FreeMap erstellen
        freeMap = FreePlaceFinder.generateFreePlaceMap(playground.coordinateSystem)
        freeMapValues = FreePlaceFinder.getFreePlaceValues(freeMap)
        maxFreePlaceIndex = freeMapValues.index(max(freeMapValues))
        ownFreePlaceIndex = FreePlaceFinder.getRelativeFreePlaceIndexForCoordinate(freeMap, self.x, self.y)

        # Wenn keine Fehler beim erstellen der FreePlaceMap auftreten
        if freeMapValues is not None and ownFreePlaceIndex is not None and maxFreePlaceIndex is not None:
            # Wenn wir uns bereits in dem größten freien Platz befinden
            if freeMapValues[ownFreePlaceIndex] == freeMapValues[maxFreePlaceIndex]:
                # Wenn wir schneller als die Mindestgeschwindigkeit sind
                if self.speed > 1:
                    logger.disabled = False
                    logger.debug("[" + str(self.id) + "]: Already in Area with max free Space of " + str(
                        freeMapValues[maxFreePlaceIndex]) + " Pixels. Slowing down to maximize Livetime!")

                    # Prüfen, ob der nächste SpeedDown uns töten würde. Wenn nicht -> Slow Down
                    if self.simulateNextTurn(playground, self.id, None, -1):
                        self.speedDown()
                        return
                # Da wir uns im größten freien Bereich befinden -> Zeit schinden
                self.rideAlongSideWall(playground)
                return
            else:
                # Wenn wir uns nicht im größten freien Bereich befinden
                moveMap = FreePlaceFinder.convertFindFurthestFieldMapToFreePlaceFormat(tempCS)
                # Prüfen, ob wir mit der aktuellen Geschwindigkeit in den größten freien Bereich kommen würden
                nearestCoordinateOnFurthestFieldMap = FreePlaceFinder.findNearestCoordinateOnFurthestFieldMap(freeMap,
                                                                                                              moveMap,
                                                                                                              maxFreePlaceIndex + 1,
                                                                                                              self.speed,
                                                                                                              self.x,
                                                                                                              self.y)

                if nearestCoordinateOnFurthestFieldMap is not None:
                    if self.moveToFurthestField(playground, nearestCoordinateOnFurthestFieldMap[0],
                                                nearestCoordinateOnFurthestFieldMap[1]):
                        return
                else:
                    # Wenn wir den größtmöglichen freien Bereich nicht erreichen können mit der aktuellen geschwindigkeit
                    # Wenn die Maximalgeschwindigkeit noch nicht erreicht ist
                    if self.speed < 10:
                        # Prüfen ob eine Geschwindigkeitsänderung was bringt
                        if self.doesSpeedUpMakeSense(playground, 1):
                            return
                        elif self.doesSpeedUpMakeSense(playground, 2):
                            return
                        elif self.doesSpeedUpMakeSense(playground, 3):
                            return
                        elif self.doesSpeedUpMakeSense(playground, 4):
                            return

        self.rideAlongSideWall(playground)
        return

    def rideAlongSideWall(self, playground):
        """Finds the nearest Wall and tries to ride alongside it while reducing the players speed to 1. The resulting
        Pattern results into a spiral. This Method ignores one cell wide indents in a wall.
        ATTENTION: This method only does one action per call. E.g. This Method only slows down the player or turns him
        according to the aforementioned plan. This means this method has to be called multiple rounds in a row to
        accomplish said plan."""
        # 1. Find nearest Wall
        # 2. Turn to nearest wall
        # 3. Try to reduce Speed
        # 4. Turn clockwise in cul de sac
        # 5. Scan if next cell is a odd shaped cul de sac or an one wide indent
        # 6. ride alongside wall
        # 7. If next wallpiece is straight, reduce speed
        # 8. Go to 4.
        logger.debug("Ride alongside wall")

        freeBlocks = {DirectionOfLooking.UP: playground.countBlocksInStraightLine(self, DirectionOfLooking.UP),
                      DirectionOfLooking.RIGHT: playground.countBlocksInStraightLine(self, DirectionOfLooking.RIGHT),
                      DirectionOfLooking.DOWN: playground.countBlocksInStraightLine(self, DirectionOfLooking.DOWN),
                      DirectionOfLooking.LEFT: playground.countBlocksInStraightLine(self, DirectionOfLooking.LEFT)}

        setOfDirections = [DirectionOfLooking.UP, DirectionOfLooking.RIGHT, DirectionOfLooking.DOWN,
                           DirectionOfLooking.LEFT]

        freeBlocks.pop(setOfDirections[(setOfDirections.index(self.directionOfLooking) + 2) % 4])

        freeBlocksWithoutDuplicateValues = {}

        # remove double values from freeBlocks, so that "min" operation does not  fail
        for key, value in freeBlocks.items():
            if value not in freeBlocksWithoutDuplicateValues.values():
                freeBlocksWithoutDuplicateValues[key] = value

        distanceOfNearestWall, directionOfClosestWall = min(
            zip(freeBlocksWithoutDuplicateValues.values(), freeBlocksWithoutDuplicateValues.keys()))

        lookDirectionAlongSideWallLeft, lookDirectionAlongSideWallRight = setOfDirections[
                                                                              (setOfDirections.index(
                                                                                  self.directionOfLooking) + 3) % 4], \
                                                                          setOfDirections[
                                                                              (setOfDirections.index(
                                                                                  self.directionOfLooking) + 1) % 4]

        freePlaceMap = FreePlaceFinder.generateFreePlaceMap(playground.coordinateSystem)
        freePlaceValues = FreePlaceFinder.getFreePlaceValues(freePlaceMap)

        directionOfLookinXY = self.x + self.directionOfLooking.value[0], self.y + self.directionOfLooking.value[1]
        lookDirectionAlongsideWallLeftXY = self.x + lookDirectionAlongSideWallLeft.value[0], self.y + \
                                           lookDirectionAlongSideWallLeft.value[1]
        lookDirectionAlongSideWallRightXY = self.x + lookDirectionAlongSideWallRight.value[0], self.y + \
                                            lookDirectionAlongSideWallRight.value[1]

        if distanceOfNearestWall == 0:
            if not playground.countBlocksInStraightLine(self, self.directionOfLooking) == 0:
                # the player is adjacent to a wall and not looking at it. Commence plan.
                # if the player would hit a wall, change direction

                if freeBlocks.get(self.directionOfLooking) < self.speed:
                    # not enough space in direction of player. change direction
                    oppositeDirectionOfPlayerLookingDirection = setOfDirections[
                        (setOfDirections.index(self.directionOfLooking) + 1) % 4]
                    self.turnDirectionOfLooking(oppositeDirectionOfPlayerLookingDirection)
                else:
                    # if the player would move into a one wide gap, change direction

                    # go one field forward look left and right
                    currentX, currentY = self.x, self.y
                    currentX += self.directionOfLooking.value[0]
                    currentY += self.directionOfLooking.value[1]

                    isGapOneCellWide = 0
                    for direction in freeBlocks.keys():
                        tempX = currentX + direction.value[0]
                        tempY = currentY + direction.value[1]
                        # check if coordinate is within system
                        if checkIfCoordinateIsInCoordinateSystem(tempX, tempY, playground.coordinateSystem):
                            if not playground.coordinateSystem[tempY][tempX] == 0:
                                isGapOneCellWide += 1

                    if isGapOneCellWide >= 2:
                        # Cell is one wide. check if space behind cell is larger, than the

                        if FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, directionOfLookinXY[0],
                                                                              directionOfLookinXY[1],
                                                                              freePlaceValues) >= (
                                FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                   lookDirectionAlongsideWallLeftXY[0],
                                                                                   lookDirectionAlongsideWallLeftXY[1],
                                                                                   freePlaceValues)
                                or FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                      lookDirectionAlongSideWallRightXY[
                                                                                          0],
                                                                                      lookDirectionAlongSideWallRightXY[
                                                                                          1], freePlaceValues)):
                            if self.simulateNextTurn(playground, self.id, self.directionOfLooking):
                                self.speedDown()
                                return
                            elif FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                    lookDirectionAlongsideWallLeftXY[0],
                                                                                    lookDirectionAlongsideWallLeftXY[1],
                                                                                    freePlaceValues) \
                                    >= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                          lookDirectionAlongSideWallRightXY[
                                                                                              0],
                                                                                          lookDirectionAlongSideWallRightXY[
                                                                                              1], freePlaceValues):
                                self.turnDirectionOfLooking(lookDirectionAlongSideWallLeft)
                                return
                            else:
                                self.turnDirectionOfLooking(lookDirectionAlongSideWallRight)
                                return

                        elif FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                lookDirectionAlongsideWallLeftXY[0],
                                                                                lookDirectionAlongsideWallLeftXY[1],
                                                                                freePlaceValues) \
                                >= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                      lookDirectionAlongSideWallRightXY[
                                                                                          0],
                                                                                      lookDirectionAlongSideWallRightXY[
                                                                                          1], freePlaceValues):
                            self.turnDirectionOfLooking(lookDirectionAlongSideWallLeft)
                            return
                        else:
                            self.turnDirectionOfLooking(lookDirectionAlongSideWallRight)
                            return
                    else:
                        self.speedDown()
                        return

            else:
                # player is adjacent to wall and looking into it. Player has to change his direction of looking
                # Change direction of looking to the direction with the most space available

                if FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, lookDirectionAlongsideWallLeftXY[0],
                                                                      lookDirectionAlongsideWallLeftXY[1],
                                                                      freePlaceValues) \
                        > FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                             lookDirectionAlongSideWallRightXY[0],
                                                                             lookDirectionAlongSideWallRightXY[1],
                                                                             freePlaceValues):
                    self.turnDirectionOfLooking(lookDirectionAlongSideWallLeft)
                    return
                else:
                    self.turnDirectionOfLooking(lookDirectionAlongSideWallRight)
                    return
        else:
            # check if a wall is behind the player, if so, go there
            # get direction of wall behind player
            setOfDirectionsWithDiagonals = [DirectionOfLooking.UP, DirectionOfLooking.UPRIGHT, DirectionOfLooking.RIGHT,
                                            DirectionOfLooking.DOWNRIGHT, DirectionOfLooking.DOWN,
                                            DirectionOfLooking.DOWNLEFT, DirectionOfLooking.LEFT,
                                            DirectionOfLooking.UPLEFT]

            """directionBehindPlayerLeft = setOfDirectionsWithDiagonals[
                (setOfDirectionsWithDiagonals.index(self.directionOfLooking) + 5) % 8]
            directionBehindPlayerRight = setOfDirectionsWithDiagonals[
                (setOfDirectionsWithDiagonals.index(self.directionOfLooking) + 3) % 8]

            # check if there is a wall behind the player on the left
            # and if left is more space than right

            directionLeftOfPlayer = setOfDirectionsWithDiagonals[(setOfDirectionsWithDiagonals.index(self.directionOfLooking) + 6) % 8]
            directionRightOfPlayer = setOfDirectionsWithDiagonals[(setOfDirectionsWithDiagonals.index(self.directionOfLooking) + 2) % 8]
            leftXYOfPlayer = self.x + directionLeftOfPlayer.value[0], self.y + directionLeftOfPlayer.value[1]
            rightXYOfPlayer = self.x + directionRightOfPlayer.value[0], self.y + directionRightOfPlayer.value[1]

            if playground.coordinateSystem[self.y + directionBehindPlayerLeft.value[1]][
                self.x + directionBehindPlayerLeft.value[0]] != 0 \
                    and FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, leftXYOfPlayer[0],leftXYOfPlayer[1],freePlaceValues)\
                    >= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, rightXYOfPlayer[0],rightXYOfPlayer[1],freePlaceValues):

                self.turnDirectionOfLooking(directionLeftOfPlayer)
                return

            #check if there is a wall right behind the player, and there is more space than on the left
            elif playground.coordinateSystem[self.y + directionBehindPlayerRight.value[1]][
                self.x + directionBehindPlayerRight.value[0]] != 0 \
                    and FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, leftXYOfPlayer[0],leftXYOfPlayer[1],freePlaceValues) \
                    <= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, rightXYOfPlayer[0],rightXYOfPlayer[1],freePlaceValues):

                self.turnDirectionOfLooking(directionRightOfPlayer)
                return"""

            if self.directionOfLooking == directionOfClosestWall:
                if distanceOfNearestWall >= self.speed:
                    # Player is already going to the closest wall and has enough space to go into it. Slow down to stall
                    self.speedDown()
                    return
                else:
                    # player is turned into the closes wall, but does not have enough space to go near it. Player has to
                    # turn in another direction
                    setOfDirections.remove(directionOfClosestWall)
                    self.turnDirectionOfLooking(random.choices(setOfDirections)[0])
                    return
            else:
                if distanceOfNearestWall >= self.speed:
                    # player is not turned to the closest wall, and has enough space to come closer to it without
                    # hitting it so he turns into it
                    self.turnDirectionOfLooking(directionOfClosestWall)
                    return
                else:
                    # player is not turned to the closest wall, but does not have enough space to to turn into it, slow
                    # down to stall and prepare for turning into wall
                    self.speedDown()
                    return

        self.fallBackPlan(playground)

    def findFurthestField(self, playground, speed):
        """Fills out a coordinate system, to tell how far the player can move"""
        logger.disabled = True
        currentPlayer = playground.players[self.id - 1]

        global newNodes
        currentNodes = [(currentPlayer.x, currentPlayer.y)]
        newNodes = []
        tempCS = copy.deepcopy(playground.coordinateSystem)
        count = 10
        turn = playground.getTurn()

        # So lange zu prüfende Knoten verfügbar sind
        while currentNodes:

            # Iteriere über alle anliegenden Knoten
            while currentNodes:
                x = currentNodes[0][0]
                y = currentNodes[0][1]
                logger.debug("CurrentNodes Entry: [" + str(x) + ", " + str(y) + "]")
                currentPlayer.checkAllNodesSurround(tempCS, x, y, count, turn, speed)
                currentNodes.remove(currentNodes[0])

            # Füge neu entdeckte Knoten hinzu nachdem alle aktuellen Knoten geprüft wurden
            while newNodes:
                currentNodes.append(newNodes[0])
                logger.debug(" -- " + str(newNodes[0]) + " -> currentNodes")
                newNodes.remove(newNodes[0])

            count += 1

            if turn < 6:
                turn += 1
            else:
                turn = 1

            logger.debug("---------------")
            for c in tempCS:
                logger.debug(c)

        logger.debug("---------------")
        for c in tempCS:
            logger.debug(c)

        # Maximalen Wert im Koordinatensystem suchen und zurück geben
        maxval = np.amax(tempCS)
        if maxval >= 10:
            for (i, row) in enumerate(tempCS):
                for (j, value) in enumerate(row):
                    if value == maxval:
                        maxvalX = j
                        maxvalY = i
                        if (maxvalX % speed != currentPlayer.x % speed) or (maxvalY % speed != currentPlayer.y % speed):
                            logger.debug("Maximal entfernte gegebenen Koordinate ist NICHT erreichbar!")
                        else:
                            logger.debug(
                                "Max Val (" + str(maxval) + ") at [" + str(maxvalX) + ", " + str(maxvalY) + "]")
                            return maxval, maxvalX, maxvalY, tempCS
            maxval -= 1
            for (i, row) in enumerate(tempCS):
                for (j, value) in enumerate(row):
                    if value == maxval:
                        maxvalX = j
                        maxvalY = i
                        if (maxvalX % speed != currentPlayer.x % speed) or (maxvalY % speed != currentPlayer.y % speed):
                            logger.debug("Maximal entfernte gegebenen Koordinate ist NICHT erreichbar!")
                        else:
                            logger.debug(
                                "Max Val (" + str(maxval) + ") at [" + str(maxvalX) + ", " + str(maxvalY) + "]")
                            return maxval, maxvalX, maxvalY, tempCS

        logger.debug("[" + str(currentPlayer.id) + "]: Konnte keinen Punkt finden.")
        for c in tempCS:
            logger.debug("")
            for d in c:
                if 10 > d >= 0:
                    logger.debug(" " + str(d) + ", ", end='')
                else:
                    logger.debug(str(d) + ", ", end='')
        logger.debug("")
        return 0, 0, 0, tempCS

    def checkAllNodesSurround(self, tempCS, x, y, count, turn, speed):
        """Checks all surrounding nodes of a given node"""
        # up
        self.checkUp(tempCS, x, y, count, turn, speed)
        # right
        self.checkRight(tempCS, x, y, count, turn, speed)
        # left
        self.checkLeft(tempCS, x, y, count, turn, speed)
        # down
        self.checkDown(tempCS, x, y, count, turn, speed)

    def checkRight(self, tempCS, currentPosX, currentPosY, count, turn, speed):
        """Checks the right node"""
        if self.checkPos(tempCS, currentPosX + speed, currentPosY, -1, False, False):

            for i in range(speed):
                checkX = currentPosX + (i + 1)
                checkY = currentPosY
                if turn == 6 and (speed - 2) < (i + 1) < speed:
                    jump = True
                else:
                    jump = False
                if speed < 3:
                    jump = False

                add = (i + 1) == speed
                if not self.checkPos(tempCS, checkX, checkY, count, jump, add):
                    break

    def checkUp(self, tempCS, currentPosX, currentPosY, count, turn, speed):
        """Checks the upper node"""
        if self.checkPos(tempCS, currentPosX, currentPosY - speed, -1, False, False):

            for i in range(speed):
                checkX = currentPosX
                checkY = currentPosY - (i + 1)
                if turn == 6 and (speed - 2) < (i + 1) < speed:
                    jump = True
                else:
                    jump = False
                if speed < 3:
                    jump = False

                add = (i + 1) == speed
                if not self.checkPos(tempCS, checkX, checkY, count, jump, add):
                    break

    def checkDown(self, tempCS, currentPosX, currentPosY, count, turn, speed):
        """Checks the node below"""
        if self.checkPos(tempCS, currentPosX, currentPosY + speed, -1, False, False):

            for i in range(speed):
                checkX = currentPosX
                checkY = currentPosY + (i + 1)
                if turn == 6 and (speed - 2) < (i + 1) < speed:
                    jump = True
                else:
                    jump = False
                if speed < 3:
                    jump = False

                add = (i + 1) == speed
                if not self.checkPos(tempCS, checkX, checkY, count, jump, add):
                    break

    def checkLeft(self, tempCS, currentPosX, currentPosY, count, turn, speed):
        """Checks the left node"""
        if self.checkPos(tempCS, currentPosX - speed, currentPosY, -1, False, False):

            for i in range(speed):
                checkX = currentPosX - (i + 1)
                checkY = currentPosY
                if turn == 6 and (speed - 2) < (i + 1) < speed:
                    jump = True
                else:
                    jump = False
                if speed < 3:
                    jump = False

                add = (i + 1) == speed
                if not self.checkPos(tempCS, checkX, checkY, count, jump, add):
                    break

    def checkPos(self, tempCS, checkX, checkY, count, jump, add):
        """Checks if the given node is free or occupied"""
        if 0 <= checkX < len(tempCS[0]) and 0 <= checkY < len(tempCS):
            if tempCS[checkY][checkX] == 0 or (jump and tempCS[checkY][checkX] < 10):
                if count != -1:  # dont update temp coordinate system if -1 is given
                    tempCS[checkY][checkX] = count
                # logger.debug("New Node Entry: [" + str(checkX) + ", " + str(checkY) + "]")
                if add:
                    newNodes.append((checkX, checkY))
                return True
            else:
                if tempCS[checkY][checkX] < 10:
                    tempCS[checkY][checkX] = -1
                    return False

    def moveToFurthestField(self, playground, maxvalX, maxvalY):
        logger.disabled = True

        if not self.isCoordinateFree(maxvalX, maxvalY, playground):
            logger.debug("Maximal entfernte gegebenen Koordinate ist bereits belegt!")
            return False
        if (maxvalX % self.speed != self.x % self.speed) or (maxvalY % self.speed != self.y % self.speed):
            logger.debug("Maximal entfernte gegebenen Koordinate ist NICHT erreichbar!")
            return False

        finder = AStar(playground.coordinateSystem, self.x, self.y, self.speed, playground.getTurn())
        self.path = finder.solve((maxvalX, maxvalY))

        if self.path is not None and len(self.path) > 0:
            logger.debug("Neuer Pfad:" + str(self.path))
            # self.printMatrix(tempCS)
        else:
            logger.debug(
                "Nix Pfad gefunden :/ von " + str(self.x) + ":" + str(self.y) + " nach " + str(maxvalX) + ":" + str(
                    maxvalY))
            return False

        firstPathX = self.path[1][0]
        firstPathY = self.path[1][1]

        logger.debug(
            "I'm at [" + str(self.x) + ", " + str(self.y) + "] ant want to go to [" + str(firstPathX) + ", " + str(
                firstPathY) + "]")

        if firstPathX > self.x:
            self.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
            logger.debug("Turn right")
        elif firstPathX < self.x:
            self.turnDirectionOfLooking(DirectionOfLooking.LEFT)
            logger.debug("Turn left")
        elif firstPathY > self.y:
            self.turnDirectionOfLooking(DirectionOfLooking.DOWN)
            logger.debug("Turn down")
        elif firstPathY < self.y:
            self.turnDirectionOfLooking(DirectionOfLooking.UP)
            logger.debug("Turn up")

        return True

    def fallBackPlan(self, playground):

        # Prüfe wie viele Blöcke in jeder Richtung frei sind
        freeBlocks = [playground.countBlocksInStraightLine(self, DirectionOfLooking.UP),
                      playground.countBlocksInStraightLine(self, DirectionOfLooking.RIGHT),
                      playground.countBlocksInStraightLine(self, DirectionOfLooking.DOWN),
                      playground.countBlocksInStraightLine(self, DirectionOfLooking.LEFT)]

        # Ändere Kurs, zur Richtung wo am meisten Blöcke frei sind
        if self.speed > 1 and max(freeBlocks) < self.speed:
            logger.debug("[" + str(self.id) + "] I slow down")
            self.speedDown()
        elif freeBlocks.index(max(freeBlocks)) == 0:  # UP
            logger.debug("[" + str(self.id) + "] I try to turn Up")
            self.turnDirectionOfLooking(DirectionOfLooking.UP)
        # try right
        elif freeBlocks.index(max(freeBlocks)) == 1:  # RIGHT
            logger.debug("[" + str(self.id) + "] I try to turn Right")
            self.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
        # try down
        elif freeBlocks.index(max(freeBlocks)) == 2:  # DOWN
            logger.debug("[" + str(self.id) + "] I try to turn Down")
            self.turnDirectionOfLooking(DirectionOfLooking.DOWN)
        # try left
        elif freeBlocks.index(max(freeBlocks)) == 3:  # LEFT
            logger.debug("[" + str(self.id) + "] I try to turn Left")
            self.turnDirectionOfLooking(DirectionOfLooking.LEFT)
