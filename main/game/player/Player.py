import copy
import logging
import sys
import numpy as np
import time

from game.player.DirectionOfLooking import DirectionOfLooking

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

            tempCS = copy.deepcopy(playground.coordinateSystem)
            count = 6

            print("---------------")


            self.findFarrestFieldUp(tempCS, self.x, self.y, count)
            print("---------------")
            # print(tempCS)
            for c in tempCS:
                print(c)
            self.findFarrestFieldDown(tempCS, self.x, self.y, count)
            print("---------------")
            # print(tempCS)
            for c in tempCS:
                print(c)
            self.findFarrestFieldLeft(tempCS, self.x, self.y, count)
            print("---------------")
            # print(tempCS)
            for c in tempCS:
                print(c)
            self.findFarrestFieldRight(tempCS, self.x, self.y, count)
            print("---------------")
            # print(tempCS)
            for c in tempCS:
                print(c)


            maxval = np.amax(tempCS)

            for (i, row) in enumerate(tempCS):
                for (j, value) in enumerate(row):
                    if value == maxval:
                        print("Max Val (" + str(maxval) + ") at [" + str(i) + ", " + str(j) + "]")
                        break

            time.sleep(2)

            # if(playground.countBlocksInStraightLine(self, self.directionOfLooking) < self.speed):
            # print("[" + self.id + "] Directory im facing is occupied")
            if False:
                freeBlocks = [playground.countBlocksInStraightLine(self, DirectionOfLooking.UP),
                              playground.countBlocksInStraightLine(self, DirectionOfLooking.RIGHT),
                              playground.countBlocksInStraightLine(self, DirectionOfLooking.DOWN),
                              playground.countBlocksInStraightLine(self, DirectionOfLooking.LEFT)]

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

    def findFarrestFieldUp(self, tempCS, x, y, count):
        # check nearest nodes
        currentPosX = x
        currentPosY = y
        # up
        checkX = currentPosX
        checkY = currentPosY - 1
        self.checkPos(tempCS, checkX, checkY, count, 1)
        # down
        #checkX = currentPosX
        #checkY = currentPosY + 1
        #self.checkPos(tempCS, checkX, checkY, count, 2)
        # right
        checkX = currentPosX + 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count, 1)
        # left
        checkX = currentPosX - 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count, 1)

    def findFarrestFieldDown(self, tempCS, x, y, count):
        # check nearest nodes
        currentPosX = x
        currentPosY = y
        # up
        #checkX = currentPosX
        #checkY = currentPosY - 1
        #self.checkPos(tempCS, checkX, checkY, count)
        # down
        checkX = currentPosX
        checkY = currentPosY + 1
        self.checkPos(tempCS, checkX, checkY, count, 2)
        # right
        checkX = currentPosX + 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count, 2)
        # left
        checkX = currentPosX - 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count, 2)

    def findFarrestFieldLeft(self, tempCS, x, y, count):
        # check nearest nodes
        currentPosX = x
        currentPosY = y

        # left
        checkX = currentPosX - 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count, 3)
        # up
        checkX = currentPosX
        checkY = currentPosY - 1
        self.checkPos(tempCS, checkX, checkY, count, 3)
        # down
        checkX = currentPosX
        checkY = currentPosY + 1
        self.checkPos(tempCS, checkX, checkY, count, 3)
        # right
        #checkX = currentPosX + 1
        #checkY = currentPosY
        #self.checkPos(tempCS, checkX, checkY, count, 2)

    def findFarrestFieldRight(self, tempCS, x, y, count):
        # check nearest nodes
        currentPosX = x
        currentPosY = y

        # left
        #checkX = currentPosX - 1
        #checkY = currentPosY
        #self.checkPos(tempCS, checkX, checkY, count, 3)
        # right
        checkX = currentPosX + 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count, 4)
        # up
        checkX = currentPosX
        checkY = currentPosY - 1
        self.checkPos(tempCS, checkX, checkY, count, 4)
        # down
        checkX = currentPosX
        checkY = currentPosY + 1
        self.checkPos(tempCS, checkX, checkY, count, 4)


    def checkPos(self, tempCS, checkX, checkY, count, val):

        if checkX >= 0 and checkX < len(tempCS[0]) and checkY >= 0 and checkY < len(tempCS):
            if tempCS[checkY][checkX] == 0 or count == 6:
                tempCS[checkY][checkX] = count

                #print("---------------")
                # print(tempCS)
                #for c in tempCS:
                    #print(c)

                #time.sleep(0.1)

                count += 1

                if val == 1: # up
                    self.findFarrestFieldUp(tempCS, checkX, checkY, count)
                elif val == 2: # down
                    self.findFarrestFieldDown(tempCS, checkX, checkY, count)
                elif val == 3:  # left
                    self.findFarrestFieldLeft(tempCS, checkX, checkY, count)
                else: # right
                    self.findFarrestFieldRight(tempCS, checkX, checkY, count)
            else:
                if tempCS[checkY][checkX] < 6:
                    tempCS[checkY][checkX] = -1
