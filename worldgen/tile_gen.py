import string
import random

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
	return ("empty block", None)				   #---------space----------------------------------------
	#return (tiles.space, None)                 #--------dot---------------------------------------

def grid_tile(mapy, mapx):
	if mapy % 2 == 0 and mapx % 2 == 0:
		return ("empty block", None)
	else:
		return ("empty dot", None)

def chunk(world, game, mapy, mapx, rows=100, collumns=100):

	topy = mapy * 100
	topx = mapx * 100




	for i in range(rows):
		for n in range(collumns):
			new_tile_ = grid_tile(mapy, mapx)

			game.tile_generator.create_tile(new_tile_[0], i + topy, n + topx)

			#apply constructs, sight block                     #     ----------use add_Construct func-----------------------#

			if new_tile_[1] != None:
				game.tile_generator.create_tile(new_tile_[1], i+topy, n+topx)


	### initialize rooms