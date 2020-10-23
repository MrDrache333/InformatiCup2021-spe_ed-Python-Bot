import pygame

class cube(object):
    rows = 20
    pixelWidth = 500

    def __init__(self, start, color : (int, int, int), dirnx=1, dirny=0):
        self.pos = start
        self.color = color
        self.dirnx = 1
        self.dirny = 0

    def move(self, dirnx, dirny):
        """Moves the Cube accordingly to dirnx and dirny"""
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        CubeSideLength = self.pixelWidth // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i * CubeSideLength + 1, j * CubeSideLength + 1, CubeSideLength - 2, CubeSideLength - 2))
        if eyes:
            centre = CubeSideLength // 2
            radius = 3
            circleMiddle = (i * CubeSideLength + centre - radius, j * CubeSideLength + 8)
            circleMiddle2 = (i * CubeSideLength + CubeSideLength - radius * 2, j * CubeSideLength + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)