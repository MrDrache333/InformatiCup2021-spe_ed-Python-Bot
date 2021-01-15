from game.player.Player import Player


class JsonInterpreter(object):

    def __init__(self):
        pass

    def getCellsFromLoadedJson(self, file):
        """
        Returns all cells from json file
        :param file: json file
        :return: cells
        """
        return file[0]['cells']

    def getPlayersFromLoadedJson(self, file):
        """
        Returns all player from json file
        :param file: json file
        :return: players
        """
        players = []

        for p in file[0]['players']:
            players.append(Player(int(p),  # player ID
                                  file[0]['players'][p]['x'],  # player X coordinate
                                  file[0]['players'][p]['y'],  # player Y coordinate
                                  file[0]['players'][p]['direction'],  # player moving direction
                                  file[0]['players'][p]['active'],  # whether player is alive
                                  file[0]['players'][p]['speed']))  # speed of player
        return players
