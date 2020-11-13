import logging
import sys

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
        if directionOfLooking.value % 2 == self.directionOfLooking.value % 2:
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

    def turnToSurvive(self, playground):
        xCoordinateOfPlayer = self.x
        yCoordinateOfPlayer = self.y


        if playground.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer-1] == 0 and self.directionOfLooking != DirectionOfLooking.LEFT and (0 <= xCoordinateOfPlayer-1 < len(playground.coordinateSystem[0]) and 0 <= yCoordinateOfPlayer < len(playground.coordinateSystem)):
            print("I try to turn Left")
            self.turnDirectionOfLooking(DirectionOfLooking.LEFT)
        elif playground.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer+1] == 0 and self.directionOfLooking != DirectionOfLooking.RIGHT and (0 <= xCoordinateOfPlayer+1 < len(playground.coordinateSystem[0]) and 0 <= yCoordinateOfPlayer < len(playground.coordinateSystem)):
            print("I try to turn Right")
            self.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
        elif playground.coordinateSystem[yCoordinateOfPlayer+1][xCoordinateOfPlayer] == 0 and self.directionOfLooking != DirectionOfLooking.DOWN and (0 <= xCoordinateOfPlayer < len(playground.coordinateSystem[0]) and 0 <= yCoordinateOfPlayer+1 < len(playground.coordinateSystem)):
            print("I try to turn Down")
            self.turnDirectionOfLooking(DirectionOfLooking.DOWN)
        elif playground.coordinateSystem[yCoordinateOfPlayer-1][xCoordinateOfPlayer] == 0 and self.directionOfLooking != DirectionOfLooking.UP and (0 <= xCoordinateOfPlayer < len(playground.coordinateSystem[0]) and 0 <= yCoordinateOfPlayer-1 < len(playground.coordinateSystem)):
            print("I try to turn Up")
            self.turnDirectionOfLooking(DirectionOfLooking.UP)
        else:
            print("nowhere to run")

    def tryToSurvive(self, playground):
        if self.active:
            #check 4 positions as far as speed amount
            xCoordinateOfPlayer = self.x
            yCoordinateOfPlayer = self.y

            if self.directionOfLooking == DirectionOfLooking.LEFT:
                xCoordinateOfPlayer -= 1
            elif self.directionOfLooking == DirectionOfLooking.UP:
                yCoordinateOfPlayer -= 1
            elif self.directionOfLooking == DirectionOfLooking.RIGHT:
                xCoordinateOfPlayer += 1
            elif self.directionOfLooking == DirectionOfLooking.DOWN:
                yCoordinateOfPlayer += 1

            if 0 <= xCoordinateOfPlayer < len(playground.coordinateSystem[0]) and 0 <= yCoordinateOfPlayer < len(playground.coordinateSystem):
                # within coordinate system

                if playground.coordinateSystem[yCoordinateOfPlayer][xCoordinateOfPlayer] == 0:
                    #Player did not collide with wall
                    pass
                else:
                    print("i'm gonna die")
                    self.turnToSurvive(playground)
            else:
                print("i'm gonna die")
                self.turnToSurvive(playground)

