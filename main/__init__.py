import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime

import pygame
import websockets as websockets

from JsonInterpreter import JsonInterpreter
from game.Playground import Playground
from game.graphic.PlaygroundPresenter import PlaygroundPresenter
from game.player.DirectionOfLooking import DirectionOfLooking

sys.setrecursionlimit(1000000)

ONLINE = False


class Game(object):

    def __init__(self, docker=False, url="", key=""):
        self.ownPlayer = None
        self.URL = url
        self.KEY = key
        self.width = 0
        self.height = 0
        self.clock = pygame.time.Clock()
        self.interpreter = JsonInterpreter()
        self.playground = None
        self.playgroundPresenter = None
        self.printedStatistics = False
        if docker:
            os.environ["SDL_VIDEODRIVER"] = "dummy"

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

        print("Your are Player " + str(data[0]['you']))

    async def playOffline(self):
        with open('spe_ed-1603447830516.json') as f:
            data = json.load(f)

        self.width = data[0]['width']
        self.height = data[0]['height']

        self.printInfo(data)
        self.playground = Playground(self.interpreter.getCellsFromLoadedJson(data),
                                     self.interpreter.getPlayersFromLoadedJson(data))
        # Den eigenen Spieler heraussuchen
        self.ownPlayer = self.playground.players[int(data[0]['you']) - 1]
        self.playgroundPresenter = PlaygroundPresenter(self.playground, self.width, self.height)
        self.playgroundPresenter.generateGameField()
        running = True

        while running:
            self.clock.tick(60)

            # Benutzereingabe prüfen
            keys = pygame.key.get_pressed()
            if self.ownPlayer.active:
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.ownPlayer.turnDirectionOfLooking(DirectionOfLooking.UP)
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.ownPlayer.turnDirectionOfLooking(DirectionOfLooking.DOWN)
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.ownPlayer.turnDirectionOfLooking(DirectionOfLooking.LEFT)
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.ownPlayer.turnDirectionOfLooking(DirectionOfLooking.RIGHT)
                elif keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
                    print("Speed Up!")
                    self.ownPlayer.speedUp()
                elif keys[pygame.K_RCTRL] or keys[pygame.K_LCTRL]:
                    self.ownPlayer.speedDown()
            if keys[pygame.K_q]:
                pygame.quit()

            active = 0
            for player in self.playground.players:
                if player.active:
                    active += 1
                    player.tryToSurvive(self.playground)
                    # print("API-Zug: " + player.choosenTurn)
                    player.fitness += 1
            if active == 0 and not self.printedStatistics:
                self.printStatistics()
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

        logger = logging.getLogger('websockets')
        logger.setLevel(logging.ERROR)
        logger.addHandler(logging.StreamHandler())

        async with websockets.connect(f"{self.URL}?key={self.KEY}") as websocket:
            print("Mit Server verbunden. Warte in Lobby...Dies kann bis zu 5 Min. dauern!", flush=True)
            self.clock.tick(1000)
            while True:
                state_json = await websocket.recv()
                data = json.loads(state_json)
                data = [data]

                if self.playground is None:
                    self.width = data[0]['width']
                    self.height = data[0]['height']

                    self.printInfo(data)
                    self.playground = Playground(self.interpreter.getCellsFromLoadedJson(data),
                                                 self.interpreter.getPlayersFromLoadedJson(data))

                    # Den eigenen Spieler heraussuchen
                    self.ownPlayer = self.playground.players[int(data[0]['you']) - 1]
                else:
                    self.playground.update(self.interpreter.getCellsFromLoadedJson(data),
                                           self.interpreter.getPlayersFromLoadedJson(data))

                self.playgroundPresenter = PlaygroundPresenter(self.playground, self.width, self.height)
                self.playgroundPresenter.generateGameField()

                for player in self.playground.players:
                    if player.active:
                        player.fitness += 1

                if self.ownPlayer.active and data[0]['running']:
                    self.ownPlayer.tryToSurvive(self.playground)

                self.playground.addTurn()

                self.playgroundPresenter.update(self.playground)
                self.playgroundPresenter.updateGameField()

                action = self.ownPlayer.choosenTurn
                # print("API-Zug: " + action)
                # time.sleep(0.1)
                action_json = json.dumps({"action": action})
                await websocket.send(action_json)

    def saveImage(self, path):
        try:
            pygame.image.save(game.playgroundPresenter.gameWindow, path)
        except pygame.error:
            print("Konnte kein Bild speichern in \"" + path + "\"")

    def printStatistics(self):
        if self.playground is None or self.playground.players is None:
            print("Playground must not be None!")
            return
        # Sortiere die Spieler anhand Ihrer Fitness
        players = sorted(self.playground.players, key=lambda p: p.fitness, reverse=True)

        print("---------Spiel Vorbei---------")
        if self.ownPlayer.active:
            print("Wir haben gewonnen !!!     PS: Weil wir einfach Boss sind ;)")
            # Screenshot des Spielfeldes speichern
            self.saveImage("results/won/result_" + str(datetime.timestamp(datetime.now())) + ".jpg")
        elif self.ownPlayer.fitness == players[0].fitness:
            print("Unentschieden. Ihr deppen seid einfach ineinander gerasselt. Zwei Dumme, ein Gedanke...")
            # Screenshot des Spielfeldes speichern
            self.saveImage("results/draw/result_" + str(datetime.timestamp(datetime.now())) + ".jpg")
        else:
            print("Haben leider verloren... :/ Alles Hacker hier...")
            # Screenshot des Spielfeldes speichern
            self.saveImage("results/lost/result_" + str(datetime.timestamp(datetime.now())) + ".jpg")
        print("---------Statistiken---------")

        for player in players:
            print("Spieler " + str(player.id) + ": " + str(player.fitness) + " Status: " + str(
                "Lebend" if player.active else "Gestorben") + " Farbe: " + self.playgroundPresenter.getColorName(
                player.id) + ("  <---WIR" if self.ownPlayer.id == player.id else ""))
        print("-------------------------------")


def sleep(secs):
    for i in range(secs, 0, -1):
        if i <= 3 or i % 10 == 0:
            print("Warte " + str(i) + " Sekunden, bis zum erneuten Start!", flush=True)
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("---Programm wurde unterbrochen!---")


docker = os.environ["Docker"] == "True"
if ONLINE:
    url = os.environ["URL"]
    key = os.environ["KEY"]

    print("API-SERVER-URL: " + url)
    print("API-KEY: " + key)
    print("DOCKER: " + str(docker))

    while True:
        # TODO Auslagern in Parameterübergabe beim Programstart
        game = Game(docker, url, key)
        try:
            asyncio.get_event_loop().run_until_complete(game.playOnline())
        except websockets.InvalidStatusCode as e:
            if e.status_code == 429:
                print("Zu viele Anfragen in zu kurzer Zeit!")
                sleep(30)
            else:
                print(e)
        except websockets.ConnectionClosedOK as e:
            if e.code == 1000:
                print("Zeitüberschreitung bei Verbindungsaufbau!")
            print(e)
            sleep(5)
        except websockets.ConnectionClosedError as e:
            if e.code == 1006:
                game.printStatistics()
                sleep(5)
        except KeyboardInterrupt:
            print("\n---Programm wurde unterbrochen!---")
else:
    game = Game(docker)
    try:
        asyncio.get_event_loop().run_until_complete(game.playOffline())
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n---Programm wurde unterbrochen!---")
