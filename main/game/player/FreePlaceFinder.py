import copy


def generateFreePlaceMap(coordinatesystem):
    """
    Generates a Map, were every free Area is marked with an Index starting by 1
    :param coordinatesystem: The Coordinate System of the Playground
    :return: The Map with marked Areas
    """
    # Return, if the CoordinateSystem is not valid
    if coordinatesystem is None or len(coordinatesystem) <= 1 or len(coordinatesystem[0]) <= 1:
        return
    count = 1
    freePlaceMap = copy.deepcopy(coordinatesystem)
    # Iterate over the Map and
    for y in range(len(coordinatesystem)):
        for x in range(len(coordinatesystem[0])):
            if coordinatesystem[y][x] != 0:
                freePlaceMap[y][x] = -1
    for y in range(len(coordinatesystem)):
        for x in range(len(coordinatesystem[0])):
            if freePlaceMap[y][x] == 0:
                freePlaceMap[y][x] = count
                stack = list(replaceAdjacent_cells(freePlaceMap, x, y, count))
                while stack:
                    coord = stack.pop()
                    stack.extend(replaceAdjacent_cells(freePlaceMap, coord[0], coord[1], count))
                count += 1
    return freePlaceMap


def convertFindFurthestFieldMapToFreePlaceFormat(inputMap):
    """
    Converts map into a type for an other function to use it
    :param inputMap: tempCS from findFurthestField
    :return: converted map
    """
    outputMap = copy.deepcopy(inputMap)
    for y in range(len(outputMap)):
        for x in range(len(outputMap[0])):
            outputMap[y][x] = -1 if outputMap[y][x] < 10 else outputMap[y][x] - 10
    return outputMap


def findNearestCoordinateOnFurthestFieldMap(freeMap, moveMap, maxFreePlaceIndex, speed, ownx, owny):
    """
    Finds the nearest reachable coordinate in the next bigger area
    :param freeMap: Map with free places/areas
    :param moveMap: Map with maximum moves from players current position
    :param maxFreePlaceIndex: How many areas exist
    :param speed: speed of the player
    :param ownx: x position of the player
    :param owny: y position of the player
    :return: nearest minimal coordinate
    """
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


def getRelativeFreePlaceIndexForCoordinate(freePlaceMap, x, y):
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


def getExactFreePlaceIndexForCoordinate(freePlaceMap, x, y):
    """
    Returns the Exact Value for a given Coordinate on the FreePlaceMap
    :param freePlaceMap: The generated FreePlaceMap
    :param x: The X Coordinate on the FreePlaceMap
    :param y: The Y Coordinate on the FreePlaceMap
    :return: The Indexvalue on the FreePlaceMap
    """
    if freePlaceMap is None or len(freePlaceMap) <= y or len(freePlaceMap[0]) <= x or x < 0 or y < 0:
        return None
    if freePlaceMap[y][x] != -1:
        return freePlaceMap[y][x] - 1
    return None


def getAmountOfFreePlacesForCoordinate(freePlaceMap, x, y, freePlaceValues=None):
    """
    Returns the Amount of free Places for a given Coordinate
    :param freePlaceMap:
    :param x: The X Coordinate on the FreePlaceMap
    :param y: The Y Coordinate on the FreePlaceMap
    :param freePlaceValues: Optional the FreePlaceValues for the Map. If nt set, the Method will calculate there Values on its own
    :return: The Amount of free Places
    """
    # If no FreePlaceValues are given -> Calculate them first
    if freePlaceValues is None:
        freePlaceValues = getFreePlaceValues(freePlaceMap)
    # Get the Area-Index for a given Coordinate
    freePlaceIndex = getExactFreePlaceIndexForCoordinate(freePlaceMap, x, y)
    # Return 0, if no Index was given or the Index is not Valid. Else return the Value on the Index Position
    if freePlaceIndex is None or freePlaceIndex >= len(freePlaceValues):
        return 0
    return freePlaceValues[freePlaceIndex]


def getFreePlaceValues(freePlaceMap):
    """
    Returns the Amount of Free Places for every Area Marked on the FreePlaceMap
    by iterating over the Map and counting each Cell of each Area together
    The Returned list starts with Area 1 on Index 0
    :param freePlaceMap: The generated FreePlaceMap
    :return: The Amounts of free Places for each Area on the FreePlaceMap
    """
    if freePlaceMap is None or len(freePlaceMap) <= 1 or len(freePlaceMap[0]) <= 1:
        return
    values = []
    # Iterate over the Map
    for y in range(len(freePlaceMap)):
        for x in range(len(freePlaceMap[0])):
            pointValue = freePlaceMap[y][x]
            if pointValue != -1:
                # Add one to the Area-Counter
                if len(values) >= pointValue:
                    values[pointValue - 1] += 1
                else:
                    values.append(1)
    return values


def getBiggestArea(freePlaceValues, place=1):
    """
    Returns the biggest requested area from the freeMap.
    If place is 1, the biggest will be returned
    If place is 2, the second biggest will be returned
    Etc
    :param freePlaceValues: Whole map with free places
    :param place: x biggest area (1./2./3./...)
    :return: index of the biggest area
    """
    if freePlaceValues is None or len(freePlaceValues) > place <= 0:
        return
    maximum = max(freePlaceValues)
    newIndex = freePlaceValues.index(maximum)
    for _ in range(1, place):
        currentMax = 0
        for value in freePlaceValues:
            if maximum > value > currentMax:
                currentMax = value
                newIndex = freePlaceValues.index(value)
        maximum = currentMax
    return newIndex
