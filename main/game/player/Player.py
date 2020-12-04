import copy
import logging
import sys

import numpy as np

from game.player.DirectionOfLooking import DirectionOfLooking
from game.player.Pathfinding import AStar

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger()

class Player(object):
    def __init__(self, id: int, x: int, y: int, directionOfLooking: str, active: bool, speed: int):
        self.id = id
        self.x = x
        self.y = y
        self.directionOfLooking = DirectionOfLooking[directionOfLooking.upper()]
        self.active = active
        self.speed = speed

    def turnDirectionOfLooking(self, directionOfLooking: DirectionOfLooking):
        '''Turns current direction to given direction if possible'''
        if directionOfLooking == self.directionOfLooking or directionOfLooking.value == self.directionOfLooking.value * -1:
            logging.debug(
                'Cant change direction, reason: Input direction is in opposite or same direction as previous one ')
        else:
            self.directionOfLooking = directionOfLooking

    def speedUp(self):
        '''Accelerate one speed'''
        if self.speed == 10:
            logging.debug('Cant accelerate, reason: I Am Speed! (Speed = 10)')
        else:
            self.speed += 1

    def speedDown(self):
        '''Decelerates one speed'''
        if self.speed == 1:
            logging.debug('Cant decelerate, reason: Don\'t stop me now! (Speed =1 )')
        else:
            self.speed -= 1

    def updatePlayer(self, id: int, x: int, y: int, directionOfLooking: DirectionOfLooking, active: bool, speed: int):
        '''Updates the player'''
        if id != self.id:
            logging.debug('No matching ID of player')
        else:
            self.x = x
            self.y = y
            self.directionOfLooking = directionOfLooking
            self.active = active
            self.speed = speed

    def die(self):
        '''Player cant move any further so it dies'''
        self.speed = 0
        self.active = False

    def tryToSurvive(self, playground):
        '''Different strategies to keep the player alive'''
        if self.active:

            # Strategie: Weit entferntestes Feld finden
            maxval, maxvalX, maxvalY, tempCS = self.findFurthestField(playground)

            if not self.moveToFurthestField(playground, maxvalX, maxvalY):
                print("CANT FIND ZE PATH, I TRY TO BIEG AB!")
                self.fallBackPlan(playground)

    def jumpOverWall(self, playground):
        '''
        Look again for furthest field, but this time with a jump and wall
        '''
        pass

    def findFurthestField(self, playground):
        '''Fills out a coordinate system, to tell how far the player can move'''
        logger.disabled = True

        global newNodes
        currentNodes = []
        currentNodes.append((self.x, self.y))
        newNodes = []
        tempCS = copy.deepcopy(playground.coordinateSystem)
        count = 10
        turn = playground.getTurn()

        # So lange zu prüfende Knoten verfügbar sind
        while len(currentNodes) > 0:

            # Iteriere über alle anliegenden Knoten
            while len(currentNodes) > 0:
                x = currentNodes[0][0]
                y = currentNodes[0][1]
                logger.debug("CurrentNodes Entry: [" + str(x) + ", " + str(y) + "]")
                self.checkAllNodesSurround(tempCS, x, y, count, turn)
                currentNodes.remove(currentNodes[0])

             # Füge neu entdeckte Knoten hinzu nachdem alle aktuellen Knoten geprüft wurden
            while len(newNodes) > 0:
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
                    logger.debug("Max Val (" + str(maxval) + ") at [" + str(j) + ", " + str(i) + "]")
                    return maxval, maxvalX, maxvalY, tempCS

    def checkAllNodesSurround(self, tempCS, x, y, count, turn):
        '''Checks all surrounding nodes of a given node'''
        # up
        self.checkUp(tempCS, x, y, count, turn)
        # right
        self.checkRight(tempCS, x, y, count, turn)
        # left
        self.checkLeft(tempCS, x, y, count, turn)
        # down
        self.checkDown(tempCS, x, y, count, turn)

    def checkRight(self, tempCS, currentPosX, currentPosY, count, turn):
        '''Checks the right node'''
        checkX = currentPosX + 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count, turn)

    def checkUp(self, tempCS, currentPosX, currentPosY, count, turn):
        '''Checks the upper node'''
        checkX = currentPosX
        checkY = currentPosY - 1
        self.checkPos(tempCS, checkX, checkY, count, turn)

    def checkDown(self, tempCS, currentPosX, currentPosY, count, turn):
        '''Checks the node below'''
        checkX = currentPosX
        checkY = currentPosY + 1
        self.checkPos(tempCS, checkX, checkY, count, turn)

    def checkLeft(self, tempCS, currentPosX, currentPosY, count, turn):
        '''Checks the left node'''
        checkX = currentPosX - 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count, turn)

    def checkPos(self, tempCS, checkX, checkY, count, turn):
        '''Checks if the given node is free or occupied'''

        if checkX >= 0 and checkX < len(tempCS[0]) and checkY >= 0 and checkY < len(tempCS):
            if tempCS[checkY][checkX] == 0 or count == 10 or (turn == 6 and self.speed >= 3):
                tempCS[checkY][checkX] = count
                #print("New Node Entry: [" + str(checkX) + ", " + str(checkY) + "]")
                newNodes.append((checkX, checkY))
            else:
                if tempCS[checkY][checkX] < 10:
                    tempCS[checkY][checkX] = -1

    def moveToFurthestField(self, playground, maxvalX, maxvalY):

        # Use a Fancy Technic to calculate the mindblown most Intelligent way from start to end
        finder = AStar(playground.coordinateSystem, self.x, self.y, self.speed)
        path = finder.solve((maxvalX, maxvalY))
        '''pathcoords = path
        PP = PlaygroundPresenter
        for i in range(0, len(pathcoords)):
            pathcoords[i] = [pathcoords[i][0] * (PP.blockwidth / 2), pathcoords[i][1] * (PP.blockwidth) / 2]
        PP.py.draw.lines(PP.py.display.get_active(), PP.playerColors[self.id], False, pathcoords)
        '''

        if path != None and len(path) > 0:
            print("Neuer Pfad:" + str(path))

        if path is None or len(path) <= 0:
            return False
        print("Neuer Pfad:" + str(path))

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
