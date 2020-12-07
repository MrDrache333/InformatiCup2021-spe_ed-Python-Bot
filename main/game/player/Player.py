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
            self.directionOfLooking = directionOfLooking

    def speedUp(self):
        """Accelerate one speed"""
        if self.speed == 10:
            logging.debug('Cant accelerate, reason: I Am Speed! (Speed = 10)')
        else:
            self.speed += 1

    def speedDown(self):
        """Decelerates one speed"""
        if self.speed == 1:
            logging.debug('Cant decelerate, reason: Don\'t stop me now! (Speed =1 )')
        else:
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

            playground = playgroundPresenter.getPlayground()
            # Strategie: Weit entferntestes Feld finden
            maxval, maxvalX, maxvalY, tempCS = self.findFurthestField(playground)

            if not self.moveToFurthestField(playgroundPresenter, maxvalX, maxvalY, tempCS):
                print("CANT FIND ZE PATH, I TRY TO BIEG AB!")
                self.fallBackPlan(playground)

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
            if not self.directionOfLooking == directionOfClosestWall:
                # the player is adjacent to a wall and not looking at it. Commence plan.
                # if the player would hit a wall, change direction
                # else slow down
                if freeBlocks.get(self.directionOfLooking) < self.speed:
                    # not enough space in direction of player. change direction
                    directionThePlayerShouldTurnTo = setOfDirections[
                        (setOfDirections.index(self.directionOfLooking) + 1) % 4]
                    self.directionOfLooking = directionThePlayerShouldTurnTo
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
                        if len(playground.coordinateSystem[0]) > tempX and len(playground.coordinateSystem) > tempY:
                            if not playground.coordinateSystem[tempY][tempX] == 0:
                                isGapOneCellWide += 1

                    if isGapOneCellWide == 2:
                        directionThePlayerShouldTurnTo = setOfDirections[
                            (setOfDirections.index(self.directionOfLooking) + 1) % 4]
                        self.directionOfLooking = directionThePlayerShouldTurnTo
                    else:
                        self.speedDown()

            else:
                # player is adjacent to wall and looking into it. Player has to change his direction of looking
                # Change direction of looking to archive clockwise motion
                directionThePlayerShouldTurnTo = setOfDirections[
                    (setOfDirections.index(self.directionOfLooking) + 1) % 4]
                self.directionOfLooking = directionThePlayerShouldTurnTo
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
                    self.directionOfLooking = random.choices(setOfDirections)
                    return
            else:
                if distanceOfNearestWall >= self.speed:
                    # player is not turned to the closest wall, and has enough space to come closer to it without
                    # hitting it so he turns into it
                    self.directionOfLooking = directionOfClosestWall
                    return
                else:
                    # player is not turned to the closest wall, but does not have enough space to to turn into it, slow
                    # down to stall and prepare for turning into wall
                    self.speedDown()
                    return

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

        # Use a Fancy Technic to calculate the mindblown most Intelligent way from start to end
        # Get the Best Path for each Speed
        finder = AStar(playground.coordinateSystem, self.x, self.y, self.speed, playground.getTurn())

        if not self.isCoordinateFree(maxvalX, maxvalY, playground):
            print("Maximal entfernte gegebenen Koordinate ist bereits belegt!")
        if (maxvalX % self.speed != self.x % self.speed) or (maxvalY % self.speed != self.y % self.speed):
            print("Maximal entfernte gegebenen Koordinate ist NICHT erreichbar!")
        oldmaxVal = (maxvalX, maxvalY)
        # Correct maxvalX and maxvalY
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

        oldpath = playground.players[int(self.id) - 1].path
        if not self.isCoordinateFree(maxvalX, maxvalY, playground) and oldpath is not None:
            for coord in reversed(oldpath):
                if self.isCoordinateFree(coord[0], coord[1], playground):
                    maxvalX = coord[0]
                    maxvalY = coord[1]

        path = finder.solve((maxvalX, maxvalY))

        # PP = PlaygroundPresenter(playground, len(playground.coordinateSystem), len(playground.coordinateSystem[0]))
        self.path = path

        if path != None and len(path) > 0:
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
            print("[" + self.id + "] I slow down")
            self.speedDown()
        elif freeBlocks.index(max(freeBlocks)) == 0:  # UP
            print("[" + self.id + "] I try to turn Up")
            self.turnDirectionOfLooking(DirectionOfLooking.UP)
        # try right
        elif freeBlocks.index(max(freeBlocks)) == 1:  # RIGHT
            print("[" + self.id + "] I try to turn Right")
            self.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
        # try down
        elif freeBlocks.index(max(freeBlocks)) == 2:  # DOWN
            print("[" + self.id + "] I try to turn Down")
            self.turnDirectionOfLooking(DirectionOfLooking.DOWN)
        # try left
        elif freeBlocks.index(max(freeBlocks)) == 3:  # LEFT
            print("[" + self.id + "] I try to turn Left")
            self.turnDirectionOfLooking(DirectionOfLooking.LEFT)
