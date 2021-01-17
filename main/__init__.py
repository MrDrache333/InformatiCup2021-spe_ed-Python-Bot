import asyncio
import copy
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

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

sys.setrecursionlimit(1000000)


def createFolderIfNotExist(path):
    path = path[0: path.rindex('/')]
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
            return True
        except Exception:
            logger.error("Could not create Folder \"" + path + "\"")
            return False
    return False


def saveGameFieldBeforeDeath(path, json):
    """
    Saves the current Gamefield as a file to debug them later
    :param json: The JSON String to store
    :param path: The path where to store the file
    :return: Nothing
    """
    if json is None:
        logger.info("JOSN is None: No GameField JSon will be stored.")
        return
    try:
        created = createFolderIfNotExist(path)
        if created:
            with open(path, "w") as text_file:
                n = text_file.write("[" + json + "]")
            if n != len(json):
                logger.info("Could not completely write GameField in \"" + path + "\"")
                return False
            else:
                return True
        else:
            return False
    except Exception:
        logger.info("Could not store GameField in \"" + path + "\"")


def saveImage(path):
    """
    Saves an image of the game after a win/draw/loose
    :param path: path to the save location
    """
    try:
        if createFolderIfNotExist(path):
            pygame.image.save(game.playgroundPresenter.gameWindow, path)
    except pygame.error:
        logger.info("Can't store image at \"" + path + "\"")


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
        self.gameStartTime = 0
        self.oldData = None
        self.oldStateJson = None
        if docker:
            os.environ["SDL_VIDEODRIVER"] = "dummy"

    def printInfo(self, data):
        """
        Prints the converted json data
        :param data: data loaded out of json
        """
        logger.info("Playfield: " + str(self.width) + " x " + str(self.height))

        for p in data[0]['players']:
            if data[0]['players'][p]['active']:
                logger.info("Player " + p + " is on [" + str(data[0]['players'][p]['x']) + "] [" + str(
                    data[0]['players'][p]['y']) + "], looking " + str(
                    data[0]['players'][p]['direction']) + " at speed " + str(
                    data[0]['players'][p]['speed']))
            else:
                logger.info("Player " + p + " is out.")

        logger.info("Your are Player " + str(data[0]['you']))

    async def playOffline(self, PlaygroundPath):
        """
        Run the simulation offline with x players with the same strategy
        :param PlaygroundPath: Path to the playground json file
        """
        with open(PlaygroundPath) as f:
            data = json.load(f)

        self.width = data[0]['width']
        self.height = data[0]['height']

        self.playground = Playground(self.interpreter.getCellsFromLoadedJson(data),
                                     self.interpreter.getPlayersFromLoadedJson(data))
        # Den eigenen Spieler heraussuchen
        self.ownPlayer = self.playground.players[int(data[0]['you']) - 1]
        self.playgroundPresenter = PlaygroundPresenter(self.playground, self.width, self.height)
        self.playgroundPresenter.generateGameField()
        running = True
        self.printInfo(data)
        self.gameStartTime = time.time()
        while running:
            self.clock.tick(20)

            # Check if pressed Key to interrupt
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                pygame.quit()

            active = 0
            for player in self.playground.players:
                if player.active:
                    active += 1
                    logger.info("Player " + str(player.id))
                    player.tryToSurvive(self.playground)
                    logger.info("Turn: " + player.choosenTurn)
                    logger.info("Chosen by " + player.turnSetFrom)
                    logger.info("")
                    player.fitness += 1
            if active == 0 and not self.printedStatistics:
                self.printStatistics()
                self.printedStatistics = True
            else:
                self.playground.movePlayer()
                self.playgroundPresenter.playground = self.playground
                self.playground.addTurn()
                self.playgroundPresenter.updateGameField()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

    async def playOnline(self):
        """
        Run the simulation offline with x players with the same strategy
        """
        wslogger = logging.getLogger('websockets')
        wslogger.setLevel(logging.ERROR)
        wslogger.addHandler(logging.StreamHandler())

        # Wait for the Client to connect to server
        async with websockets.connect(f"{self.URL}?key={self.KEY}") as websocket:
            logger.info("Connected to server. Waiting in lobby...This can take up to 5 min.!")
            self.clock.tick(1000)
            while True:
                # Wait for the servers response
                state_json = await websocket.recv()
                if self.gameStartTime == 0:
                    self.gameStartTime = time.time()
                # Store the current time to calculate the time needed for a turn
                startTime = time.time_ns()
                data = json.loads(state_json)
                data = [data]

                # If game was just created, create needed objects too
                if self.playground is None:
                    self.width = data[0]['width']
                    self.height = data[0]['height']

                    self.printInfo(data)
                    self.playground = Playground(self.interpreter.getCellsFromLoadedJson(data),
                                                 self.interpreter.getPlayersFromLoadedJson(data))

                    # Get own player out of the Data
                    self.ownPlayer = self.playground.players[int(data[0]['you']) - 1]
                else:
                    self.playground.update(self.interpreter.getCellsFromLoadedJson(data),
                                           self.interpreter.getPlayersFromLoadedJson(data))

                self.playgroundPresenter = PlaygroundPresenter(self.playground, self.width, self.height)
                self.playgroundPresenter.generateGameField()

                for player in self.playground.players:
                    if player.active:
                        player.fitness += 1

                # Compare if a player died from last round
                if self.oldData is not None:
                    for player in self.oldData:
                        if player.active != self.playground.players[player.id - 1].active:
                            logger.info("The Player " + str(player.id) + "[" + self.playgroundPresenter.getColorName(
                                player.id) + "]" + " died!" + (" <-- WE" if self.ownPlayer.id == player.id else ""))
                            logger.info("")

                # If our player is active and the game is running, try to Survive
                if self.ownPlayer.active and data[0]['running']:
                    self.ownPlayer.tryToSurvive(self.playground)
                    logger.info("Turn: " + self.ownPlayer.choosenTurn)
                    logger.info("Chosen by " + self.ownPlayer.turnSetFrom)

                self.playground.addTurn()

                self.playgroundPresenter.update(self.playground)
                self.playgroundPresenter.updateGameField()

                self.oldData = copy.deepcopy(self.playground.players)
                # If game is running an we're still active, print out our Turn, duration and send choosen turn to server
                if self.ownPlayer.active and data[0]['running']:
                    action = self.ownPlayer.choosenTurn
                    action_json = json.dumps({"action": action})
                    logger.info("Our turn took " + str((time.time_ns() - startTime) // 1000000) + " milliseconds!")
                    logger.info("")
                    await websocket.send(action_json)
                    self.oldStateJson = copy.deepcopy(state_json)
                else:
                    return

    def printStatistics(self):
        """
        Prints statistics of the played game
        How long did it take, who won?
        """
        if self.playground is None or self.playground.players is None:
            logger.info("Playground must not be None!")
            return
        # Sort playes based on their fitness value
        players = sorted(self.playground.players, key=lambda p: p.fitness, reverse=True)

        logger.info("---------Game OVER---------")
        logger.info("The game lasts " + str(round(time.time() - game.gameStartTime, 1)) + " Seconds!")
        logger.info("Average turntime was about " + str(
            round(float((time.time() - game.gameStartTime) / players[0].fitness), 2)) + " Seconds")
        if self.ownPlayer.active:
            logger.info("WE WON !!!     PS: Because we can ;)")
            # Store Scrrenshot of the Gamefield
            saveImage("results/won/result_" + str(datetime.timestamp(datetime.now())) + ".jpg")
        elif self.ownPlayer.fitness == players[0].fitness:
            logger.info("It's a draw. Your tried your best...but hey...he died too")
            # Store Scrrenshot of the Gamefield
            saveImage("results/draw/result_" + str(datetime.timestamp(datetime.now())) + ".jpg")
            saveGameFieldBeforeDeath("results/draw/result_" + str(datetime.timestamp(datetime.now())) + ".json",
                                     self.oldStateJson)
        else:
            logger.info("We lost... :/ Maybe they're hacking...")
            # Store Scrrenshot of the Gamefield
            saveImage("results/lost/result_" + str(datetime.timestamp(datetime.now())) + ".jpg")
            saveGameFieldBeforeDeath("results/lost/result_" + str(datetime.timestamp(datetime.now())) + ".json",
                                     self.oldStateJson)
        logger.info("---------Stats---------")

        for player in players:
            logger.info("Player " + str(player.id) + ": " + str(player.fitness) + " State: " + str(
                "ALIVE" if player.active else "DEAD") + " Color: " + self.playgroundPresenter.getColorName(
                player.id)
                        + ("  <---WE" if self.ownPlayer.id == player.id else ""))
        logger.info("-------------------------------")


def sleep(secs):
    """
    Wait for x seconds
    :param secs: seconds
    """
    for i in range(secs, 0, -1):
        if i <= 3 or i % 10 == 0:
            logger.info("WAIT " + str(i) + " SECONDS TO START AGAIN!")
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("---PROGRAM INTERRUPTED!---")
            exit()


docker = False
ONLINE = True
OfflinePath = ""
url = ""
key = ""
try:
    ONLINE = os.environ["Online"] == "True"
except KeyError:
    logger.info("Online Parameter is not set. DEFAULT=True")

if not ONLINE:
    try:
        OfflinePath = os.environ["Playground"]
    except KeyError:
        logger.info("Playground Parameter is not set but Online was set to FALSE")
        logger.info("Please set the needed environment variables. Please take a look at our "
                    "documentation to ensure the proper use of our program")
        exit(-1)
else:
    try:
        url = os.environ["URL"]
        key = os.environ["KEY"]
    except KeyError:
        logger.info("URL or KEY Parameter is not set but Online was set to TRUE")
        logger.info("Please set the needed environment variables. Please take a look at our "
                    "documentation to ensure the proper use of our program")
        exit(-1)
try:
    docker = os.environ["Docker"] == "True"
except KeyError:
    logger.info("Docker Parameter is not set. DEFAULT=FALSE")

if ONLINE:

    logger.info("API-SERVER-URL: " + url)
    logger.info("API-KEY: " + key)
    logger.info("DOCKER: " + str(docker))

    while True:
        game = Game(docker, url, key)
        try:
            asyncio.get_event_loop().run_until_complete(game.playOnline())
            game.printStatistics()
            sleep(5)
        except websockets.InvalidStatusCode as e:
            if e.status_code == 429:
                logger.info("TOO MANY REQUESTS")
                sleep(30)
            else:
                logger.debug(e)
        except websockets.ConnectionClosedOK as e:
            if e.code == 1000:
                logger.debug("Server Closed with Code: 1000 OK")
                game.printStatistics()
                sleep(5)
        except websockets.ConnectionClosedError as e:
            if e.code == 1006:
                logger.debug("Server Closed with Code: 1006 ERROR")
                game.printStatistics()
                sleep(5)
        except KeyboardInterrupt:
            logger.info("\n---Programm wurde unterbrochen!---")
            exit()
else:
    game = Game(docker)
    try:
        asyncio.get_event_loop().run_until_complete(game.playOffline(OfflinePath))
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n---Programm wurde unterbrochen!---")
