import copy
import inspect
import logging
import sys

import numpy as np

from game.Playground import Playground
from game.player import FreePlaceFinder
from game.player.DirectionOfLooking import DirectionOfLooking
from game.player.Pathfinding import AStar

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()


def checkIfCoordinateIsInCoordinateSystem(givenX, givenY, coordinateSystem):
    """
    Checks if a specific coordinate is withing the playground/coordinatesystem
    :param givenX: x coordinate
    :param givenY: y coordinate
    :param coordinateSystem: coordinate system to check
    :return: if coordinate is withing the coordinatesystem
    """
    return (
            len(coordinateSystem) > givenY >= 0
            and len(coordinateSystem[0]) > givenX >= 0
    )


def printMatrix(matrix):
    """
    Prints the matrix of a map (used during bugfixing)
    For example: freePlaceMap or moveMap
    :param matrix: matrix/map to show
    """
    for y in matrix:
        line = "".join(
            ((str(x) if len(str(x)) == 2 else "0" + str(x)) + " ") for x in y
        )

        logger.info(line)


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
        self.turnSetFrom = "unset"
        self.followPath = False
        self.nextTurn = None

    def isCoordinateFree(self, x, y, playground):
        """
        Checks if a specific coordinate is not occupied by a wall
        :param x: x coordinate
        :param y: y coordinate
        :param playground: playground of the game
        :return: boolean if coordinat is free
        """
        return playground.coordinateSystem[y][x] == 0

    def turnDirectionOfLooking(self, directionOfLooking: DirectionOfLooking):
        """
        Turns current direction to given direction if possible
        :param directionOfLooking: direction to change to
        """
        if directionOfLooking.value == self.directionOfLooking.value * -1:
            logging.info(
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
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            if "simulate" not in calframe[1][3]:
                self.turnSetFrom = calframe[1][3] + " Line: " + str(calframe[1].lineno)

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

        # Check input Parameters
        if directionOfLooking is not None and speedChange != 0:
            logger.info("Invalid Parameters")
            return None
        currentPlayground = copy.deepcopy(playground)

        # Turn our player to the choosen direction
        if speedChange != 0:
            if speedChange < 0:
                currentPlayground.players[playerId - 1].speedDown()
            elif speedChange > 0:
                currentPlayground.players[playerId - 1].speedUp()
        elif directionOfLooking is not None:
            currentPlayground.players[playerId - 1].turnDirectionOfLooking(directionOfLooking)

        # Filter nearest Players to avoid irrelevant calculations
        nearestPlayers = []
        ownPlayer = currentPlayground.players[playerId - 1]
        for player in currentPlayground.players:
            if player.id == ownPlayer.id or not player.active:
                continue
            # Check Distance to other Player
            if abs(ownPlayer.x - player.x) + abs(ownPlayer.y - player.y) <= ownPlayer.speed + player.speed + 1:
                nearestPlayers.append(player)

        # Create Array to store current Turn
        playerTurnCountArray = [0 for _ in nearestPlayers]
        if not playerTurnCountArray:
            currentPlayground.movePlayer()
            freePlaceMap = FreePlaceFinder.generateFreePlaceMap(playground.coordinateSystem)
            freePlaceValues = FreePlaceFinder.getFreePlaceValues(freePlaceMap)

            # Calculate the available space after the choosen turn
            freeBlocks = [FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                             currentPlayground.players[playerId - 1].x +
                                                                             DirectionOfLooking.UP.value[
                                                                                 0] * currentPlayground.players[
                                                                                 playerId - 1].speed,
                                                                             currentPlayground.players[playerId - 1].y +
                                                                             DirectionOfLooking.UP.value[
                                                                                 1] * currentPlayground.players[
                                                                                 playerId - 1].speed, freePlaceValues),
                          FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                             currentPlayground.players[playerId - 1].x +
                                                                             DirectionOfLooking.RIGHT.value[
                                                                                 0] * currentPlayground.players[
                                                                                 playerId - 1].speed,
                                                                             currentPlayground.players[playerId - 1].y +
                                                                             DirectionOfLooking.RIGHT.value[
                                                                                 1] * currentPlayground.players[
                                                                                 playerId - 1].speed, freePlaceValues),
                          FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                             currentPlayground.players[playerId - 1].x +
                                                                             DirectionOfLooking.DOWN.value[
                                                                                 0] * currentPlayground.players[
                                                                                 playerId - 1].speed,
                                                                             currentPlayground.players[playerId - 1].y +
                                                                             DirectionOfLooking.DOWN.value[
                                                                                 1] * currentPlayground.players[
                                                                                 playerId - 1].speed, freePlaceValues),
                          FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                             currentPlayground.players[playerId - 1].x +
                                                                             DirectionOfLooking.LEFT.value[
                                                                                 0] * currentPlayground.players[
                                                                                 playerId - 1].speed,
                                                                             currentPlayground.players[playerId - 1].y +
                                                                             DirectionOfLooking.LEFT.value[
                                                                                 1] * currentPlayground.players[
                                                                                 playerId - 1].speed, freePlaceValues)]

            return currentPlayground.players[playerId - 1].active and max(freeBlocks) > 0

        # Iterate over all possible combinations of enemy turns
        IterationsDone = False
        # Alive iterations
        alive = 0
        # Iteration count
        iterations = 0
        while not IterationsDone:
            nextPlayground = copy.deepcopy(currentPlayground)
            # Iterate over all possible playerturns
            for nearestPlayerIndex in range(len(nearestPlayers)):
                playgroundPlayer = nextPlayground.players[nearestPlayers[nearestPlayerIndex].id - 1]
                if playgroundPlayer is not None:
                    """Turns:
                    0: Go Left
                    1: Go Right
                    2: Change Nothing
                    3: Slow Down
                    4: Speed Up
                    """
                    # Change player direction based on the number in array
                    if playerTurnCountArray[nearestPlayerIndex] == 0:
                        if playgroundPlayer.directionOfLooking == DirectionOfLooking.UP:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.LEFT)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.DOWN:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.LEFT:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.DOWN)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.RIGHT:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.UP)
                    elif playerTurnCountArray[nearestPlayerIndex] == 1:
                        if playgroundPlayer.directionOfLooking == DirectionOfLooking.UP:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.DOWN:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.LEFT)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.LEFT:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.UP)
                        elif playgroundPlayer.directionOfLooking == DirectionOfLooking.RIGHT:
                            playgroundPlayer.turnDirectionOfLooking(DirectionOfLooking.DOWN)
                    elif playerTurnCountArray[nearestPlayerIndex] == 3:
                        playgroundPlayer.speedDown()
                    elif playerTurnCountArray[nearestPlayerIndex] == 4:
                        playgroundPlayer.speedUp()

            # Move every player and check if own player is alive and next turn has possible Moves
            nextPlayground.movePlayer()
            # Check if there is space in the Next Turn
            freeBlocks = [
                nextPlayground.countBlocksInStraightLine(nextPlayground.players[playerId - 1], DirectionOfLooking.UP),
                nextPlayground.countBlocksInStraightLine(nextPlayground.players[playerId - 1],
                                                         DirectionOfLooking.RIGHT),
                nextPlayground.countBlocksInStraightLine(nextPlayground.players[playerId - 1], DirectionOfLooking.DOWN),
                nextPlayground.countBlocksInStraightLine(nextPlayground.players[playerId - 1], DirectionOfLooking.LEFT)]

            if nextPlayground.players[playerId - 1].active and max(freeBlocks) / nextPlayground.players[
                playerId - 1].speed > 0.5:
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
        # Calculate the chance to be alive. Must be over 80% to count as a Good Choice
        return (alive / iterations) > 0.8

    def speedUp(self):
        """
        Accelerate one speed
        """
        if self.speed < 10:
            self.choosenTurn = "speed_up"
            self.speed += 1
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            if "simulate" not in calframe[1][3]:
                self.turnSetFrom = calframe[1][3] + " Line: " + str(calframe[1].lineno)

    def speedDown(self):
        """
        Decelerates one speed
        """
        if self.speed > 1:
            self.choosenTurn = "slow_down"
            self.speed -= 1
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            if "simulate" not in calframe[1][3]:
                self.turnSetFrom = calframe[1][3] + " Line: " + str(calframe[1].lineno)

    def updatePlayer(self, id: int, x: int, y: int, directionOfLooking: DirectionOfLooking, active: bool, speed: int):
        """
        Updates player variables
        :param id: player id
        :param x: x coordinate
        :param y: y coordinate
        :param directionOfLooking: direction the player looks
        :param active: if player is still alive
        :param speed: speed of the player
        """
        if id != self.id:
            logging.info('No matching ID of player')
        else:
            self.x = x
            self.y = y
            self.directionOfLooking = directionOfLooking
            self.active = active
            self.speed = speed

    def die(self):
        """
        Player cant move any further so it dies
        """
        self.speed = 0
        self.path = []
        self.active = False

    def doesSpeedUpMakeSense(self, playground, speedchange, changePlayer=True):
        """
        Check if the player can reach another area through jumping with a speed change
        :param playground: playground of the game
        :param speedchange: amound to add to the current speed
        :param changePlayer: if player should execute speed up right now if it makes sense
        :return: bool whether it makes sense or not
        """
        if speedchange <= 0:
            return False
        nextPlayground = copy.deepcopy(playground)

        if nextPlayground.players[self.id - 1].speed + speedchange < 3:
            return False
        # Create new playground and move all players, to look how the new playground would look like
        alive = 0

        # Create FreePlaceMap
        freeMap = FreePlaceFinder.generateFreePlaceMap(nextPlayground.coordinateSystem)
        freeMapValues = FreePlaceFinder.getFreePlaceValues(freeMap)

        # Simulate the choosen count speedUps one after another
        for _ in range(speedchange):
            alive = (alive + 1) if self.simulateNextTurn(nextPlayground, self.id, None, 1) else alive
            nextPlayground.players[self.id - 1].speedUp()
            nextPlayground.movePlayer()
            nextPlayground.addTurn()

        # Check if player is still alive in new playground
        if alive is speedchange:
            maxval, maxvalX, maxvalY, tempCS = self.findFurthestField(
                nextPlayground, nextPlayground.players[self.id - 1].speed)

            # Iterate over all bigger areas and check if they are reachable
            ownFreePlaceIndex = FreePlaceFinder.getRelativeFreePlaceIndexForCoordinate(freeMap, nextPlayground.players[
                self.id - 1].x, nextPlayground.players[self.id - 1].y)

            moveMap = FreePlaceFinder.convertFindFurthestFieldMapToFreePlaceFormat(tempCS)
            for freePlaceAreaCount in range(len(freeMapValues)):
                maxFreePlaceIndex = FreePlaceFinder.getBiggestArea(freeMapValues, freePlaceAreaCount + 1)
                # If we are currently in max Area -> Skip
                if ownFreePlaceIndex == maxFreePlaceIndex:
                    break

                # Calculate the nearest Coordinate in the Bigger Area if exist
                nearestCoordinateOnFurthestFieldMap = FreePlaceFinder.findNearestCoordinateOnFurthestFieldMap(freeMap,
                                                                                                              moveMap,
                                                                                                              maxFreePlaceIndex + 1,
                                                                                                              nextPlayground.players[
                                                                                                                  self.id - 1].speed,
                                                                                                              nextPlayground.players[
                                                                                                                  self.id - 1].x,
                                                                                                              nextPlayground.players[
                                                                                                                  self.id - 1].y)

                if nearestCoordinateOnFurthestFieldMap is not None:
                    # Calculate new path
                    finder = AStar(nextPlayground.coordinateSystem, nextPlayground.players[self.id - 1].x,
                                   nextPlayground.players[self.id - 1].y, nextPlayground.players[self.id - 1].speed,
                                   nextPlayground.getTurn())
                    self.path = finder.solve(nearestCoordinateOnFurthestFieldMap)

                    if self.path is not None and maxFreePlaceIndex is not None and ownFreePlaceIndex is not None and (
                            freeMapValues[maxFreePlaceIndex] / freeMapValues[
                        ownFreePlaceIndex]) > 1.3:

                        # Check if still alive after next Turn in new Area
                        nextAreaPlayground = copy.deepcopy(nextPlayground)
                        nextAreaPlayground.players[self.id - 1].x = nearestCoordinateOnFurthestFieldMap[0]
                        nextAreaPlayground.players[self.id - 1].y = nearestCoordinateOnFurthestFieldMap[1]

                        # Set the new Direction based on last Coordinate on path to new Area
                        if nearestCoordinateOnFurthestFieldMap[0] < self.path[len(self.path) - 2][0]:
                            nextAreaPlayground.players[self.id - 1].directionOfLooking = DirectionOfLooking.LEFT
                        elif nearestCoordinateOnFurthestFieldMap[0] > self.path[len(self.path) - 2][0]:
                            nextAreaPlayground.players[self.id - 1].directionOfLooking = DirectionOfLooking.RIGHT
                        elif nearestCoordinateOnFurthestFieldMap[1] < self.path[len(self.path) - 2][1]:
                            nextAreaPlayground.players[self.id - 1].directionOfLooking = DirectionOfLooking.UP
                        elif nearestCoordinateOnFurthestFieldMap[1] > self.path[len(self.path) - 2][1]:
                            nextAreaPlayground.players[self.id - 1].directionOfLooking = DirectionOfLooking.DOWN

                        # Simulates if there is a possible turn in the new Area
                        if self.simulateNextTurn(nextAreaPlayground, self.id,
                                                 nextAreaPlayground.players[self.id - 1].directionOfLooking):
                            if changePlayer:
                                self.speedUp()
                            self.followPath = True
                            # If double jump -> mark next turn as speedUp
                            if speedchange > 1:
                                self.nextTurn = ""
                                for _ in range(speedchange):
                                    self.nextTurn += "speed_up"
                            return True
                        else:
                            self.path = None
                    self.path = None
        return False

    def tryToFollowPath(self, playground):
        """
        Player tries to follow a precalculated path
        While doing so, it checks if a turn will kill the player
        :param playground: playground of the game
        :return: if the path can be followed
        """
        # Check if we're next waypoint still alive
        if self.path is None or len(self.path) == 0:
            return False
        nextCoord = self.path.pop(0)
        while nextCoord[0] == self.x and nextCoord[1] == self.y or (
                abs(nextCoord[0] - self.x) != self.speed and abs(nextCoord[1] - self.y) != self.speed):
            if len(self.path) > 0:
                nextCoord = self.path.pop(0)
            else:
                logger.info("FEHLER")
                return False

        # Calculate the new Path
        finder = AStar(playground.coordinateSystem, playground.players[self.id - 1].x,
                       playground.players[self.id - 1].y, playground.players[self.id - 1].speed,
                       playground.getTurn())
        path = finder.solve(nextCoord)
        if path is not None and len(path) > 0:
            nextDirection = None
            if nextCoord[0] > playground.players[self.id - 1].x:
                nextDirection = DirectionOfLooking.RIGHT
            elif nextCoord[0] < playground.players[self.id - 1].x:
                nextDirection = DirectionOfLooking.LEFT
            elif nextCoord[1] > playground.players[self.id - 1].y:
                nextDirection = DirectionOfLooking.DOWN
            elif nextCoord[1] < playground.players[self.id - 1].y:
                nextDirection = DirectionOfLooking.UP

            # Simulate turn
            if self.simulateNextTurn(playground, self.id, nextDirection):
                self.turnDirectionOfLooking(nextDirection)
                return True
        return False

    def tryToSurvive(self, playground):
        """
        Executes diffrent strategies on diffrent conditions to keep the player alive using the playground as the
        provided playfield
        :param playground: playfield
        :return: none
        """
        # Reset turns to make
        self.choosenTurn = "change_nothing"
        self.turnSetFrom = "unset"

        # Check if the player should make a specific turn to follow a pre-calculated Path
        if self.nextTurn is not None:
            if "speed_up" in self.nextTurn:

                if self.simulateNextTurn(playground, self.id, None, 1):
                    self.speedUp()
                    self.nextTurn = self.nextTurn.replace("speed_up", "", 1)
                    if len(self.nextTurn) == 0:
                        self.nextTurn = None
                    return
                else:
                    logger.info("[" + str(self.id) + "]: Cancled speedUp")
                    self.nextTurn = None

        if self.followPath and self.path is not None and len(self.path) > 0:
            if self.tryToFollowPath(playground):
                return
        self.followPath = False
        self.path = None

        # Find all possible moves with current speed
        _, _, _, tempCS = self.findFurthestField(playground, self.speed)

        # Create freeMap
        freeMap = FreePlaceFinder.generateFreePlaceMap(playground.coordinateSystem)
        freeMapValues = FreePlaceFinder.getFreePlaceValues(freeMap)
        ownFreePlaceIndex = FreePlaceFinder.getRelativeFreePlaceIndexForCoordinate(freeMap, self.x, self.y)
        maxFreePlaceIndex = FreePlaceFinder.getBiggestArea(freeMapValues)

        # If there where no errors creating the FreeplaceMap
        if freeMapValues is not None and ownFreePlaceIndex is not None and maxFreePlaceIndex is not None:
            # If we're allready in biggest Area
            if freeMapValues[ownFreePlaceIndex] == freeMapValues[maxFreePlaceIndex]:
                # Check if some user is direct near us in the same direction and could so possibly cut off our way to success
                shouldEscape = False
                for player in playground.players:
                    if player.id != self.id and player.active and ((abs(player.x - self.x) <= 2 and abs(
                            player.y - self.y) <= 4) or (abs(player.y - self.y) <= 2 and abs(
                        player.x - self.x) <= 4)) and player.directionOfLooking == self.directionOfLooking and (
                            self.speed <= player.speed + 2 < 10):
                        shouldEscape = True
                if shouldEscape and self.simulateNextTurn(playground, self.id, None, 1):
                    self.speedUp()
                    return
                # We're alone...so just ride along side the wall
                self.rideAlongSideWall(playground)
                return
            else:
                logger.info("Not in Biggest Area!")
                moveMap = FreePlaceFinder.convertFindFurthestFieldMapToFreePlaceFormat(tempCS)
                # Calc the nearest coordinate in the bigger Area, if exist
                nearestCoordinateOnFurthestFieldMap = FreePlaceFinder.findNearestCoordinateOnFurthestFieldMap(freeMap,
                                                                                                              moveMap,
                                                                                                              maxFreePlaceIndex + 1,
                                                                                                              self.speed,
                                                                                                              self.x,
                                                                                                              self.y)

                if nearestCoordinateOnFurthestFieldMap is not None:
                    if self.moveToFurthestField(playground, nearestCoordinateOnFurthestFieldMap[0],
                                                nearestCoordinateOnFurthestFieldMap[1]):
                        logger.info("  Found way out! Folllowing new path.")
                        return
                else:
                    # If the current speed is slower then the maximum speed
                    if self.speed < 10:
                        # Check if a speedup is able to bring us to one bigger Area
                        for i in range(1, 5):
                            if ((self.speed == 1 and i > 1) or self.speed != 1) and self.doesSpeedUpMakeSense(
                                    playground, i):
                                logger.info("Found way to Area with " + str(
                                    freeMapValues[maxFreePlaceIndex] - freeMapValues[
                                        ownFreePlaceIndex]) + " more free Pixels!")
                                return

                        # Check if a specific turn opens the possibility to jump into biggest field
                        possibleTurns = []
                        if self.directionOfLooking == DirectionOfLooking.UP:
                            if DirectionOfLooking.UP not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                    self.id,
                                                                                                    DirectionOfLooking.UP):
                                possibleTurns.append(DirectionOfLooking.UP)
                            if DirectionOfLooking.LEFT not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                      self.id,
                                                                                                      DirectionOfLooking.LEFT):
                                possibleTurns.append(DirectionOfLooking.LEFT)
                            if DirectionOfLooking.RIGHT not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                       self.id,
                                                                                                       DirectionOfLooking.RIGHT):
                                possibleTurns.append(DirectionOfLooking.RIGHT)
                        elif self.directionOfLooking == DirectionOfLooking.LEFT:
                            if DirectionOfLooking.LEFT not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                      self.id,
                                                                                                      DirectionOfLooking.LEFT):
                                possibleTurns.append(DirectionOfLooking.LEFT)
                            if DirectionOfLooking.UP not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                    self.id,
                                                                                                    DirectionOfLooking.UP):
                                possibleTurns.append(DirectionOfLooking.UP)
                            if DirectionOfLooking.DOWN not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                      self.id,
                                                                                                      DirectionOfLooking.DOWN):
                                possibleTurns.append(DirectionOfLooking.DOWN)
                        elif self.directionOfLooking == DirectionOfLooking.RIGHT:
                            if DirectionOfLooking.RIGHT not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                       self.id,
                                                                                                       DirectionOfLooking.RIGHT):
                                possibleTurns.append(DirectionOfLooking.RIGHT)
                            if DirectionOfLooking.UP not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                    self.id,
                                                                                                    DirectionOfLooking.UP):
                                possibleTurns.append(DirectionOfLooking.UP)
                            if DirectionOfLooking.DOWN not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                      self.id,
                                                                                                      DirectionOfLooking.DOWN):
                                possibleTurns.append(DirectionOfLooking.DOWN)
                        elif self.directionOfLooking == DirectionOfLooking.DOWN:
                            if DirectionOfLooking.DOWN not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                      self.id,
                                                                                                      DirectionOfLooking.DOWN):
                                possibleTurns.append(DirectionOfLooking.DOWN)
                            if DirectionOfLooking.LEFT not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                      self.id,
                                                                                                      DirectionOfLooking.LEFT):
                                possibleTurns.append(DirectionOfLooking.LEFT)
                            if DirectionOfLooking.RIGHT not in possibleTurns and self.simulateNextTurn(playground,
                                                                                                       self.id,
                                                                                                       DirectionOfLooking.RIGHT):
                                possibleTurns.append(DirectionOfLooking.RIGHT)

                        for dir in possibleTurns:
                            nextPlayground = copy.deepcopy(playground)
                            nextPlayground.players[self.id - 1].directionOfLooking = dir
                            nextPlayground.movePlayer()
                            nextPlayground.addTurn()
                            for i in range(1, 5):
                                if ((nextPlayground.players[self.id - 1].speed == 1 and i > 1) or
                                    nextPlayground.players[self.id - 1].speed != 1) and self.doesSpeedUpMakeSense(
                                    nextPlayground, i, False):
                                    self.turnDirectionOfLooking(dir)
                                    return

        if len(freeMapValues) > 1:
            logger.info("  cant get out!")
        self.rideAlongSideWall(playground)
        return

    def rideAlongSideWall(self, playground):
        """
        Finds the nearest Wall and tries to ride alongside it while reducing the players speed to 1. The resulting
        Pattern results into a spiral. This Method ignores one cell wide indents in a wall.
        ATTENTION: This method only does one action per call. E.g. This Method only slows down the player or turns him
        according to the aforementioned plan. This means this method has to be called multiple rounds in a row to
        accomplish said plan.
        :param playground: game playground
        :return: none
        """
        # 1. Find nearest Wall
        # 2. Turn to nearest wall
        # 3. Try to reduce Speed
        # 4. Turn clockwise in cul de sac
        # 5. Scan if next cell is a odd shaped cul de sac or an one wide indent
        # 6. ride alongside wall
        # 7. If next wallpiece is straight, reduce speed
        # 8. Go to 4.

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

        directionOfLookinXY = self.x + self.directionOfLooking.value[0] * self.speed, self.y + \
                              self.directionOfLooking.value[1] * self.speed
        lookDirectionAlongsideWallLeftXY = self.x + lookDirectionAlongSideWallLeft.value[0], self.y + \
                                           lookDirectionAlongSideWallLeft.value[1]
        lookDirectionAlongSideWallRightXY = self.x + lookDirectionAlongSideWallRight.value[0], self.y + \
                                            lookDirectionAlongSideWallRight.value[1]

        if distanceOfNearestWall == 0:
            if (
                    playground.countBlocksInStraightLine(self, self.directionOfLooking)
                    != 0
            ):
                # the player is adjacent to a wall and not looking at it. Commence plan.
                # if the player would hit a wall, change direction

                if freeBlocks.get(self.directionOfLooking) < self.speed:
                    # not enough space in direction of player. change direction
                    oppositeDirectionOfPlayerLookingDirection = setOfDirections[
                        (setOfDirections.index(self.directionOfLooking) + 1) % 4]
                    if self.simulateNextTurn(playground, self.id, oppositeDirectionOfPlayerLookingDirection):
                        self.turnDirectionOfLooking(oppositeDirectionOfPlayerLookingDirection)
                else:
                    # if the player would move into a one wide gap, change direction

                    # go one field forward look left and right
                    currentX, currentY = self.x, self.y
                    currentX += self.directionOfLooking.value[0] * self.speed
                    currentY += self.directionOfLooking.value[1] * self.speed

                    isGapOneCellWide = 0
                    for direction in freeBlocks:
                        tempX = currentX + direction.value[0] * self.speed
                        tempY = currentY + direction.value[1] * self.speed
                        # check if coordinate is within system
                        if checkIfCoordinateIsInCoordinateSystem(tempX, tempY, playground.coordinateSystem):
                            if (playground.coordinateSystem[tempY][tempX] != 0):
                                isGapOneCellWide += 1
                        else:
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
                            elif FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                    lookDirectionAlongsideWallLeftXY[0],
                                                                                    lookDirectionAlongsideWallLeftXY[1],
                                                                                    freePlaceValues) \
                                    >= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                          lookDirectionAlongSideWallRightXY[
                                                                                              0],
                                                                                          lookDirectionAlongSideWallRightXY[
                                                                                              1], freePlaceValues):
                                if self.simulateNextTurn(playground, self.id, lookDirectionAlongSideWallLeft):
                                    self.turnDirectionOfLooking(lookDirectionAlongSideWallLeft)
                                    return
                            else:
                                if self.simulateNextTurn(playground, self.id, lookDirectionAlongSideWallRight):
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
                            if self.simulateNextTurn(playground, self.id, lookDirectionAlongSideWallLeft):
                                self.turnDirectionOfLooking(lookDirectionAlongSideWallLeft)
                                return
                        else:
                            if self.simulateNextTurn(playground, self.id, lookDirectionAlongSideWallRight):
                                self.turnDirectionOfLooking(lookDirectionAlongSideWallRight)
                                return
                    else:
                        if self.simulateNextTurn(playground, self.id, None, -1):
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
                    if self.simulateNextTurn(playground, self.id, lookDirectionAlongSideWallLeft):
                        self.turnDirectionOfLooking(lookDirectionAlongSideWallLeft)
                        return
                else:
                    if self.simulateNextTurn(playground, self.id, lookDirectionAlongSideWallRight):
                        self.turnDirectionOfLooking(lookDirectionAlongSideWallRight)
                        return
        else:
            # check if a wall is behind the player, if so, go there
            # get direction of wall behind player
            setOfDirectionsWithDiagonals = [DirectionOfLooking.UP, DirectionOfLooking.UPRIGHT, DirectionOfLooking.RIGHT,
                                            DirectionOfLooking.DOWNRIGHT, DirectionOfLooking.DOWN,
                                            DirectionOfLooking.DOWNLEFT, DirectionOfLooking.LEFT,
                                            DirectionOfLooking.UPLEFT]

            directionBehindPlayerLeft = setOfDirectionsWithDiagonals[
                (setOfDirectionsWithDiagonals.index(self.directionOfLooking) + 5) % 8]
            directionBehindPlayerRight = setOfDirectionsWithDiagonals[
                (setOfDirectionsWithDiagonals.index(self.directionOfLooking) + 3) % 8]

            # check if there is a wall behind the player on the left
            # and if left is more space than right

            directionLeftOfPlayer = setOfDirectionsWithDiagonals[
                (setOfDirectionsWithDiagonals.index(self.directionOfLooking) + 6) % 8]
            directionRightOfPlayer = setOfDirectionsWithDiagonals[
                (setOfDirectionsWithDiagonals.index(self.directionOfLooking) + 2) % 8]
            leftXYOfPlayer = self.x + directionLeftOfPlayer.value[0] * self.speed, self.y + directionLeftOfPlayer.value[
                1] * self.speed
            rightXYOfPlayer = self.x + directionRightOfPlayer.value[0] * self.speed, self.y + \
                              directionRightOfPlayer.value[1] * self.speed

            if checkIfCoordinateIsInCoordinateSystem(self.x + directionBehindPlayerLeft.value[0] * self.speed,
                                                     self.y + directionBehindPlayerLeft.value[1] * self.speed,
                                                     playground.coordinateSystem) and \
                    playground.coordinateSystem[self.y + directionBehindPlayerLeft.value[1] * self.speed][
                        self.x + directionBehindPlayerLeft.value[0] * self.speed] != 0 \
                    and FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, leftXYOfPlayer[0],
                                                                           leftXYOfPlayer[1], freePlaceValues) \
                    >= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, rightXYOfPlayer[0],
                                                                          rightXYOfPlayer[1], freePlaceValues):

                if self.simulateNextTurn(playground, self.id, directionLeftOfPlayer):
                    self.turnDirectionOfLooking(directionLeftOfPlayer)
                    return

            # check if there is a wall right behind the player, and there is more space than on the left
            elif checkIfCoordinateIsInCoordinateSystem(self.x + directionBehindPlayerRight.value[0] * self.speed,
                                                       self.y + directionBehindPlayerRight.value[1] * self.speed,
                                                       playground.coordinateSystem) and \
                    playground.coordinateSystem[self.y + directionBehindPlayerRight.value[1] * self.speed][
                        self.x + directionBehindPlayerRight.value[0] * self.speed] != 0 \
                    and FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, leftXYOfPlayer[0],
                                                                           leftXYOfPlayer[1], freePlaceValues) \
                    <= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap, rightXYOfPlayer[0],
                                                                          rightXYOfPlayer[1], freePlaceValues):
                if self.simulateNextTurn(playground, self.id, directionRightOfPlayer):
                    self.turnDirectionOfLooking(directionRightOfPlayer)
                    return

            if self.directionOfLooking == directionOfClosestWall:
                if distanceOfNearestWall >= self.speed:
                    # Player is already going to the closest wall and has enough space to go into it. Slow down to stall
                    self.speedDown()
                    return
                else:
                    # player is turned into the closes wall, but does not have enough space to go near it. Player has to
                    # turn in another direction
                    setOfDirections.remove(directionOfClosestWall)
                    for dir in setOfDirections:
                        if self.simulateNextTurn(playground, self.id,
                                                 dir) and FreePlaceFinder.getAmountOfFreePlacesForCoordinate(
                            freePlaceMap, self.x + dir.value[0] * self.speed, self.y + dir.value[1] * self.speed,
                            freePlaceValues) >= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                                   self.x +
                                                                                                   self.directionOfLooking.value[
                                                                                                       0] * self.speed,
                                                                                                   self.y +
                                                                                                   self.directionOfLooking.value[
                                                                                                       1] * self.speed,
                                                                                                   freePlaceValues):
                            self.turnDirectionOfLooking(dir)
                            return
                return
            else:
                if distanceOfNearestWall >= self.speed:
                    # player is not turned to the closest wall, and has enough space to come closer to it without
                    # hitting it so he turns into it
                    for dir in setOfDirections:
                        if self.simulateNextTurn(playground, self.id,
                                                 dir) and FreePlaceFinder.getAmountOfFreePlacesForCoordinate(
                            freePlaceMap, self.x + dir.value[0] * self.speed, self.y + dir.value[1] * self.speed,
                            freePlaceValues) >= FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                                                   self.x +
                                                                                                   self.directionOfLooking.value[
                                                                                                       0] * self.speed,
                                                                                                   self.y +
                                                                                                   self.directionOfLooking.value[
                                                                                                       1] * self.speed,
                                                                                                   freePlaceValues):
                            self.turnDirectionOfLooking(dir)
                            return
                else:
                    # player is not turned to the closest wall, but does not have enough space to to turn into it, slow
                    # down to stall and prepare for turning into wall
                    if self.simulateNextTurn(playground, self.id, None, -1):
                        self.speedDown()
                        return

        self.fallBackPlan(playground)

    def findFurthestField(self, playground, speed):
        """
        Fills out a coordinate system, to tell how far the player can move
        :param playground: playfield
        :param speed: current speed
        :return: coordinates and map with possible moves to the furthest coordinate
        """
        currentPlayer = playground.players[self.id - 1]

        global newNodes
        currentNodes = [(currentPlayer.x, currentPlayer.y)]
        newNodes = []
        tempCS = copy.deepcopy(playground.coordinateSystem)
        count = 10
        turn = playground.getTurn()

        # While there are nodes to check
        while currentNodes:

            # Check neighbors
            while currentNodes:
                x = currentNodes[0][0]
                y = currentNodes[0][1]
                currentPlayer.checkAllNodesSurround(tempCS, x, y, count, turn, speed)
                currentNodes.remove(currentNodes[0])

            # Add all new nodes to the array
            while newNodes:
                currentNodes.append(newNodes[0])
                newNodes.remove(newNodes[0])

            count += 1

            if turn < 6:
                turn += 1
            else:
                turn = 1

        # Find max Path an return
        maxval = np.amax(tempCS)
        if maxval >= 10:
            for (i, row) in enumerate(tempCS):
                for (j, value) in enumerate(row):
                    if value == maxval:
                        maxvalX = j
                        maxvalY = i
                        if (
                                maxvalX % speed == currentPlayer.x % speed
                                and maxvalY % speed == currentPlayer.y % speed
                        ):
                            return maxval, maxvalX, maxvalY, tempCS
            maxval -= 1
            for (i, row) in enumerate(tempCS):
                for (j, value) in enumerate(row):
                    if value == maxval:
                        maxvalX = j
                        maxvalY = i
                        if not ((maxvalX % speed != currentPlayer.x % speed) or (
                                maxvalY % speed != currentPlayer.y % speed)):
                            return maxval, maxvalX, maxvalY, tempCS

        return 0, 0, 0, tempCS

    def checkAllNodesSurround(self, tempCS, x, y, count, turn, speed):
        """
        Checks all surrounding nodes of a given node
        :param tempCS: Map with possible moves to furthest field
        :param x: x coordinate
        :param y: y coordinate
        :param count: number of turn to check
        :param turn: current turn
        :param speed: current speed
        """
        # up
        self.checkUp(tempCS, x, y, count, turn, speed)
        # right
        self.checkRight(tempCS, x, y, count, turn, speed)
        # left
        self.checkLeft(tempCS, x, y, count, turn, speed)
        # down
        self.checkDown(tempCS, x, y, count, turn, speed)

    def checkRight(self, tempCS, currentPosX, currentPosY, count, turn, speed):
        """
        Checks the right node
        :param tempCS: Map with possible moves to furthest field
        :param currentPosX: x coordinate
        :param currentPosY: y coordinate
        :param count: number of turn to check
        :param turn: current turn
        :param speed: current speed
        """
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
        """
        Checks the upper node
        :param tempCS: Map with possible moves to furthest field
        :param currentPosX: x coordinate
        :param currentPosY: y coordinate
        :param count: number of turn to check
        :param turn: current turn
        :param speed: current speed
        """
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
        """
        Checks the node bellow
        :param tempCS: Map with possible moves to furthest field
        :param currentPosX: x coordinate
        :param currentPosY: y coordinate
        :param count: number of turn to check
        :param turn: current turn
        :param speed: current speed
        """
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
        """
        Checks the left node
        :param tempCS: Map with possible moves to furthest field
        :param currentPosX: x coordinate
        :param currentPosY: y coordinate
        :param count: number of turn to check
        :param turn: current turn
        :param speed: current speed
        """
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
        """
        Checks if the given node is free or occupied
        :param tempCS: Map with possible moves to furthest field
        :param checkX: x coordinate
        :param checkY: y coordinate
        :param count: number of turn to check
        :param jump: if a jump will be executed
        :param add: if the checked nodes shall be attached and checked in the next iterration
        :return:
        """
        if 0 <= checkX < len(tempCS[0]) and 0 <= checkY < len(tempCS):
            if tempCS[checkY][checkX] == 0 or (jump and tempCS[checkY][checkX] < 10):
                if count != -1:  # dont update temp coordinate system if -1 is given
                    tempCS[checkY][checkX] = count
                if add:
                    newNodes.append((checkX, checkY))
                return True
            else:
                if tempCS[checkY][checkX] < 10:
                    tempCS[checkY][checkX] = -1
                    return False

    def moveToFurthestField(self, playground, maxvalX, maxvalY):
        """
        Moves the player on a calculated path to the defined coordinates using the A* algorithm. If no path is
        found returns false
        :param playground: playfield
        :param maxvalX: x position of the furthest field
        :param maxvalY: y position of the furthest field
        :return: if method was successful
        """

        if not self.isCoordinateFree(maxvalX, maxvalY, playground):
            logger.info("Maximum distant given coordinate is already occupied!")
            return False
        if (maxvalX % self.speed != self.x % self.speed) or (maxvalY % self.speed != self.y % self.speed):
            logger.info("Maximum distant given coordinate is NOT reachable!")
            return False

        finder = AStar(playground.coordinateSystem, self.x, self.y, self.speed, playground.getTurn())
        self.path = finder.solve((maxvalX, maxvalY))

        if self.path is not None and len(self.path) > 0:
            logger.info("New path:" + str(self.path))
            # self.printMatrix(tempCS)
        else:
            logger.info(
                "No path found :/ from " + str(self.x) + ":" + str(self.y) + " to " + str(maxvalX) + ":" + str(
                    maxvalY))
            return False

        firstPathX = self.path[1][0]
        firstPathY = self.path[1][1]

        logger.info(
            "I'm at [" + str(self.x) + ", " + str(self.y) + "] ant want to go to [" + str(firstPathX) + ", " + str(
                firstPathY) + "]")

        if firstPathX > self.x:
            self.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
        elif firstPathX < self.x:
            self.turnDirectionOfLooking(DirectionOfLooking.LEFT)
        elif firstPathY > self.y:
            self.turnDirectionOfLooking(DirectionOfLooking.DOWN)
        elif firstPathY < self.y:
            self.turnDirectionOfLooking(DirectionOfLooking.UP)

        return True

    def fallBackPlan(self, playground):
        """
        Calculates the distance to all walls in the cardinal directions, and turns to the one with the most distance
        :param playground: playfield
        :return: none
        """

        # Create FreePlaceMap
        freePlaceMap = FreePlaceFinder.generateFreePlaceMap(playground.coordinateSystem)
        freePlaceValues = FreePlaceFinder.getFreePlaceValues(freePlaceMap)

        # Check how many free Pixels are left in each direction
        freeBlocks = [FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                         self.x + DirectionOfLooking.UP.value[
                                                                             0] * self.speed,
                                                                         self.y + DirectionOfLooking.UP.value[
                                                                             1] * self.speed, freePlaceValues),
                      FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                         self.x + DirectionOfLooking.RIGHT.value[
                                                                             0] * self.speed,
                                                                         self.y + DirectionOfLooking.RIGHT.value[
                                                                             1] * self.speed, freePlaceValues),
                      FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                         self.x + DirectionOfLooking.DOWN.value[
                                                                             0] * self.speed,
                                                                         self.y + DirectionOfLooking.DOWN.value[
                                                                             1] * self.speed, freePlaceValues),
                      FreePlaceFinder.getAmountOfFreePlacesForCoordinate(freePlaceMap,
                                                                         self.x + DirectionOfLooking.LEFT.value[
                                                                             0] * self.speed,
                                                                         self.y + DirectionOfLooking.LEFT.value[
                                                                             1] * self.speed, freePlaceValues)]

        # Check if we're alive in each direction
        setOfDirections = [self.directionOfLooking, DirectionOfLooking.UP, DirectionOfLooking.RIGHT,
                           DirectionOfLooking.DOWN,
                           DirectionOfLooking.LEFT]

        for dir in setOfDirections:
            if self.simulateNextTurn(playground, self.id, dir):
                self.turnDirectionOfLooking(dir)
                return

        # Turn to the direction with most free space
        if self.speed > 1 and max(freeBlocks) < self.speed:
            logger.info("[" + str(self.id) + "] I slow down")
            self.speedDown()
        elif freeBlocks.index(max(freeBlocks)) == 0:  # UP
            logger.info("[" + str(self.id) + "] I try to turn Up")
            self.turnDirectionOfLooking(DirectionOfLooking.UP)
        # try right
        elif freeBlocks.index(max(freeBlocks)) == 1:  # RIGHT
            logger.info("[" + str(self.id) + "] I try to turn Right")
            self.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
        # try down
        elif freeBlocks.index(max(freeBlocks)) == 2:  # DOWN
            logger.info("[" + str(self.id) + "] I try to turn Down")
            self.turnDirectionOfLooking(DirectionOfLooking.DOWN)
        # try left
        elif freeBlocks.index(max(freeBlocks)) == 3:  # LEFT
            logger.info("[" + str(self.id) + "] I try to turn Left")
            self.turnDirectionOfLooking(DirectionOfLooking.LEFT)
