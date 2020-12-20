import copy


def generateFreePlaceMap(coordinatesystem):
    """
    Generiert eine Karte, die alle verbundenen freien Pixel in Areale einteilt
    :param coordinatesystem: Das Koordinatensystem des Spiels
    :return: Die erstelle Karte mit markierten Arealen
    """
    # Wenn das Koordinatensystem ungültig ist
    if coordinatesystem is None or len(coordinatesystem) <= 1 or len(coordinatesystem[0]) <= 1:
        return
    count = 1
    freePlaceMap = copy.deepcopy(coordinatesystem)
    for y in range(len(coordinatesystem)):
        for x in range(len(coordinatesystem[0])):
            if coordinatesystem[y][x] != 0:
                freePlaceMap[y][x] = -1
    for y in range(len(coordinatesystem)):
        for x in range(len(coordinatesystem[0])):
            if freePlaceMap[y][x] == 0:
                freePlaceMap[y][x] = count
                stack = []
                stack.extend(replaceAdjacent_cells(freePlaceMap, x, y, count))
                while len(stack) > 0:
                    coord = stack.pop()
                    stack.extend(replaceAdjacent_cells(freePlaceMap, coord[0], coord[1], count))
                count += 1
    return freePlaceMap


def convertFindFurthestFieldMapToFreePlaceFormat(inputMap):
    outputMap = copy.deepcopy(inputMap)
    for y in range(len(outputMap)):
        for x in range(len(outputMap[0])):
            outputMap[y][x] = -1 if outputMap[y][x] < 10 else outputMap[y][x] - 10
    return outputMap


def findNearestCoordinateOnFurthestFieldMap(freeMap, moveMap, maxFreePlaceIndex, speed, ownx, owny):
    minimalValue = None
    minimalCoord = None

    for y in range(len(freeMap)):
        for x in range(len(freeMap[0])):
            if freeMap[y][x] == maxFreePlaceIndex:
                if moveMap[y][x] != -1:
                    # check if pos is reachable
                    if not (x % speed != ownx % speed) or (y % speed != owny % speed):
                        if minimalValue is None or moveMap[y][x] < minimalValue:
                            minimalValue = moveMap[y][x]
                            minimalCoord = (x, y)

    if minimalValue is not None:
        return minimalCoord
    else:
        return None


def replaceAdjacent_cells(freePlaceMap, x, y, count):
    """
    Checks every Cell surrounded by the current Cell if its free and has no Value.
    Then the Current count will be the new Value and this new Cell will be Added to the List to be checked

    :param freePlaceMap: The Current FreePlaceMap
    :param x: The Current X Coordinate to check the Neighbours of
    :param y: The Current Y Coordinate to check the Neighbours of
    :param count: The Current Area-Index
    :return: The List with every valid Neighbour
    """
    list = []
    if freePlaceMap is None or len(freePlaceMap) <= 1 or len(freePlaceMap[0]) <= 1:
        return
    # Check Left Cell
    if x > 0 and freePlaceMap[y][x - 1] != -1 and freePlaceMap[y][x - 1] != count:
        freePlaceMap[y][x - 1] = count
        list.append((x - 1, y))
    # Check Right Cell
    if x < len(freePlaceMap[0]) - 1 and freePlaceMap[y][x + 1] != -1 and freePlaceMap[y][x + 1] != count:
        freePlaceMap[y][x + 1] = count
        list.append((x + 1, y))
    # Check Cell Underneath
    if y > 0 and freePlaceMap[y - 1][x] != -1 and freePlaceMap[y - 1][x] < count:
        freePlaceMap[y - 1][x] = count
        list.append((x, y - 1))
    # Check Upper Cell
    if y < len(freePlaceMap) - 1 and freePlaceMap[y + 1][x] != -1 and freePlaceMap[y + 1][x] != count:
        freePlaceMap[y + 1][x] = count
        list.append((x, y + 1))
    return list


def getFreePlaceIndexForCoordinate(freePlaceMap, x, y):
    """
    Returns the Index in the FreePlaceValueArray in witch the given Coordinate is in
    :param freePlaceMap: The FreePlaceMap to check on
    :param x: The X Coordinate to Check for
    :param y: The Y Coordinate to Check for
    :return: The found Index or None if not Found
    """
    if freePlaceMap is None or len(freePlaceMap) < y or len(freePlaceMap[0]) < x or x < 0 or y < 0:
        return None
    # Check current Cell
    if freePlaceMap[y][x] != -1:
        return freePlaceMap[y][x] - 1
    # Check Left Cell
    elif x > 0 and freePlaceMap[y][x - 1] != -1:
        return freePlaceMap[y][x - 1] - 1
    # Check Right Cell
    elif x < len(freePlaceMap[0]) - 1 and freePlaceMap[y][x + 1] != -1:
        return freePlaceMap[y][x + 1] - 1
    # Check Cell Underneath
    elif y > 0 and freePlaceMap[y - 1][x] != -1:
        return freePlaceMap[y - 1][x] - 1
    # Check Upper Cell
    elif y < len(freePlaceMap) - 1 and freePlaceMap[y + 1][x] != -1:
        return freePlaceMap[y + 1][x] - 1
    return None


def getFreePlaceValues(freePlaceMap):
    if freePlaceMap is None or len(freePlaceMap) <= 1 or len(freePlaceMap[0]) <= 1:
        return
    values = []
    for y in range(len(freePlaceMap)):
        for x in range(len(freePlaceMap[0])):
            pointValue = freePlaceMap[y][x]
            if pointValue != -1:
                if len(values) >= pointValue:
                    values[pointValue - 1] += 1
                else:
                    values.append(1)
    return values
