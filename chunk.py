# -*- coding: utf-8 -*-
import random
import string
import copy
import math
from map import *
from windowmod import *
from bearlibterminal import terminal

import tiles
import bresenham
import weather
import mobs
import gradient

import time

class worldlayer(object):
	def __init__(self, worldmap, name=''):
		self.tiles = {}
		self.visible_tiles = {}
		self.worldmap = worldmap
		self.name = name
		self.layer_group = self.worldmap.map_layers
		self.layer_group.append(self)

	def add_tile(self, y, x, tile):
		try:
			self.tiles[(y, x)]
			return False
		except KeyError:
			if self.worldmap.check_passable(y, x):
				self.tiles[(y, x)] = tile._create()
				self.worldmap.recalc_blockable(y, x)
				return True
			else:
				return False

	def delete_tile(self, y, x, tile):
		try:
			del self.tiles[(y, x)]
			self.worldmap.recalc_blockable(y, x)
			return True
		except KeyError:
			return False

class worldmap(object):
	def __init__(self, ylen, xlen, gametype):
		self.ylen = ylen
		self.xlen = xlen
		self.radius = ylen/2
		self.gametype = gametype

		self.w_ylen = 26#56   #90
		self.w_xlen = 46#96   #160

		self.worldmap = []
		self.dmap = []
		self.tmap = []
		self.cmap = []

		self.map_layers = []

		self.map = worldlayer(self, name='terrain')              #terrain, not destructible
		self.conmap = worldlayer(self, name='constructs')           #constructs
		self.entity_map = worldlayer(self, name='entities')	   #entities (only tiles)


		self.seethrough = set([])        #sight block map, upper layer

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
	def recalc_win(self, game_w_ylen, game_w_xlen):
		self.w_xlen = game_w_xlen - 32 # 32 from side panels
		self.w_ylen = game_w_ylen - 16 # 15 for message window
		self.windows.resize(self.w_ylen, self.w_xlen)

	def initworld(self):
		### init grid
		for y in range(self.ylen):
			self.worldmap.append([[] for i in range(self.xlen)])
			self.dmap.append([[] for i in range(self.xlen)])
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
				
		#defines difficulty tiles
		for i in range(self.ylen):
			for x in range(self.xlen):
				if self.worldmap[i][x] == []:
					self.dmap[i][x] = [tiles.d0]
				else:
					self.dmap[i][x] = [self.newchunk(self.worldmap[i][x])]

		#defines terrain and forests, etc -----------------------------------------------------

		# #### mountains ####
		# mountdata = {}

		# for i in range(random.randint(1, 3)):
		# 	while True:
		# 		mountstart = [random.randint(20, 80), random.randint(20, 80)]
		# 		if self.worldmap[mountstart[0]][mountstart[1]] != None:
		# 			if not bresenham.distance(mountstart, [50, 50], 30):
		# 				break

		# 	# draw path
		# 	mountainpath = []

		# 	disty = mountstart[0] - 50
		# 	distx = mountstart[1] - 50

		# 	if abs(disty) >= abs(distx):
		# 		mounttall = True
		# 	else:
		# 		mounttall = False
			
		# 	if mountstart[0] >= 50:
		# 		if mountstart[1] >= 50:
		# 			#bot. right
		# 			mountdirection = 'bot. right'
		# 		else:
		# 			#bot. left
		# 			mountdirection = 'bot. left'
		# 	else:
		# 		if mountstart[1] >= 50:
		# 			mountdirection = 'top right'
		# 			#top right
		# 		else:
		# 			#top left
		# 			mountdirection = 'top left'
		# 	self.mountainloop(mountstart, mountdirection, mounttall, mountainpath)

		# 	for mountaintile in mountainpath:
		# 		if self.worldmap[mountaintile[0]][mountaintile[1]] != []:
		# 			if mountaintile not in mountdata.keys():
		# 				mountdata[(mountaintile[0]), mountaintile[1]] = tiles.w_mountain
		# 			else:
		# 				if self.is_surrounded(mountdata, mountaintile[0], mountaintile[1]):
		# 					if random.randint(0, 5) != 0:
		# 						mountdata[(mountaintile[0]), mountaintile[1]] = tiles.w_tallmountain		

		# for mountain in mountdata.keys():
		# 	if random.randint(0, 5) != 0 and self.is_surrounded(mountdata, mountain[0], mountain[1]):
		# 		mountdata[mountain] = tiles.w_tallmountain

		# 	#adds to map
		# 	try:
		# 		self.tmap[mountain[0]][mountain[1]][0] = mountdata[mountain]
		# 	except IndexError:
		# 		self.tmap[mountain[0]][mountain[1]].append(mountdata[mountain])

		# ### forests ###

		# for i in range(random.randint(2, 4)):
		# 	randoffset = random.randint(self.radius/5, self.radius/2.5)
		# 	starty = self.center[0] + (random.randint(-1, 1)) * (randoffset)
		# 	startx = self.center[1] + (random.randint(-1, 1)) * (randoffset)
			
		# 	foresttiles = [[starty, startx]]
		# 	forestdata = {(starty, startx) : tiles.w_forest}
		# 	### grow
		# 	for i in range(random.randint(8, 12)):
		# 		for tree in foresttiles:
		# 			pathy = tree[0]
		# 			pathx = tree[1]

		# 			rand_direction = random.randint(1, 4)

		# 			if rand_direction == 1:    #North
		# 				pathy -= 1
		# 			elif rand_direction == 2:  #West
		# 				pathx += 1
		# 			elif rand_direction == 3:  #South
		# 				pathy += 1
		# 			else:                      #East
		# 				pathx -= 1

		# 			### checks for conflicts
		# 			if pathy >= self.ylen or pathy == 0 or pathx >= self.xlen or pathx == 0:
		# 				break
		# 			if self.worldmap[pathy][pathx] != None:
		# 				if (pathy, pathx) in forestdata.keys() and self.is_surrounded(forestdata, pathy, pathx):
		# 					forestdata[(pathy, pathx)] = tiles.w_thickforest
		# 				elif (pathy, pathx) not in forestdata.keys():
		# 					foresttiles.append([pathy, pathx])
		# 					forestdata[(pathy, pathx)] = tiles.w_forest


		# 	### adds forest to map
		# 	for tile in forestdata:
		# 		try:
		# 			if self.tmap[tile[0]][tile[1]][0] == tiles.w_mountain and forestdata[tile] == tiles.w_thickforest:
		# 				self.tmap[tile[0]][tile[1]][0] = tiles.w_mountainforest

		# 		except IndexError:
		# 			self.tmap[tile[0]][tile[1]].append(forestdata[tile])

		# #### everything else (grass) ####
		for y in range(self.ylen):
		 	for x in range(self.xlen):
		 		self.tmap[y][x].append(tiles.w_void)

		###  init windows
		self.windows = panel(self.w_ylen, self.w_xlen, 1, 16)

		self.map.window = self.windows.add_win(1)
		self.conmap.window = self.windows.add_win(10)
		self.entity_map.window = self.windows.add_win(20)

		### init minimap
		self.minimap = window(31, 30, 60, 60)
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

	# def mountainloop(self, mountstart, coord, tall, mountainpath):
	# 	pathy = int(mountstart[0])
	# 	pathx = int(mountstart[1])


	# 	if tall:
	# 		if coord in ['top right', 'top left']:
	# 			direction = 1
	# 		else:
	# 			direction = -1

	# 		for i in range(100):

	# 			randvalues = [-1, 0, 1]
	# 			randdir = randvalues[random.randint(1, 2)]
	# 			pathx += randdir
	# 			pathy += direction

	# 			if 10 < pathy < 90 and 10 < pathx < 90:
	# 				mountainpath.append((pathy, pathx))
	# 			else:
	# 				break

	# 	else:
	# 		if coord in ['top right', 'bot. right']:
	# 			direction = -1
	# 		else:
	# 			direction = 1

	# 		for i in range(100):
	# 			randvalues = [-1, 0, 1]
	# 			randdir = randvalues[random.randint(1, 2)]
	# 			pathy += randdir
	# 			pathx += direction

	# 			if 10 < pathy < 90 and 10 < pathx < 90:
	# 				mountainpath.append((pathy, pathx))
	# 			else:
	# 				break

	# 	# dynamic
	# 	branches = []

	# 	length = len(mountainpath)

	# 	for i in range(length):
	# 		i_n = ((float(i) / float(length)) * 100)
	# 		x = mountainpath[i][1]
	# 		y = mountainpath[i][0]

	# 		if i_n <= 10 or i_n >= 90:
	# 			pass
				
	# 		else:
	# 			if tall:
	# 				cord = x
	# 			else:
	# 				cord = y

	# 			if i_n <= 30 or i_n >= 70:
	# 				checklist = [cord - 1, cord + 1]
	# 			elif i_n <= 45 or i_n >= 55:
	# 				checklist = [cord - 2, cord - 1, cord + 1, cord + 2]
	# 			else:
	# 				checklist = [cord - 3, cord - 2, cord - 1, cord + 1, cord + 2, cord + 3]

	# 			for checkpath in checklist:
	# 				if 10 < checkpath < 90:
	# 					if tall:
	# 						branches.append((y, checkpath))
	# 					else:
	# 						branches.append((checkpath, x))

	# 	for branch in branches:
	# 		mountainpath.append(branch)
			



	def godprint(self, map):
		for row in range(self.ylen):
			printrow = []
			for collumn in range(self.xlen):
				printrow.append(str(map[row][collumn][0].icon))
			print string.join(printrow)

	def worldprint(self, map):
		for y in range(self.ylen):
			for x in range(self.xlen):
				terminal.put(x, y, str(map[y][x][0].icon))

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

	def printview(self, game):
		#p time_3 = time.clock()
		self.windows.clear()
		#self.windows.windows
		for layer in self.map_layers:
			for tilecoord in layer.visible_tiles:
				#{ (window coords) : [tile1, tile_color1] }
				layer_data = layer.visible_tiles[tilecoord]
				current_tile = layer_data[0]
				layer.window.put(tilecoord[0], tilecoord[1], current_tile.icon, layer_data[1])
		
		#p print("print view: --- %s seconds ---" % (time.clock() - time_3))
		#p print("--------------------------------------------------------")
		#p print("--------------------------------------------------------")

	def print_indicator(self, y, x, indicator=u'×'):
		self.windows.windows[-1].fx.put(y - self.window_top_y, x - self.window_top_x, indicator)

	def recalc_FOV(self, game):
		#p time_1 = time.clock()

		character = game.me

		locy = character.y
		locx = character.x

		sight = character.sight_range.max

		topy = locy - int(self.w_ylen / 2)
		topx = locx - int(self.w_xlen / 2)

		rendy = locy - sight
		rendx = locx - sight

		self.distance_map = {} # stores tiles distance from player

		for i in range(-1, sight*2 + 2):
			for n in range(-1, sight*2 + 2):
				self.distance_map[(rendy + i, rendx + n)] = math.hypot(locx - rendx - n, locy - rendy - i)

		self.visible_coords = game.FOV.Calculate_Sight(self.seethrough, locy, locx, sight, self.distance_map)

		
		#p print("FOV render: --- %s seconds ---" % (time.clock() - time_1))

	def recalc_view(self, game, y, x):
		#p time_2 = time.clock()

		self.visible_tiles = {}    # { (coords) : [[tile1, emit_color1, dark_color1, tile_color1], ... ] }
		sun_color = game.timer.day_night_color()
		sun_emit_str = game.timer.day_night_emit_str()
		sun_color_str = game.timer.day_night_color_str()

		self.window_top_y = y - self.w_ylen / 2
		self.window_top_x = x - self.w_xlen / 2

		for layer in self.map_layers:
			layer.visible_tiles = {}
			
		for tilecoord in self.visible_coords:
			window_y = tilecoord[0] - self.window_top_y
			window_x = tilecoord[1] - self.window_top_x
			if (window_y >= 0 and window_x >= 0) and (window_y < self.w_ylen and window_x < self.w_xlen):
				
				if tilecoord in self.covered:
					amb_color_str = int(sun_color_str * self.covered[tilecoord] / 100)
				else:
					amb_color_str = sun_color_str

				distance_from_char = self.distance_map[tilecoord]

				glow_strength = self.get_glow_str(game, tilecoord, sun_emit_str, distance_from_char, game.me)

				if glow_strength >= game.me.get_sight_requirement(distance_from_char):

					for layer in self.map_layers:
						if tilecoord in layer.tiles:
							tile_layer_data = []
							check_tile = layer.tiles[tilecoord]
							tile_layer_data.append(check_tile)

							new_color = self.glow_coords._reblend(tilecoord, sun_color, amb_color_str, self.amb_emit_str, glow_strength, check_tile.color, game.me.y, game.me.x)

							tile_layer_data.append(new_color)

							layer.visible_tiles[(window_y, window_x)] = tile_layer_data

		#p print("dynamic lighting: --- %s seconds ---" % (time.clock() - time_2))

	def get_glow_str(self, game, tilecoord, sun_emit_str, distance_from_mob, mob):
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

	def view(self, game):
		self.recalc_FOV(game)
		self.recalc_view(game, game.me.y, game.me.x)
		self.printview(game)

	def view_move(self, game, y, x):
		self.recalc_view(game, y, x)
		self.printview(game)

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
		for layer in self.map_layers:
			try:
				if layer.tiles[(tiley, tilex)].blockable:
					blocked = True
			except KeyError:
				pass

		if blocked:
			self.seethrough.add((tiley, tilex))
		else:
			try:
				self.seethrough.discard((tiley, tilex))
			except KeyError:
				pass

		# recalc emit
		self.glow_coords._recast((tiley, tilex))


	def check_passable(self, y, x):
		for layer in self.map_layers:
			if (y, x) in layer.tiles:
				if not layer.tiles[(y, x)].passable:
					return False
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

		chunk(self, y, x)

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
