import string
from tiles_data import tiles

class Room(object):
    def __init__(self, width, height, plan):
        self.width = width
        self.height = height
        self.plan = plan

def convert(room, tiledata):
    newdata = []
    roomdata = room.plan
    for row in range(room.height):
        newrow = []
        for collumn in range(room.width):
            currenttile = roomdata[row][collumn]
            newrow.append([tiledata[currenttile], row, collumn])
        newdata.append(newrow)
    return newdata

#---------------------ROOM PLANS--------------------------
hut = Room(8, 6, 
    [
    '########',
    '#....f.#',
    '#.b....#',
    '#.b...t#',
    '#......#',
    '###d####',
    ])
huttiledata = {'#' : tiles.wall, '.' : tiles.space, 'b' : tiles.bed, 't' : tiles.torch_dim, 'f' : tiles.fire_home, 'd' : tiles.wooden_door}


#----------------ROOM CONVERSION--------------------------
hut = convert(hut, huttiledata)