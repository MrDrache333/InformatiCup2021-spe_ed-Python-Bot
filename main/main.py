# Snake Tutorial Python

import random
import pygame
import tkinter as tk
from tkinter import messagebox
import gameGraphic.playerGraphic.snake as snake


def redrawWindow(surface):
    global rows, width, players, snack
    surface.fill((0, 0, 0))
    for player in players:
        player.draw(surface)
        pass
    #player1.draw(surface)
    #snack.draw(surface)
    drawGrid(width, rows, surface)
    pygame.display.update()


def randomSnack(rows, item):
    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
            continue
        else:
            break

    return (x, y)


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
    global width, rows, players, player1, player2, player3, player4, snack
    width = 500
    rows = 20
    players = []

    for i in range(4):
        player = snake.snake(createRandomColor(), createRandomPosition(rows, rows))
        players.append(player)
        pass

    win = pygame.display.set_mode((width, width))

    flag = True

    clock = pygame.time.Clock()

    while flag:
        pygame.time.delay(50)
        clock.tick(10)
        #player1.move()
        #if player1.body[0].pos == snack.pos:
         #   player1.addCube()
          #  snack = cube(randomSnack(rows, player1), color=(0, 255, 0))

        """for x in range(len(player1.body)):
            if player1.body[x].pos in list(map(lambda z: z.pos, player1.body[x + 1:])):
                print('Score: ', len(player1.body))
                message_box('You Lost!', 'Play again...')
                player1.reset((10, 10))
                break
"""
        redrawWindow(win)

    pass


main()