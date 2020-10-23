import asyncio
import json

import websockets as websockets

from game.playground import Playground


class Game:

    def __init__(self, url, key):
        self.URL = url
        self.KEY = key
        self.playGround = Playground()

    async def play(self):
        async with websockets.connect(f"{self.URL}?key={self.KEY}") as websocket:
            print("Waiting for initial state...", flush=True)
        while True:
            state_json = await websocket.recv()
            state = json.loads(state_json)
            print("<", state)

            # TODO Draw
            self.playGround.draw(state["cells"])

            # If not own Bot break
            own_player = state["players"][str(state["you"])]
            if not state["running"] or not own_player["active"]:
                break

            # TODO If own Bot, calc Action and send

            action = ""
            print(">", action)
            action_json = json.dumps({"action": action})
            await websocket.send(action_json)


game = Game()

asyncio.get_event_loop().run_until_complete(game.play())
