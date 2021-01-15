import copy

import pygame

from game.Playground import Playground


class PlaygroundPresenter(object):
    # Defining Constants
    global playerColors, colorNames, blockwidth, py
    py = pygame
    blockwidth = 10
    # Defining PlayerColors
    playerColors = {
        -1: (255, 255, 255),  # Zwei Spieler auf gleicher koordinate
        0: (255, 255, 255),  # white / no player
        1: (153, 255, 51),  # Green
        2: (204, 0, 0),  # Red
        3: (0, 128, 255),  # Blue
        4: (255, 128, 51),  # Orange
        5: (255, 51, 153),  # Pink
        6: (129, 26, 232)  # Purple
    }
    colorNames = {
        -1: "White",
        0: "White",
        1: "Green",
        2: "Red",
        3: "Blue",
        4: "Orange",
        5: "Pink",
        6: "Purple"
    }

    def getColorName(self, id):
        """
        Returns the color of a player
        :param id: Player ID
        :return: colorname
        """
        return colorNames[id]

    def __init__(self, playground: Playground, width, height):
        self.playground = playground
        self.displayWidth = width * blockwidth
        self.displayHeight = height * blockwidth
        self.gameWindow = py.display.set_mode((self.displayWidth, self.displayHeight))

    def update(self, playground: Playground):
        """
        Updates the playground
        :param playground: the playground to update
        :return: the updated playground
        """
        self.playground = playground

    def getPlayground(self):
        """
        :returns the playground
        :return: playground
        """
        return self.playground

    def generateGameField(self):
        """
        Generates the game field
        :return: game field
        """
        self.updateGameField()

        # pygame.display.flip()

        # setting title and favicon
        py.display.set_caption("Spe_ed")
        py.display.set_icon(pygame.image.load("Lightning_McQueen.png"))

    def drawPath(self, path, player):
        """
        Draws the path of a player each round when a player moves
        :param path: previous path of a player
        :param playerid: id of the player
        """
        pathcoords = copy.deepcopy(path)
        if pathcoords is not None and len(pathcoords) >= 1:
            if pathcoords[0][0] != player.x or pathcoords[0][1] != player.y:
                pathcoords.insert(0, (player.x, player.y))
            if len(pathcoords) >= 2:
                for i in range(len(pathcoords)):
                    pathcoords[i] = [pathcoords[i][0] * blockwidth + (blockwidth / 2),
                                     pathcoords[i][1] * blockwidth + blockwidth / 2]
                py.draw.lines(self.gameWindow, playerColors[int(player.id)], False, pathcoords, width=3)

    def updateGameField(self):
        """
        Updates the game field by drawing rectangles in different colors for different players
        """
        # fill screen with a white blankspace
        self.gameWindow.fill((40, 40, 40))
        white = (255, 255, 255)

        x = 0
        y = 0
        for _ in range(int(self.displayWidth / blockwidth)):
            x += blockwidth
            pygame.draw.line(self.gameWindow, white, (x, 0), (x, self.displayHeight))

        for _ in range(int(self.displayHeight / blockwidth)):
            y += blockwidth
            py.draw.line(self.gameWindow, white, (0, y), (self.displayWidth, y))

        # Determine width and height of a cube
        widthOfCube = self.displayWidth / len(self.playground.coordinateSystem[0])
        heightOfCube = self.displayHeight / len(self.playground.coordinateSystem)
        currentXOfCube = 0
        currentYOfCube = 0

        # iterate through the whole coordinateSystem and draw a rectangle with a different color for every different
        # number
        for i in range(len(self.playground.coordinateSystem)):

            for i2 in range(len(self.playground.coordinateSystem[i])):

                if self.playground.coordinateSystem[i][i2] != 0:
                    # draw cube with correct color
                    py.draw.rect(self.gameWindow,
                                 playerColors[
                                     self.playground.coordinateSystem[i][i2]],
                                 (currentXOfCube, currentYOfCube, widthOfCube, heightOfCube))

                currentXOfCube += widthOfCube

            currentXOfCube = 0
            currentYOfCube += heightOfCube
        for player in self.playground.players:
            self.drawPath(player.path, player)

        py.display.flip()
