import json

import pygame


from game.Playground import Playground
from game.graphic.PlaygroundPresenter import PlaygroundPresenter
from game.player.DirectionOfLooking import DirectionOfLooking
from JsonInterpreter import JsonInterpreter

with open('spe_ed-10x15.json') as f:
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
playgroundPresenter = PlaygroundPresenter(playground, width, height)
clock = pygame.time.Clock()
running = True

# Den eigenen Spieler heraussuchen
ownPlayer = None
for player in playground.players:
    if player.id == '1':
        ownPlayer = player
        break
if ownPlayer is None:
    exit("Invalid Players")

while running:
    # pygame.time.delay(500//60)
    # clock.tick(1000 // 800)
    clock.tick(1000 // 400)

    # Benutzereingabe prüfen
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        ownPlayer.turnDirectionOfLooking(DirectionOfLooking.UP)
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        ownPlayer.turnDirectionOfLooking(DirectionOfLooking.DOWN)
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        ownPlayer.turnDirectionOfLooking(DirectionOfLooking.LEFT)
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ownPlayer.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
    elif keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
        print("Speed Up!")
        ownPlayer.speedUp()
    elif keys[pygame.K_RCTRL] or keys[pygame.K_LCTRL]:
        ownPlayer.speedDown()
    elif keys[pygame.K_q]:
        pygame.quit()

    for player in playground.players:
        player.tryToSurvive(playground)
    # ownPlayer.tryToSurvive(playground)

    playground.movePlayer()
    playgroundPresenter.playground = playground
    playgroundPresenter.updateGameField()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
