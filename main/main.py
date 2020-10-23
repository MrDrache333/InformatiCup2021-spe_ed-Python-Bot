# Snake Tutorial Python

import random

import pygame

from main.gameGraphic.playgroundGraphic import playgroundGraphic


def createRandomColor():
    """Creates a random RGB (int, int int) color"""
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def createRandomPosition(rows: int, column: int):
    """Creates a random Position in within the given :param rows and :param column and returns it as (int, int)"""
    x = random.randrange(rows)
    y = random.randrange(column)
    return x, y


def main():
    global pixelWidth, pixelHeight, rows, columns

    pixelWidth = 500
    pixelHeight = 500

    rows = 20  # int(input("Anzahl der Zeilen eingeben: "))
    columns = 30  # int(input("Anzahl der Spalten eingeben: "))

    playfield = playgroundGraphic.Playfield(pixelWidth, pixelHeight, rows, columns)

    playfield.updateWindow()

    pygame.time.delay(10000)

    pass


main()
