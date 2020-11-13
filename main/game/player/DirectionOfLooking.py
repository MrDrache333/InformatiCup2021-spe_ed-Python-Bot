from enum import Enum


class DirectionOfLooking(Enum):
    '''Keys contain values that correspond to the x/y direction on the coordinatefield
    e.g. UP := y = -1 | DOWN := y = 1 | DOWNLEFT := x,y = -1, 1'''
    UP = 0, -1
    RIGHT = 1, 0
    DOWN = 0, 1
    LEFT = -1, 0
    UPRIGHT = 1, -1
    DOWNRIGHT = 1, 1
    DOWNLEFT = -1, 1
    UPLEFT = -1, -1
