import asyncio
import json
import websockets

def __init__():
    pass


async def play():
    url = "wss://msoll.de/spe_ed"
    key = "72ILGT3YVIW5DV2UR3L5E6VCMFB6TJPR6LAX2ZLGMYGRQSVTW2C4G4E2"

    async with websockets.connect(f"{url}?key={key}") as websocket:
        print("Waiting for initial state...", flush=True)
        while True:
            state_json = await websocket.recv()
            state = json.loads(state_json)
            print("<", state)

asyncio.get_event_loop().run_until_complete(play())