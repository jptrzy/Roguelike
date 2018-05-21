import string
import math

# Taken from http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm

def check_line(start, end, map):
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
 
    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)
 
    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
 
    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
 
    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1
 
    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
 
    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        # Check for block
        if (coord) in map:
        	return False
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx
 
    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()

    return True

def draw_line(start, end, map, topy, topx, tiles):
	changex = end[1] - start[1]
	changey = end[0] - start[0]

	if changex == 0:
		if end[0] < start[0]:
			for y in range(start[0], end[0] - 1, -1):
				if (y, start[1]) in map and y != start[0]:
					return
				tiles[(y - topy, start[1] - topx)] = (y, start[1])

		else:
			for y in range(start[0], end[0] + 1):
				if (y, start[1]) in map and y != start[0]:
					return
				tiles[(y - topy, start[1] - topx)] = (y, start[1])

	else:
		slope = float(changey)/changex
		adjust = 1 if slope >= 0 else -1
		err = 0
		rang = 0.5
		if -1 <= slope <= 1: 
			dslop = abs(slope)
			y = int(start[0])
			if end[1] < start[1]:
				for x in range(start[1], end[1] - 1, -1):
					if (y, x) in map and [y, x] != start:
						return
					tiles[(y - topy, x - topx)] = (y, x)
					err += dslop
					if err >= rang:
						y += adjust
						rang += 1
			else:
				for x in range(start[1], end[1] + 1):
					if (y, x) in map and [y, x] != start:
						return
					tiles[(y - topy, x - topx)] = (y, x)
					err += dslop
					if err >= rang:
						y += adjust
						rang += 1
		else:
			dslop = abs(float(changex)/changey)
			x = start[1]
			if end[0] < start[0]:
				for y in range(start[0], end[0] - 1, -1):
					if (y, x) in map and [y, x] != start:
						return
					tiles[(y - topy, x - topx)] = (y, x)
					err += dslop
					if err >= rang:
						x += adjust
						rang += 1
			else:
				for y in range(start[0], end[0]+1):
					if (y, x) in map and [y, x] != start:
						return
					tiles[(y - topy, x - topx)] = (y, x)
					err += dslop
					if err >= rang:
						x += adjust
						rang += 1

def distance(start, end, goal):
	d = ((start[1] - end[1])**2 + (start[0] - end[0])**2)**0.5
	if math.ceil(d) == goal or math.floor(d) == goal:
	#if d <= goal:
		return True
	else:
		return False

def distance_lower_than(start, end, goal, limit=0):
	d = ((start[1] - end[1])**2 + (start[0] - end[0])**2)**0.5
	if math.floor(d) <= goal or math.floor(d) <= limit:
		return True
	else:
		return False

def area_distance(start, end, goal):
	d = ((start[1] - end[1])**2 + (start[0] - end[0])**2)**0.5
	if math.ceil(d) <= goal:
		return True
	else:
		return False

def calc_distance(start, end):
	return ((start[1] - end[1])**2 + (start[0] - end[0])**2)**0.5