import copy
import logging
import sys
import time

import numpy as np

from game.player.DirectionOfLooking import DirectionOfLooking
from game.player.Pathfinding import AStar

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class Player(object):
    def __init__(self, id: int, x: int, y: int, directionOfLooking: str, active: bool, speed: int):
        self.id = id
        self.x = x
        self.y = y
        self.directionOfLooking = DirectionOfLooking[directionOfLooking.upper()]
        self.active = active
        self.speed = speed

    def turnDirectionOfLooking(self, directionOfLooking: DirectionOfLooking):

        if directionOfLooking == self.directionOfLooking or directionOfLooking.value == self.directionOfLooking.value * -1:
            logging.debug(
                'Cant change direction, reason: Input direction is in opposite or same direction as previous one ')
        else:
            self.directionOfLooking = directionOfLooking

    def speedUp(self):
        if self.speed == 10:
            logging.debug('Cant accelerate, reason: I Am Speed! (Speed = 10)')
        else:
            self.speed += 1

    def speedDown(self):
        if self.speed == 1:
            logging.debug('Cant decelerate, reason: Don\'t stop me now! (Speed =1 )')
        else:
            self.speed -= 1

    def updatePlayer(self, id: int, x: int, y: int, directionOfLooking: DirectionOfLooking, active: bool, speed: int):
        if id != self.id:
            logging.debug('No matching ID of player')
        else:
            self.x = x
            self.y = y
            self.directionOfLooking = directionOfLooking
            self.active = active
            self.speed = speed

    def die(self):
        self.speed = 0
        self.active = False

    def tryToSurvive(self, playground):
        if self.active:

            #Strategie: Weit entferntestes Feld finden
            maxvalX, maxvalY = self.findFurthestField(playground)


            # Use a Fancy Technic to calculate the mindblown most Intelligent way from start to end
            finder = AStar(playground.coordinateSystem, self.x, self.y)
            path = finder.solve((maxvalX, maxvalY))

            if path != None and len(path) > 0:

                print("Neuer Pfad:" + str(path))

                firstPathX = path[1][0]
                firstPathY = path[1][1]

                print("I'm at [" + str(self.x) + ", " + str(self.y) + "] ant want to go to [" + str(firstPathX) + ", " + str(firstPathY) + "]")

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

            # Ändere Richtung immer in die Richtung wo am meisten Blöcke frei sind
            else:
                print("I DONT KNOW WHAT TO DO!")


            '''
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
            '''

    # Füllt ein Koordinatensystem mit Werten um ausgehend der Spielerposition den weit entferntesten Punkt zu finden
    def findFurthestField(self, playground):

        debug = False

        global newNodes
        currentNodes = []
        currentNodes.append((self.x, self.y))
        newNodes = []
        tempCS = copy.deepcopy(playground.coordinateSystem)
        count = 10

        # So lange zu prüfende Knoten verfügbar sind
        while len(currentNodes) > 0:

            # Iteriere über alle anliegenden Knoten
            while len(currentNodes) > 0:
                x = currentNodes[0][0]
                y = currentNodes[0][1]
                if debug:
                    print("CurrentNodes Entry: [" + str(x) + ", " + str(y) + "]")
                self.checkAllNodesSurround(tempCS, x, y, count)
                currentNodes.remove(currentNodes[0])

             # Füge neu entdeckte Knoten hinzu nachdem alle aktuellen Knoten geprüft wurden
            while len(newNodes) > 0:
                currentNodes.append(newNodes[0])
                if debug:
                    print(" -- " + str(newNodes[0]) + " -> currentNodes")
                newNodes.remove(newNodes[0])

            count += 1

            if debug:
                print("---------------")
                for c in tempCS:
                    print(c)


        if debug:
            print("---------------")
            for c in tempCS:
                print(c)

        # Maximalen Wert im Koordinatensystem suchen und zurück geben
        maxval = np.amax(tempCS)
        for (i, row) in enumerate(tempCS):
            for (j, value) in enumerate(row):
                if value == maxval:
                    maxvalX = j
                    maxvalY = i
                    print("Max Val (" + str(maxval) + ") at [" + str(j) + ", " + str(i) + "]")
                    return maxvalX, maxvalY


    # Prüfe alle anliegenden Knoten
    def checkAllNodesSurround(self, tempCS, x, y, count):
        # up
        self.checkUp(tempCS, x, y, count)
        # right
        self.checkRight(tempCS, x, y, count)
        # left
        self.checkLeft(tempCS, x, y, count)
        # down
        self.checkDown(tempCS, x, y, count)

    # Prüfe rechten Knoten
    def checkRight(self, tempCS, currentPosX, currentPosY, count):
        checkX = currentPosX + 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count)

    # Prüfe obeneren Knoten
    def checkUp(self, tempCS, currentPosX, currentPosY, count):
        checkX = currentPosX
        checkY = currentPosY - 1
        self.checkPos(tempCS, checkX, checkY, count)

    # Prüfe unteren Knoten
    def checkDown(self, tempCS, currentPosX, currentPosY, count):
        checkX = currentPosX
        checkY = currentPosY + 1
        self.checkPos(tempCS, checkX, checkY, count)

    # Prüfe linken Knoten
    def checkLeft(self, tempCS, currentPosX, currentPosY, count):
        checkX = currentPosX - 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count)

    # Prüfe ob Knoten frei ist oder Hindernis beinhaltet
    def checkPos(self, tempCS, checkX, checkY, count):

        if checkX >= 0 and checkX < len(tempCS[0]) and checkY >= 0 and checkY < len(tempCS):
            if tempCS[checkY][checkX] == 0 or count == 10:
                tempCS[checkY][checkX] = count
                #print("New Node Entry: [" + str(checkX) + ", " + str(checkY) + "]")
                newNodes.append((checkX, checkY))
            else:
                if tempCS[checkY][checkX] < 10:
                    tempCS[checkY][checkX] = -1