# -*- coding: utf-8 -*-
import random
import string
import copy
import math
from worldgen import tile_gen
from window import windows
from bearlibterminal import terminal

from tiles_data import tiles
from include import bresenham
import weather
from mobs import mobs
from include import gradient

import time
"""
World layers (from lowest to highest):
- terrain
- constructs
- mobs
"""

class worldlayer(object):
	def __init__(self, worldmap, name, max_objects=1):
		self.worldmap = worldmap
		self.name = name
		self.max_objects = max_objects # max number of objects that can occupy a coordinate space in the layer

		self.tiles = {} # dictionary: { (y, x) : number of objects }
		self.layer_group = self.worldmap.layers

	def add_tile(self, y, x): # checks if the tile is occupied DOES NOT CHECK IF BLOCKABLE
		try:
			if self.tiles[(y, x)] + 1 > self.max_objects:
				successful = False
			else:
				self.tiles[(y, x)] += 1
				successful = True

		except KeyError:
			self.tiles[(y, x)]  = 1
			successful = True

		return successful

	def delete_tile(self, y, x):
		try:
			self.tiles[(y, x)] -= 1
		except KeyError:
			return

class layer_tracker(object):
	def __init__(self, worldmap):
		self.worldmap = worldmap

		self.worldlayers_count = 0

		self.worldlayers = {}     # dictionary: { "world layer name" : world layer object, ... }
		self.tiles = {}           # dictionary: { (y, x) : [tile1, tile2, tile3, ... ], ... }

		self.visible_tiles_info = {} # dictionary of tile data as specified in worldmap.recalc_view

		self.windows = windows.panel(self.worldmap.w_ylen, self.worldmap.w_xlen, 1, 10)

		self.windows.add_win(self.worldlayers_count+1, "top")

	def add_layer(self, name, max_objects=1):
		new_worldlayer = worldlayer(self.worldmap, name, max_objects)
		self.worldlayers[new_worldlayer.name] = new_worldlayer
		self.worldlayers_count += 1
		new_worldlayer.window = self.windows.add_win(self.worldlayers_count, new_worldlayer.name)

		self.recalc_top_window()

	def recalc_top_window(self):
		self.windows.del_win("top")
		self.windows.add_win(self.worldlayers_count+1, "top")

	def add_tile(self, y, x, tile):
		tile.worldlayer = self.worldlayers[tile.worldlayer_name]
		if not tile.worldlayer.add_tile(y, x):
			successful = False
		else:
			# worldlayer able to store object, now check other conditions
			if (not tile.ethereal) and (not self.worldmap.check_passable(y, x)):
				successful = False
			else:
				# tile able to be placed
				try:
					self.tiles[(y, x)].append(tile)
				except KeyError:
					self.tiles[(y, x)] = [tile]

				successful = True

		if successful:
			self.recalculate_space(y, x)

		return successful

	def delete_tile(self, y, x, tile):
		try:
			self.tiles[(y, x)].remove(tile)
			tile.worldlayer.delete_tile(y, x)
			successful = True
		except KeyError:
			successful = False

		if successful:
			self.recalculate_space(y, x)

		return successful

	def recalculate_space(self, y, x):
		self.worldmap.recalc_blockable(y, x)


	def get_tiles(self, y, x):
		# returns a list of all tiles within the space
		try:
			return self.tiles[(y, x)]
		except KeyError:
			return None

class worldmap(object):
	def __init__(self, game, ylen, xlen, gametype):
		self.game = game
		self.ylen = ylen
		self.xlen = xlen
		self.radius = ylen/2
		self.gametype = gametype

		self.w_ylen = 0
		self.w_xlen = 0

		self.worldmap = []
		self.tmap = []
		self.cmap = []

		# initialize layers
		self.layers = layer_tracker(self)
		self.layers.add_layer('terrain', max_objects=1)
		self.layers.add_layer('constructs', max_objects=1)
		self.layers.add_layer('mobs', max_objects=1)
		self.layers.add_layer('example objects', max_objects=10)


		self.blockable_coordinates = set([])        #sight block map

		self.aura_group = {}      #aura_group, glow_coords

		self.glow_coords = tiles.glow_aff_dict(self)

		self.covered = {}   #{(coords) : amount of cover (0-100)}

		self.center = [self.ylen/2, self.xlen/2]
		self.startyx = [self.ylen/2 + random.randint(-6, 6), self.xlen/2 + random.randint(-8, 8)]

		self.octant_coords = {
		0:(0,1),
		2:(-1,1),
		4:(-1,0),
		6:(-1,-1),
		8:(0,-1),
		10:(1,-1),
		12:(1,0),
		14:(1,1)
		}
