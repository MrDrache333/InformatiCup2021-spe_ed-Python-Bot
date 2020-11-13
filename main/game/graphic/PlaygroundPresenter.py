import tkinter

import pygame

from game.Playground import Playground


class PlaygroundPresenter(object):
    # Defining Constants
    global playerColors
    # Defining PlayerColors
    playerColors = {
        0: (255, 255, 255),  # white / no player
        1: (153, 255, 51),  # Green
        2: (204, 0, 0),  # Red
        3: (0, 128, 255),  # Blue
        4: (255, 128, 51),  # Orange
        5: (255, 51, 153),  # Pink
        6: (96, 96, 96)  # Grey
    }

    def __init__(self, playground: Playground, width, height):
        self.playground = playground
        self.displayWidth = width * 15
        self.displayHeight = height * 15
        self.gameWindow = pygame.display.set_mode((self.displayWidth, self.displayHeight))
        self.generateGameField()

    def generateGameField(self):
        self.updateGameField()
        self.gameWindow.fill((40, 40, 40))
        white = (255, 255, 255)

        x = 0
        y = 0
        for i in range(int(self.displayWidth/15)):
            x += 15
            pygame.draw.line(self.gameWindow, white, (x, 0), (x, self.displayHeight))

        for l in range(int(self.displayHeight/15)):
            y += 15
            pygame.draw.line(self.gameWindow, white, (0, y), (self.displayWidth, y))

        # pygame.display.flip()

        # setting title and favicon
        pygame.display.set_caption("Spe_ed")
        pygame.display.set_icon(pygame.image.load("Lightning_McQueen.png"))

    def updateGameField(self):
        """Draws rectangles in different colors to different players"""
        # fill screen with a white blankspace

        # Determine width and height of a cube

        widthOfCube = self.displayWidth / len(self.playground.coordinateSystem[0])
        heightOfCube = self.displayHeight / len(self.playground.coordinateSystem)
        currentXOfCube = 0
        currentYOfCube = 0

        # iterate through the whole coordinateSystem and draw a rectangle with a different color for every different number
        for i in range(len(self.playground.coordinateSystem)):

            for i2 in range(len(self.playground.coordinateSystem[i])):

                if self.playground.coordinateSystem[i][i2] != 0:
                    # draw cube with correct color
                    pygame.draw.rect(self.gameWindow,
                                     playerColors[
                                         self.playground.coordinateSystem[i][i2]],
                                     (currentXOfCube, currentYOfCube, widthOfCube, heightOfCube))

                currentXOfCube += widthOfCube

            currentXOfCube = 0
            currentYOfCube += heightOfCube

        pygame.display.flip()
