import json

with open('spe_ed-1603447830516.json') as f:
    data = json.load(f)

width = data[0]['width']
height = data[0]['height']

print("Playfield: " + str(width) + " x " + str(height))


for p in data[0]['players']:
    if data[0]['players'][p]['active'] == True:
        print("Player " + p + " is on [" + str(data[0]['players'][p]['x']) + "] [" + str(data[0]['players'][p]['y']) + "], looking " + str(data[0]['players'][p]['direction']) + " at speed " + str(data[0]['players'][p]['speed']))
    else:
        print("Player " + p + " is out.")


for c in data[0]['cells']:
    print(c)