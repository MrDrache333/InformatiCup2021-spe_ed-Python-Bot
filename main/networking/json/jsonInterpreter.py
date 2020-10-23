from main.game.player.player import Player


class JsonInterpreter(object):

    def __init__(self, file):
        self.file = file

    def getCells(self, file):
        pass


def getPlayersFromLoadedJson(file):
    players = []

    for p in file[0]['players']:
        players.append(Player(p,  # player ID
                              file[0]['players'][p]['x'],  # player X coordinate
                              file[0]['players'][p]['y'],  # player Y coordinate
                              file[0]['players'][p]['direction'],  # player moving direction
                              file[0]['players'][p]['active'],  # whether player is alive
                              file[0]['players'][p]['speed']))  # speed of player
    return players


def getCellsFromLoadedJson(file):
    return file[0]['cells']
