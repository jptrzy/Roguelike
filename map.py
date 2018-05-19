import string
import random
import tiles

def rand3(c1, c2, c3):
	x = random.randint(1, 3)
	if x <= 1:
		return c1
	elif x == 2:
		return c2
	else:
		return c3

def newtile(desc):
	# unshade for simple map
	return (tiles.empty, None)				   #---------space----------------------------------------
	#return (tiles.space, None)                 #--------dot---------------------------------------


	try:
		return (tile, con)
	except NameError:
		return (tile, None)

def grid_tile(mapy, mapx):
	if mapy % 2 == 0 and mapx % 2 == 0:
		return (tiles.empty, None)
	else:
		return (tiles.space, None)

def chunk(world, mapy, mapx, rows=100, collumns=100):

	topy = mapy * 100
	topx = mapx * 100

	map = world.tmap

	type = map[mapy][mapx][0].desc

	### adjacent tiles
	leftadj = map[mapy][mapx - 1][0].desc
	rightadj = map[mapy][mapx + 1][0].desc
	topadj = map[mapy - 1][mapx][0].desc
	botadj = map[mapy + 1][mapx][0].desc
	topleft = map[mapy - 1][mapx - 1][0].desc
	topright = map[mapy - 1][mapx + 1][0].desc
	bottomleft = map[mapy + 1][mapx - 1][0].desc
	bottomright = map[mapy + 1][mapx + 1][0].desc


	for i in range(rows):

		for n in range(collumns):

			if 20 <= i <= 80:
				if n <= 20:
					dire = leftadj
					dist_from_edge = int(n)
				elif n >= 80:
					dire = rightadj
					dist_from_edge = int(100 - n)
				else:
					dire = type
					dist_from_edge = int(40)
			elif i < 20:
				if 20 <= n <= 80:
					dire = topadj
					dist_from_edge = int(i)
				elif n < 20:
					dire = rand3(topleft, leftadj, topadj)              #------------------
					dist_from_edge = (i + n)/2
				elif n > 80:
					dire = rand3(topright, rightadj, topadj)             #------------------
					dist_from_edge = (i + (100 - n))/2
			elif i > 80:
				if 20 <= n <= 80:
					dire = botadj
					dist_from_edge = int(100 - i)
				elif n < 20:
					dire = rand3(bottomleft, botadj, leftadj)           #------------------
					dist_from_edge = (n + (100 - i))/2
				elif n > 80:
					dire = rand3(bottomright, botadj, rightadj)          #------------------
					dist_from_edge = (200 - n - i)/2

			rand = random.randint(1, 20)

			if dist_from_edge < rand: #tend toward adjacent
				rand2 = random.randint(0, 1)
				if rand2 == 0:
					new_tile_ = grid_tile(mapy, mapx) # dire
				else:
					new_tile_ = grid_tile(mapy, mapx)
			else: 
				new_tile_ = grid_tile(mapy, mapx)

			world.map.add_tile(i + topy, n + topx, new_tile_[0])

			#apply constructs, sight block                     #     ----------use add_Construct func-----------------------#

			if new_tile_[1] != None:
				world.conmap.add_tile(i+topy, n+topx, new_tile_[1])


	### initialize rooms