# Snake Tutorial Python

import random
import pygame
import tkinter as tk
from tkinter import messagebox
from win32api import GetSystemMetrics
from gameGraphic.playgroundGraphic import playgroundGraphic


def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass


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

    pixelWidth = GetSystemMetrics(0)//2
    pixelHeight = GetSystemMetrics(1)//2

    rows = 10#int(input("Anzahl der Zeilen eingeben: "))
    columns = 14#int(input("Anzahl der Spalten eingeben: "))

    playfield = playgroundGraphic.Playfield(pixelWidth, pixelHeight, rows, columns)

    playfield.updateWindow()

    pygame.time.delay(5000)





   # flag = True
#
 #   clock = pygame.time.Clock()
#
 #   while flag:
  #      pygame.time.delay(50)
   #     clock.tick(10)
    #    #player1.move()
     #   #if player1.body[0].pos == snack.pos:
      #   #   player1.addCube()
       #   #  snack = cube(randomSnack(rows, player1), color=(0, 255, 0))
#
 #       for x in range(len(player1.body)):
  #          if player1.body[x].pos in list(map(lambda z: z.pos, player1.body[x + 1:])):
   #             print('Score: ', len(player1.body))
    #            message_box('You Lost!', 'Play again...')
     #           player1.reset((10, 10))
      #          break


    pass


main()