import copy

def generateFreePlaceMap(coordinatesystem):
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
                replaceAdjacent_cells(freePlaceMap, x, y, count)
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
    if freePlaceMap is None or len(freePlaceMap) <= 1 or len(freePlaceMap[0]) <= 1:
        return
    if x > 0 and freePlaceMap[y][x - 1] != -1 and freePlaceMap[y][x - 1] != count:
        freePlaceMap[y][x - 1] = count
        replaceAdjacent_cells(freePlaceMap, x - 1, y, count)
    if x < len(freePlaceMap[0]) - 1 and freePlaceMap[y][x + 1] != -1 and freePlaceMap[y][x + 1] != count:
        freePlaceMap[y][x + 1] = count
        replaceAdjacent_cells(freePlaceMap, x + 1, y, count)
    if y > 0 and freePlaceMap[y - 1][x] != -1 and freePlaceMap[y - 1][x] < count:
        freePlaceMap[y - 1][x] = count
        replaceAdjacent_cells(freePlaceMap, x, y - 1, count)
    if y < len(freePlaceMap) - 1 and freePlaceMap[y + 1][x] != -1 and freePlaceMap[y + 1][x] != count:
        freePlaceMap[y + 1][x] = count
        replaceAdjacent_cells(freePlaceMap, x, y + 1, count)


def getFreePlaceIndexForCoordinate(freePlaceMap, x, y):
    if freePlaceMap is None or len(freePlaceMap) < y or len(freePlaceMap[0]) < x or x < 0 or y < 0:
        return None
    if x > 0 and freePlaceMap[y][x - 1] != -1:
        return freePlaceMap[y][x - 1] - 1
    elif x < len(freePlaceMap[0]) - 1 and freePlaceMap[y][x + 1] != -1:
        return freePlaceMap[y][x + 1] - 1
    elif y > 0 and freePlaceMap[y - 1][x] != -1:
        return freePlaceMap[y - 1][x] - 1
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
