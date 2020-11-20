import copy
import logging
import sys

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

            tempCS = copy.deepcopy(playground.coordinateSystem)
            count = 6
            # self.findFarrestField(tempCS, self.x, self.y, count)

            # Use a Fancy Technic to calculate the mindblown most Intelligent way from start to end
            finder = AStar(playground.coordinateSystem, self.x, self.y)
            path = finder.solve((0, 5))
            print(path)

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

    def findFarrestField(self, tempCS, x, y, count):
        # check nearest nodes

        print("Current Pos: " + str(x) + " x " + str(y) + " with count: " + str(count))
        currentPosX = x
        currentPosY = y

        # up
        checkX = currentPosX
        checkY = currentPosY - 1
        self.checkPos(tempCS, checkX, checkY, count)

        # right
        checkX = currentPosX + 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count)

        # down
        checkX = currentPosX
        checkY = currentPosY - 1
        self.checkPos(tempCS, checkX, checkY, count)

        # left
        checkX = currentPosX - 1
        checkY = currentPosY
        self.checkPos(tempCS, checkX, checkY, count)

    def checkPos(self, tempCS, checkX, checkY, count):
        print("---------------")
        # print(tempCS)
        for c in tempCS:
            print(c)
        if 0 <= checkX < len(tempCS[0]) and 0 <= checkY < len(tempCS):
            if tempCS[checkY][checkX] == 0:
                tempCS[checkY][checkX] = count
                count += 1
                self.findFarrestField(tempCS, checkX, checkY, count)
            else:
                if tempCS[checkY][checkX] < 6:
                    tempCS[checkY][checkX] = -1
