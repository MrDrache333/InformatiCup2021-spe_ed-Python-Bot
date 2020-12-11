import copy
import logging
import random
import sys

import numpy as np

from game.player.DirectionOfLooking import DirectionOfLooking
from game.player.Pathfinding import AStar

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger()
logger.disabled = True


def checkIfCoordinateIsInCoordinateSystem(givenX, givenY, coordinateSystem):
    if len(coordinateSystem) > givenY >= 0 and len(coordinateSystem[0]) > givenX >= 0:
        return True
    return False


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

    def printMatrix(self, matrix):
        for y in matrix:
            line = ""
            for x in y:
                line += ((str(x) if len(str(x)) == 2 else "0" + str(x)) + " ")
            print(line)

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

    def tryToSurvive(self, playgroundPresenter):
        """Different strategies to keep the player alive"""
        if self.active:
            self.choosenTurn = "change_nothing"
            playground = playgroundPresenter.getPlayground()
            self.rideAlongSideWall(playground)
            """
            # Strategie: Weit entferntestes Feld finden
            maxval, maxvalX, maxvalY, tempCS = self.findFurthestField(playground)

            if not self.moveToFurthestField(playgroundPresenter, maxvalX, maxvalY, tempCS):
                print("CANT FIND ZE PATH, I TRY TO BIEG AB!")
                self.fallBackPlan(playground)"""

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
        print("Ride alongside wall")

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

                    freeBlocks.pop(self.directionOfLooking)

                    isGapOneCellWide = 0
                    for direction in freeBlocks.keys():
                        tempX = currentX + direction.value[0]
                        tempY = currentY + direction.value[1]
                        # check if coordinate is within system
                        if checkIfCoordinateIsInCoordinateSystem(tempX, tempY, playground.coordinateSystem):
                            if not playground.coordinateSystem[tempY][tempX] == 0:
                                isGapOneCellWide += 1

                    if isGapOneCellWide == 2:
                        # Cell is one wide. check if space behind cell is larger, than the
                        lookDirectionAlongSideWallLeft, lookDirectionAlongSideWallRight = setOfDirections[
                                                                                              (setOfDirections.index(
                                                                                                  self.directionOfLooking) + 3) % 4], \
                                                                                          setOfDirections[
                                                                                              (setOfDirections.index(
                                                                                                  self.directionOfLooking) + 1) % 4]

                        if self.getAmountOfFreeSpaces(self.x, self.y, self.directionOfLooking,
                                                      playground.coordinateSystem) >= (
                                self.getAmountOfFreeSpaces(self.x, self.y, lookDirectionAlongSideWallLeft,
                                                           playground.coordinateSystem) or self.getAmountOfFreeSpaces(
                                self.x, self.y, lookDirectionAlongSideWallRight, playground.coordinateSystem)):
                            self.speedDown()
                        elif self.getAmountOfFreeSpaces(self.x, self.y, lookDirectionAlongSideWallLeft,
                                                        playground.coordinateSystem) >= self.getAmountOfFreeSpaces(
                            self.x, self.y, lookDirectionAlongSideWallRight, playground.coordinateSystem) :
                            self.turnDirectionOfLooking(lookDirectionAlongSideWallLeft)
                        else:
                            self.turnDirectionOfLooking(lookDirectionAlongSideWallRight)
                    else:
                        self.speedDown()

            else:
                # player is adjacent to wall and looking into it. Player has to change his direction of looking
                # Change direction of looking to the direction with the most space available
                lookDirectionAlongSideWallLeft, lookDirectionAlongSideWallRight = setOfDirections[
                                                                                      (setOfDirections.index(
                                                                                          self.directionOfLooking) + 3) % 4], \
                                                                                  setOfDirections[
                                                                                      (setOfDirections.index(
                                                                                          self.directionOfLooking) + 1) % 4]

                if self.getAmountOfFreeSpaces(self.x, self.y, lookDirectionAlongSideWallLeft,
                                              playground.coordinateSystem) > self.getAmountOfFreeSpaces(self.x, self.y,
                                                                                                         lookDirectionAlongSideWallRight,
                                                                                                         playground.coordinateSystem):
                    self.turnDirectionOfLooking(lookDirectionAlongSideWallLeft)
                else:
                    self.turnDirectionOfLooking(lookDirectionAlongSideWallRight)

        else:
            if self.directionOfLooking == directionOfClosestWall:
                if distanceOfNearestWall >= self.speed:
                    # Player is already going to the closest wall and has enough space to go into it. Slow down to stall
                    self.speedDown()
                    return
                else:
                    # player is turned into the closes wall, but does not have enough space to go near it. Player has to
                    # turn in another direction
                    setOfDirections.remove(directionOfClosestWall)
                    self.turnDirectionOfLooking(random.choices(setOfDirections))
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

    def getAmountOfFreeSpaces(self, givenX, givenY, directionOfLooking, coordinateSystem):
        """returns the amount of free spaces in the given coordinatesystem from a given coordinate and direction"""
        # 1. black out coordinate behind given coordinate
        # 2. check coordinate up if coordinate == 0 add 1 to free space counter run 2. on this coordinate
        # 3. check coordinate right if coordinate == 0 add 1 to free space counter run 3. on this coordinate
        # 4. check coordinate down if coordinate == 0 add 1 to free space counter run 2. on this coordinate
        # 5. ...
        # 6. return free space

        temporaryCoordinateSystem = copy.deepcopy(coordinateSystem)

        tmpX, tmpY =directionOfLooking.value

        givenX += tmpX
        givenY += tmpY

        if checkIfCoordinateIsInCoordinateSystem(givenX, givenY, temporaryCoordinateSystem):
            if not temporaryCoordinateSystem[givenY][givenX] == 0:
                return 0
            else:
                temporaryCoordinateSystem[givenY][givenX] = -1



        amountOfFreeSpaces = self.checkSurroundingCellsForEmptiness(givenX, givenY, temporaryCoordinateSystem)

        return amountOfFreeSpaces

    def checkSurroundingCellsForEmptiness(self, givenX, givenY, coordinateSystem):
        """ATTENTION: This method is reserved fot the 'getAmountOfFreeSpaces' method. It recursively counts free
        spaces in a given coordinatesystem and marks them as they are counted """
        setOfDirections = [DirectionOfLooking.UP, DirectionOfLooking.RIGHT, DirectionOfLooking.DOWN,
                           DirectionOfLooking.LEFT]

        amountOfFreeSpaces = 0

        # check surrounding nodes for emptiness
        for direction in setOfDirections:
            tmpX, tmpY = direction.value
            toBeAnalysedX = givenX + tmpX
            toBeAnalysedY = givenY + tmpY
            if checkIfCoordinateIsInCoordinateSystem(toBeAnalysedX, toBeAnalysedY, coordinateSystem):
                if coordinateSystem[toBeAnalysedY][toBeAnalysedX] == 0:
                    coordinateSystem[toBeAnalysedY][toBeAnalysedX] = -1
                    amountOfFreeSpaces = self.checkSurroundingCellsForEmptiness(toBeAnalysedX, toBeAnalysedY,
                                                                                coordinateSystem) + 1

        return amountOfFreeSpaces

    def findFurthestField(self, playground):
        """Fills out a coordinate system, to tell how far the player can move"""
        logger.disabled = True

        global newNodes
        currentNodes = [(self.x, self.y)]
        newNodes = []
        tempCS = copy.deepcopy(playground.coordinateSystem)
        count = 10
        turn = playground.getTurn()
        tempSpeed = self.speed

        # So lange zu prüfende Knoten verfügbar sind
        while currentNodes:

            # Iteriere über alle anliegenden Knoten
            while currentNodes:
                x = currentNodes[0][0]
                y = currentNodes[0][1]
                logger.debug("CurrentNodes Entry: [" + str(x) + ", " + str(y) + "]")
                self.checkAllNodesSurround(tempCS, x, y, count, turn)
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
        for (i, row) in enumerate(tempCS):
            for (j, value) in enumerate(row):
                if value == maxval:
                    maxvalX = j
                    maxvalY = i
                    logger.debug(
                        "Max Val ("
                        + str(maxval)
                        + ") at ["
                        + str(maxvalX)
                        + ", "
                        + str(maxvalY)
                        + "]"
                    )

                    return maxval, maxvalX, maxvalY, tempCS

    def checkAllNodesSurround(self, tempCS, x, y, count, turn):
        """Checks all surrounding nodes of a given node"""
        # up
        self.checkUp(tempCS, x, y, count, turn)
        # right
        self.checkRight(tempCS, x, y, count, turn)
        # left
        self.checkLeft(tempCS, x, y, count, turn)
        # down
        self.checkDown(tempCS, x, y, count, turn)

    def checkRight(self, tempCS, currentPosX, currentPosY, count, turn):
        """Checks the right node"""
        for i in range(self.speed):
            checkX = currentPosX + (i + 1)
            checkY = currentPosY
            if turn == 6 and (self.speed - 2) < (i + 1) < self.speed:
                jump = True
            else:
                jump = False

            add = (i + 1) == self.speed
            if not self.checkPos(tempCS, checkX, checkY, count, jump, add):
                break

    def checkUp(self, tempCS, currentPosX, currentPosY, count, turn):
        """Checks the upper node"""
        for i in range(self.speed):
            checkX = currentPosX
            checkY = currentPosY - (i + 1)
            if turn == 6 and (self.speed - 2) < (i + 1) < self.speed:
                jump = True
            else:
                jump = False

            add = (i + 1) == self.speed
            if not self.checkPos(tempCS, checkX, checkY, count, jump, add):
                break

    def checkDown(self, tempCS, currentPosX, currentPosY, count, turn):
        """Checks the node below"""
        for i in range(self.speed):
            checkX = currentPosX
            checkY = currentPosY + (i + 1)
            if turn == 6 and (self.speed - 2) < (i + 1) < self.speed:
                jump = True
            else:
                jump = False

            add = (i + 1) == self.speed
            if not self.checkPos(tempCS, checkX, checkY, count, jump, add):
                break

    def checkLeft(self, tempCS, currentPosX, currentPosY, count, turn):
        """Checks the left node"""
        for i in range(self.speed):
            checkX = currentPosX - (i + 1)
            checkY = currentPosY
            if turn == 6 and (self.speed - 2) < (i + 1) < self.speed:
                jump = True
            else:
                jump = False

            add = (i + 1) == self.speed
            if not self.checkPos(tempCS, checkX, checkY, count, jump, add):
                break

    def checkPos(self, tempCS, checkX, checkY, count, jump, add):
        '''Checks if the given node is free or occupied'''

        if 0 <= checkX < len(tempCS[0]) and 0 <= checkY < len(tempCS):
            if tempCS[checkY][checkX] == 0 or (jump and tempCS[checkY][checkX] < 10):
                tempCS[checkY][checkX] = count
                # print("New Node Entry: [" + str(checkX) + ", " + str(checkY) + "]")
                if add:
                    newNodes.append((checkX, checkY))
                return True
            else:
                if tempCS[checkY][checkX] < 10:
                    tempCS[checkY][checkX] = -1
                    return False

    def moveToFurthestField(self, playgroundPresenter, maxvalX, maxvalY, tempCS):
        playground = playgroundPresenter.getPlayground()

        hasToBeCorrected = False

        if not self.isCoordinateFree(maxvalX, maxvalY, playground):
            print("Maximal entfernte gegebenen Koordinate ist bereits belegt!")
            hasToBeCorrected = True
        if (maxvalX % self.speed != self.x % self.speed) or (maxvalY % self.speed != self.y % self.speed):
            hasToBeCorrected = True
            print("Maximal entfernte gegebenen Koordinate ist NICHT erreichbar!")

        # Correct maxvalX and maxvalY by selecting the Nearest Cell to the Initial One
        if maxvalX % self.speed != self.x % self.speed:
            newmaxvalx = self.x
            if maxvalX < self.x:
                while newmaxvalx > maxvalX and newmaxvalx - self.speed >= 0:
                    newmaxvalx -= self.speed
            if maxvalX > self.x:
                while newmaxvalx < maxvalX and newmaxvalx + self.speed < len(playground.coordinateSystem[0]):
                    newmaxvalx += self.speed
            maxvalX = newmaxvalx

        if maxvalY % self.speed != self.y % self.speed:
            newmaxvaly = self.y
            if maxvalY < self.y:
                while newmaxvaly > maxvalY and newmaxvaly - self.speed >= 0:
                    newmaxvaly -= self.speed
            if maxvalY > self.y:
                while newmaxvaly < maxvalY and newmaxvaly + self.speed < len(playground.coordinateSystem):
                    newmaxvaly += self.speed
            maxvalY = newmaxvaly

        finder = AStar(playground.coordinateSystem, self.x, self.y, self.speed, playground.getTurn())
        path = finder.solve((maxvalX, maxvalY))
        if path is None or len(path) == 0:
            hasToBeCorrected = True
        # NOTLÖSUNG, falls kein Pfad vorhanden
        if hasToBeCorrected:
            print("NOTLÖSUNG: Versuche Koordinate zu korrigieren!")
            count = 1
            fastestReachable = []
            while (count < 3 and (len(playground.coordinateSystem[0]) > (count * self.speed + self.x) >= 0) or (
                    len(playground.coordinateSystem) > (count * self.speed + self.y) >= 0) or (
                           len(playground.coordinateSystem[0]) > (self.x - count * self.speed) >= 0) or (
                           len(playground.coordinateSystem) > (self.y - count * self.speed) >= 0)):
                for ym in range(count * -1, count + 1):
                    for xm in range(count * -1, count + 1):
                        # If Cells to test were already tested, next
                        if abs(xm) < count and abs(ym) < count:
                            continue
                        # Calc new Coordinate to check
                        tempX = maxvalX + xm * self.speed
                        tempY = maxvalY + ym * self.speed
                        # Test if new coordinate is out of bounds
                        if not (len(playground.coordinateSystem[0]) > tempX >= 0) or not (
                                len(playground.coordinateSystem) > tempY >= 0):
                            continue
                        # Test if new Coord is free
                        if self.isCoordinateFree(tempX, tempY, playground):
                            fastestReachable.append([tempX, tempY])
                count += 1
            path = []
            for coord in fastestReachable:
                finder = AStar(playground.coordinateSystem, self.x, self.y, self.speed, playground.getTurn())
                path = finder.solve(coord)
                if path is not None and len(path) > 0:
                    print("NOTLÖSUNG: Erreichbare Alternative gefunden! " + str(maxvalX) + ":" + str(
                        maxvalY) + " -> " + str(coord[0]) + ":" + str(coord[1]) + " Dist: " + str(
                        abs(maxvalX - coord[0] + abs(maxvalY - coord[1]))))
                    break

        # PP = PlaygroundPresenter(playground, len(playground.coordinateSystem), len(playground.coordinateSystem[0]))
        self.path = path

        if path is not None and len(path) > 0:
            print("Neuer Pfad:" + str(path))
        else:
            # self.printMatrix(tempCS)
            print("Nix Pfad gefunden :/ von " + str(self.x) + ":" + str(self.y) + " nach " + str(maxvalX) + ":" + str(
                maxvalY))
            return False

        firstPathX = path[1][0]
        firstPathY = path[1][1]

        print(
            "I'm at [" + str(self.x) + ", " + str(self.y) + "] ant want to go to [" + str(firstPathX) + ", " + str(
                firstPathY) + "]")

        if firstPathX > self.x:
            self.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
            print("Turn right")
        elif firstPathX < self.x:
            self.turnDirectionOfLooking(DirectionOfLooking.LEFT)
            print("Turn left")
        elif firstPathY > self.y:
            self.turnDirectionOfLooking(DirectionOfLooking.DOWN)
            print("Turn down")
        elif firstPathY < self.y:
            self.turnDirectionOfLooking(DirectionOfLooking.UP)
            print("Turn up")

        return True

    def fallBackPlan(self, playground):

        # Prüfe wie viele Blöcke in jeder Richtung frei sind
        freeBlocks = [playground.countBlocksInStraightLine(self, DirectionOfLooking.UP),
                      playground.countBlocksInStraightLine(self, DirectionOfLooking.RIGHT),
                      playground.countBlocksInStraightLine(self, DirectionOfLooking.DOWN),
                      playground.countBlocksInStraightLine(self, DirectionOfLooking.LEFT)]

        # Ändere Kurs, zur Richtung wo am meisten Blöcke frei sind
        if self.speed > 1 and max(freeBlocks) < self.speed:
            print("[" + str(self.id) + "] I slow down")
            self.speedDown()
        elif freeBlocks.index(max(freeBlocks)) == 0:  # UP
            print("[" + str(self.id) + "] I try to turn Up")
            self.turnDirectionOfLooking(DirectionOfLooking.UP)
        # try right
        elif freeBlocks.index(max(freeBlocks)) == 1:  # RIGHT
            print("[" + str(self.id) + "] I try to turn Right")
            self.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
        # try down
        elif freeBlocks.index(max(freeBlocks)) == 2:  # DOWN
            print("[" + str(self.id) + "] I try to turn Down")
            self.turnDirectionOfLooking(DirectionOfLooking.DOWN)
        # try left
        elif freeBlocks.index(max(freeBlocks)) == 3:  # LEFT
            print("[" + str(self.id) + "] I try to turn Left")
            self.turnDirectionOfLooking(DirectionOfLooking.LEFT)
