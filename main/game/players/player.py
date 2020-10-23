class Player(object):
    def __init__(self, id: int, directionOfLooking: str, active: bool, speed: int):
        self.id = id
        self.directionOfLooking = directionOfLooking
        self.active = active
        self.speed = speed