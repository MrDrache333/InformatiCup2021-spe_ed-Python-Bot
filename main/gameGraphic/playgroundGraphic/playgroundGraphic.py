import pygame

class Playfield(object):


    def __init__(self, pixelWidth, pixelHeight, rows, columns):
        self.pixelWidth = pixelWidth
        self.pixelHeight = pixelHeight
        self.rows = rows
        self.columns = columns


    def createGameWindow(self):
        """creates the internal pygame display"""
        pygame.display.set_mode((self.pixelWidth, self.pixelHeight))


    def drawGrid(self, surface):
        """Draws the lines representing the playfield"""
        spaceBetweenVerticalLines = self.pixelWidth // self.rows
        spaceBetweenHorizontaleLines = self.pixelHeight // self.columns

        #Draw horizontale lines
        x = 0
        for i in range(self.columns):
            x = x + spaceBetweenHorizontaleLines
            pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, self.pixelWidth))

        #Draws vertical lines
        y = 0
        for i in range(self.rows):
            y = y + spaceBetweenVerticalLines
            pygame.draw.line(surface, (255, 255, 255), (y, 0), (y, self.pixelHeight))
        pass

    def updateWindow(self, surface):
        """updates the playfield accordingly to (i dont know yet...)"""
        self.drawGrid(surface)-
        pygame.display.update()
        pass