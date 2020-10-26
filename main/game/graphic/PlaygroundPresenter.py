import pygame

from game.Playground import Playground


class PlaygroundPresenter(object):

    def __init__(self, playground: Playground):
        self.playground = playground
        pygame.init()

    def updateGameField(self):
        pass