###################################
################ ##################
###### ### 5 ###4# 3 ##### 2 ######
#######6######## ######   #########
## 7 ###  ###### #### #############
##########   ### #   ###### 1 #####
#############  #  #################
#    8                      0      #
###############     ###############
#############  # ###   #####15#####
### 9  ####   ## ######14 #########
#########10##### ###13####  #######
######   ###11## ########### ######
################12 ################
################ ##################
###################################
	def recalc_win(self, w_ylen, w_xlen, y, x):
		self.w_xlen = w_xlen
		self.w_ylen = w_ylen
		self.layers.windows.resize(self.w_ylen, self.w_xlen)
		self.layers.windows.move(y, x)

	def initworld(self):
		### init grid
		for y in range(self.ylen):
			self.worldmap.append([[] for i in range(self.xlen)])
			self.tmap.append([[] for i in range(self.xlen)])
			self.cmap.append([[] for i in range(self.xlen)])
		
		### generate shape
		for y in range(self.ylen):
			for x in range(self.xlen):
				distance_from_center = ((y - self.center[0]) ** 2 + (x - self.center[1]) ** 2) ** 0.5
				if distance_from_center < self.ylen/3.5:
					self.worldmap[y][x] = copy.copy(distance_from_center)
				if round(distance_from_center) == round(self.ylen/3.5)-1:
					pathy = int(y)
					pathx = int(x)

					for i in range(100):
						rand_direction = random.randint(1, 4)
						
						#Determine new direction for path
						if rand_direction == 1:
							pathy += 1
						elif rand_direction == 2:
							pathy -= 1
						elif rand_direction == 3:
							pathx += 1
						else:
							pathx -= 1

						#Check current location
						if pathy >= (self.ylen) or pathy < 0 or pathx >= self.xlen or pathx < 0:
							break

						#checks distance from center of map
						distance_from_center = ((pathy - self.center[0]) ** 2 + (pathx - self.center[1]) ** 2) ** 0.5

						#allows a length/5 empty border
						if distance_from_center > (self.ylen/2) - 5:
							break
						else:
							self.worldmap[pathy][pathx] = copy.copy(distance_from_center)

		### init minimap
		self.minimap = windows.window(31, 30, 60, 60)
		self.minimapgrid = []
		for i in range(30):
			self.minimapgrid.append([[] for x in range(30)])

	def is_surrounded(self, grid, y, x):
		c = [-1, 1]
		for i in c:
			if (y+i, x) not in grid.keys():
				return False
			elif (y, x+i) not in grid.keys():
				return False
			elif (y+i, x+i) not in grid.keys():
				return False
			elif (y+i, x-i) not in grid.keys():
				return False
			else:
				pass
		return True

	def minimapprint(self, mapy, mapx):
		self.minimap.clear()
		minitopy = mapy - 15
		minitopx = mapx - 15
		self.tmap[mapy][mapx].insert(0, tiles.player)

		for y in range(30):
			for x in range(30):
				self.minimap.put(y, x, str(self.tmap[minitopy + y][minitopx + x][0].icon), self.tmap[minitopy + y][minitopx + x][0].color)

		self.tmap[mapy][mapx].pop(0)

		self.minimap.wprint(31, 0, str(self.tmap[mapy][mapx][0].desc), self.tmap[mapy][mapx][0].color)

	def printview(self):
		#p time_3 = time.clock()
		self.layers.windows.clear()
		
		for tilecoord in self.layers.visible_tiles_info:
			#{ (window coords) : [[tile1, tile_color1], ... ] }
			for tile_data in self.layers.visible_tiles_info[tilecoord]:
				current_tile = tile_data[0]
				self.layers.windows.get_win(current_tile.worldlayer.name).put(tilecoord[0], tilecoord[1], current_tile.icon, tile_data[1])

		#p print("print view: --- %s seconds ---" % (time.clock() - time_3))
		#p print("--------------------------------------------------------")
		#p print("--------------------------------------------------------")

	def print_indicator(self, y, x, indicator=u'×'):
		self.layers.windows.get_win("top").put(y - self.window_top_y, x - self.window_top_x, indicator)

	def recalc_FOV(self):
		#p time_1 = time.clock()

		character = self.game.me

		locy = character.y
		locx = character.x

		sight = character.sight_range.value

		rendy = locy - sight
		rendx = locx - sight

		self.distance_map = {} # stores tiles distance from player

		for i in range(-1, sight*2 + 2):
			for n in range(-1, sight*2 + 2):
				self.distance_map[(rendy + i, rendx + n)] = math.hypot(locx - rendx - n, locy - rendy - i)

		self.visible_coords = self.game.FOV.Calculate_Sight(self.blockable_coordinates, locy, locx, sight, self.distance_map)

		
		#p print("FOV render: --- %s seconds ---" % (time.clock() - time_1))

	def recalc_view(self, y, x):
		#p time_2 = time.clock()

		sun_color = self.game.timer.day_night_color()
		sun_emit_str = self.game.timer.day_night_emit_str()
		sun_color_str = self.game.timer.day_night_color_str()

		self.window_top_y = y - int(float(self.w_ylen) / 2)
		self.window_top_x = x - int(float(self.w_xlen) / 2)

		self.layers.visible_tiles_info = {}
			
		for tilecoord in self.visible_coords:
			window_y = tilecoord[0] - self.window_top_y
			window_x = tilecoord[1] - self.window_top_x
			if (window_y >= 0 and window_x >= 0) and (window_y < self.w_ylen and window_x < self.w_xlen):
				
				if tilecoord in self.covered:
					amb_color_str = int(sun_color_str * self.covered[tilecoord] / 100)
				else:
					amb_color_str = sun_color_str

				distance_from_char = self.distance_map[tilecoord]

				glow_strength = self.get_glow_str(tilecoord, distance_from_char, self.game.me)

				if glow_strength >= self.game.me.get_sight_requirement(distance_from_char):
					tiles_in_coord = self.layers.get_tiles(tilecoord[0], tilecoord[1])
					if tiles_in_coord != None:
						for check_tile in tiles_in_coord:
							tile_layer_data = []
							tile_layer_data.append(check_tile)

							new_color = self.glow_coords._reblend(tilecoord, sun_color, amb_color_str, self.amb_emit_str, glow_strength, check_tile.color, self.game.me.y, self.game.me.x)

							tile_layer_data.append(new_color)

							try:
								self.layers.visible_tiles_info[(window_y, window_x)].append(tile_layer_data)
							except KeyError:
								self.layers.visible_tiles_info[(window_y, window_x)] = [tile_layer_data]

		#p print("dynamic lighting: --- %s seconds ---" % (time.clock() - time_2))

	def get_glow_str(self, tilecoord, distance_from_mob, mob):
		sun_emit_str = self.game.timer.day_night_emit_str()

		if tilecoord in self.covered:
			self.amb_emit_str = int(sun_emit_str * self.covered[tilecoord] / 100)
		else:
			self.amb_emit_str = sun_emit_str

		detect_glow_str = mob.get_detect_glow_str(distance_from_mob)
		
		if tilecoord in self.glow_coords.distinct:
			glow_strength = self.glow_coords._get_glow_str(tilecoord, self.amb_emit_str, detect_glow_str, mob.y, mob.x)
		else:
			glow_strength = self.amb_emit_str + detect_glow_str

		return glow_strength

	def check_enough_light(self, tilecoord, distance_from_mob, mob):
		glow_strength = self.get_glow_str(tilecoord, distance_from_mob, mob)
		return glow_strength >= mob.get_sight_requirement(distance_from_mob)

	def view(self):
		#p FOV_time = time.clock()
		self.recalc_FOV()
		#p FOV_time = time.clock() - FOV_time
		#p render_time = time.clock()
		self.recalc_view(self.game.me.y, self.game.me.x)
		#p render_time = time.clock() - render_time
		#p print_time = time.clock()
		self.printview()
		#p print_time = time.clock() - print_time

		#p print("FOV time: %s \n Render time: %s \n Print view time: %s \n" % (FOV_time, render_time, print_time))

	def view_move(self, y, x):
		self.recalc_view(y, x)
		self.printview()

	def adjacent_by(self, y, x, map):
		c = [-1, 1]
		for i in c:
			if (y+i, x) in map.keys():
				return True
			elif (y, x+i) in map.keys():
				return True
			elif (y+i, x+i) in map.keys():
				return True
			elif (y+i, x-i) in map.keys():
				return True
			else:
				pass
		return False

	def recalcloc(self, mapy, mapx):
		c = [-1, 1]

		if self.cmap[mapy][mapx] == []:
			self.initchunk(mapy, mapx)

		for i in c:
			if self.cmap[mapy+i][mapx] == []:
				self.initchunk(mapy+i, mapx)
			if self.cmap[mapy][mapx+i] == []:
				self.initchunk(mapy, mapx+i)
			if self.cmap[mapy+i][mapx+i] == []:
				self.initchunk(mapy+i, mapx+i)
			if self.cmap[mapy+i][mapx-i] == []:
				self.initchunk(mapy+i, mapx-i)

		# recalculate minimap
		#self.minimapprint(mapy, mapx)                             #------------------------------------------------------------------------------

	def recalc_blockable(self, tiley, tilex):       # recalc blockable
		blocked = False
		try:
			for tile in self.layers.tiles[(tiley, tilex)]:
				if tile.blocks_sight:
					blocked = True
					break
		except KeyError:
			pass

		if blocked:
			if (tiley, tilex) not in self.blockable_coordinates:
				# only change if necessary
				self.blockable_coordinates.add((tiley, tilex))
				self.glow_coords._recast((tiley, tilex))
		else:
			if self.blockable_coordinates.discard((tiley, tilex)) != None:
				self.glow_coords._recast((tiley, tilex))

	def check_passable(self, y, x):
		try:
			for tile in self.layers.tiles[(y, x)]:
				if tile.blocks_path:
					return False
		except KeyError:
			pass
		return True

	def newchunk(self, distance):
		parameters = {1:tiles.d1,2:tiles.d2,3:tiles.d3,4:tiles.d4,5:tiles.d5,6:tiles.d6,7:tiles.d7,8:tiles.d8,9:tiles.d9,10:tiles.d10}
		step = self.radius / 10       #not 10 for the last step
		check = copy.copy(step)
		Range = 1
		while True:
			if distance < check:
				break
			else:
				check += step
				Range += 1

		random_n = random.randint(-2, 2)
		try:
			chunk = parameters[Range + random_n]
		except KeyError:
			chunk = parameters[Range]
		return chunk

	def initchunk(self, y, x):
		self.cmap[y][x].append('.')

		tile_gen.chunk(self, self.game, y, x)

	def get_mapx(self, x):
		return int(math.floor(x / 100))

	def get_mapy(self, y):
		return int(math.floor(y / 100))

	def get_octant(self, coord1, coord2): # relative to coord1
		Ax, Ay = coord1[1], -coord1[0]
		Bx, By = coord2[1], -coord2[0]

		dy = By - Ay
		dx = Bx - Ax

		angle = math.atan2(dy, dx)

		if angle == 0:
			return 0
		elif angle > 0:
			if angle < math.pi/4:
				return 1
			elif angle == math.pi/4:
				return 2
			elif angle < math.pi/2:
				return 3
			elif angle == math.pi/2:
				return 4
			elif angle < 3*math.pi/4:
				return 5
			elif angle == 3*math.pi/4:
				return 6
			elif angle < math.pi:
				return 7
			elif angle == math.pi:
				return 8
		elif angle < 0:
			if angle == -math.pi:
				return 8
			elif angle < -3*math.pi/4:
				return 9
			elif angle == -3*math.pi/4:
				return 10
			elif angle < -math.pi/2:
				return 11
			elif angle == -math.pi/2:
				return 12
			elif angle < -math.pi/4:
				return 13
			elif angle == -math.pi/4:
				return 14
			elif angle < 0:
				return 15


###################################
################ ##################
###### ### 5 ###4# 3 ##### 2 ######
#######6######## ######   #########
## 7 ###  ###### #### #############
##########   ### #   ###### 1 #####
#############  #  #################
#    8                      0      #
###############     ###############
#############  # ###   #####15#####
### 9  ####   ## ######14 #########
#########10##### ###13####  #######
######   ###11## ########### ######
################12 ################
################ ##################
###################################
