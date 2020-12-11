import asyncio
import json

import pygame
import websockets as websockets

from JsonInterpreter import JsonInterpreter
from game.Playground import Playground
from game.graphic.PlaygroundPresenter import PlaygroundPresenter
# Play online via API-Key, or Offline
from game.player.DirectionOfLooking import DirectionOfLooking

ONLINE = False


class Game(object):

    def __init__(self, url, key):
        self.URL = url
        self.KEY = key
        self.width = 0
        self.height = 0
        self.clock = pygame.time.Clock()
        self.interpreter = JsonInterpreter()
        self.playground = None
        self.playgroundPresenter = None
        self.printedStatistics = False

    def printInfo(self, data):
        print("Playfield: " + str(self.width) + " x " + str(self.height))

        for p in data[0]['players']:
            if data[0]['players'][p]['active']:
                print("Player " + p + " is on [" + str(data[0]['players'][p]['x']) + "] [" + str(
                    data[0]['players'][p]['y']) + "], looking " + str(
                    data[0]['players'][p]['direction']) + " at speed " + str(
                    data[0]['players'][p]['speed']))
            else:
                print("Player " + p + " is out.")

        for c in data[0]['cells']:
            print(c)
        print("Your are Player " + str(data[0]['you']))

    async def playOffline(self):
        with open('spe_ed-1603447830516_1.json') as f:
            data = json.load(f)

        self.width = data[0]['width']
        self.height = data[0]['height']

        self.printInfo(data)

        self.playground = Playground(self.interpreter.getCellsFromLoadedJson(data),
                                     self.interpreter.getPlayersFromLoadedJson(data))
        self.playgroundPresenter = PlaygroundPresenter(self.playground, self.width, self.height)
        running = True

        # Den eigenen Spieler heraussuchen
        ownPlayer = None
        for player in self.playground.players:
            if player.id == data[0]['you']:
                ownPlayer = player
                break
        if ownPlayer is None:
            exit("Invalid Players")

        while running:
            # pygame.time.delay(500//60)
            self.clock.tick(30)
            # clock.tick(10000)

            # Benutzereingabe prüfen
            keys = pygame.key.get_pressed()
            if ownPlayer.active:
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
            if keys[pygame.K_q]:
                pygame.quit()

            active = 0
            for player in self.playground.players:
                if player.active:
                    active += 1
                    player.tryToSurvive(self.playgroundPresenter)
                    print("API-Zug: " + player.choosenTurn)
                    player.fitness += 1
            if active == 0 and not self.printedStatistics:
                print("--- Statistiken ---")
                for player in self.playground.players:
                    print("Spieler " + str(player.id) + ": " + str(player.fitness))
                    self.printedStatistics = True
            else:
                for player in self.playground.players:
                    self.playground.movePlayer(player.id - 1)
                self.playgroundPresenter.playground = self.playground
                self.playground.addTurn()
                self.playgroundPresenter.updateGameField()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

    async def playOnline(self):

        async with websockets.connect(f"{self.URL}?key={self.KEY}") as websocket:
            print("Waiting for initial state...", flush=True)

        while True:
            state_json = await websocket.recv()
            data = json.loads(state_json)

            self.width = data[0]['width']
            self.height = data[0]['height']

            self.printInfo(data)

            self.interpreter = JsonInterpreter()
            self.playground = Playground(self.interpreter.getCellsFromLoadedJson(data),
                                         self.interpreter.getPlayersFromLoadedJson(data))
            self.playgroundPresenter = PlaygroundPresenter(self.playground, self.width, self.height)
            self.clock = pygame.time.Clock()
            running = True

            # Den eigenen Spieler heraussuchen
            ownPlayer = None
            for player in self.playground.players:
                if player.id == data[0]['you']:
                    ownPlayer = player
                    break
            if ownPlayer is None:
                exit("Invalid Players")

            active = 0
            for player in self.playground.players:
                if player.active:
                    active += 1
                    player.fitness += 1

            if ownPlayer.active and data[0]['active']:
                ownPlayer.tryToSurvive(self.playgroundPresenter)

            if active == 0 and not self.printedStatistics:
                print("--- Statistiken ---")
                for player in self.playground.players:
                    print("Spieler " + str(player.id) + ": " + str(player.fitness))
                    self.printedStatistics = True
            else:
                self.playground.addTurn()
                self.playgroundPresenter.playground = self.playground
                self.playgroundPresenter.updateGameField()

            action = ownPlayer.choosenTurn
            print("API-Zug: " + action)
            action_json = json.dumps({"action": action})
            await websocket.send(action_json)


# TODO Auslagern in Parameterübergabe beim Programstart
game = Game("wss://msoll.de/spe_ed", "72ILGT3YVIW5DV2UR3L5E6VCMFB6TJPR6LAX2ZLGMYGRQSVTW2C4G4E2")


def getPlaygroundPresenter():
    return game.playgroundPresenter


if ONLINE:
    asyncio.get_event_loop().run_until_complete(game.playOnline())
else:
    asyncio.get_event_loop().run_until_complete(game.playOffline())
