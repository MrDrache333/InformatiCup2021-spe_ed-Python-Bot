import json

import pygame

from game.Playground import Playground
from game.graphic.PlaygroundPresenter import PlaygroundPresenter
from networking.json.JsonInterpreter import JsonInterpreter

with open('spe_ed-1603447830516.json') as f:
    data = json.load(f)

width = data[0]['width']
height = data[0]['height']

print("Playfield: " + str(width) + " x " + str(height))

for p in data[0]['players']:
    if data[0]['players'][p]['active']:
        print("Player " + p + " is on [" + str(data[0]['players'][p]['x']) + "] [" + str(
            data[0]['players'][p]['y']) + "], looking " + str(data[0]['players'][p]['direction']) + " at speed " + str(
            data[0]['players'][p]['speed']))
    else:
        print("Player " + p + " is out.")

for c in data[0]['cells']:
    print(c)

interpreter = JsonInterpreter()
playground = Playground(interpreter.getCellsFromLoadedJson(data), interpreter.getPlayersFromLoadedJson(data))
playgroundPresenter = PlaygroundPresenter(playground)
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(20)
    playground.movePlayer()
    playgroundPresenter.playground = playground
    playgroundPresenter.updateGameField()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
