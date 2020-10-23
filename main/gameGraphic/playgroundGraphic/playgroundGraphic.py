import pygame


class Playfield(object):

    def __init__(self, pixelWidth: int, pixelHeight: int, rows: int, columns: int):
        """Initilizes the Playfield while creating a pygame display"""
        self.pixelWidth = pixelWidth
        self.pixelHeight = pixelHeight
        self.rows = rows
        self.columns = columns
        self.surface = pygame.display.set_mode((self.pixelWidth, self.pixelHeight))

    def drawGrid(self):
        """Draws the lines representing the playfield"""
        spaceBetweenVerticalLines = self.pixelWidth // self.columns
        spaceBetweenHorizontalLines = self.pixelHeight // self.rows

        # Draw horizontal lines
        x = 0
        for i in range(self.rows+1):
            pygame.draw.line(self.surface, (255, 255, 255), (0, x), (self.pixelWidth, x))
            x = x + spaceBetweenHorizontalLines

        # Draws vertical lines
        y = 0
        for i in range(self.columns+1):
            pygame.draw.line(self.surface, (255, 255, 255), (y, 0), (y, self.pixelHeight))
            y = y + spaceBetweenVerticalLines

    def updateWindow(self):
        """updates the playfield accordingly to (i dont know yet...)"""
        self.surface.fill((0, 0, 0))
        self.drawGrid()
        pygame.display.update()
