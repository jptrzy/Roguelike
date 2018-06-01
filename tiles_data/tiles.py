# -*- coding: utf-8 -*- 
import math
from include import gradient
import copy
import json
from include import bresenham
import random
from include import random_addon

class tile(object):
	def __init__(self, id_, name, plural, icon, description, description_long, color, world_layer_id, blocks_sight=False, blocks_path=False, ethereal=False, aura=None, debris_data=None):
		self.id_ = id_
		self.name = name
		self.plural = plural
		self.icon = icon
		self.description = description
		self.description_long = description_long
		self.color = color
		self.world_layer_id = world_layer_id

		self.blocks_sight = blocks_sight
		self.blocks_path = blocks_path
		self.ethereal = ethereal
		self.aura = aura
		self.debris_data = debris_data

	def remove(self, y, x, world, game):
		if self.aura is not None:
			self.aura._remove_effect()
			self.aura._remove()

		if self.debris_data is not None:
			try:
				debris_tiles = self.debris_data["tiles"]
				for debris_tile_id in debris_tiles:
					debris_tile_info = debris_tiles[debris_tile_id]
					debris_tile_lower_amount_limit = debris_tile_info["lower amount limit"]
					debris_tile_upper_amount_limit = debris_tile_info["upper amount limit"]
					debris_tile_bias_to_lowest_amount = debris_tile_info["bias to lowest amount"]

					amount = random_addon.random_integer_in_interval(debris_tile_lower_amount_limit, debris_tile_upper_amount_limit, bias_to_min=debris_tile_bias_to_lowest_amount)

					debris_tile_spread_radius = debris_tile_info["spread radius"]
					debris_tile_bias_to_center = debris_tile_info["bias to center"]
					
					# scatter the debris
					distance_map = bresenham.get_distance_map(y, x, debris_tile_spread_radius)
					debris_coordinates = game.FOV.Calculate_Sight(world.path_blockable_coordinates, y, x, debris_tile_spread_radius, distance_map)
					
					amount = min(amount, len(debris_coordinates))

					debris_amount = 0

					spawned_coords = set([])

					while debris_amount < amount:
						distance = random_addon.random_number_in_interval(0, debris_tile_spread_radius, bias_to_min=debris_tile_bias_to_center)
						select_random_coordinate = set([])
						
						for coordinate in debris_coordinates:
							if abs(distance_map[coordinate] - distance) < 1:
								if coordinate not in spawned_coords:
									select_random_coordinate.add(coordinate)
						
						# spawn a debris tile
						if len(select_random_coordinate) > 0:
							coordinate = random.choice(tuple(select_random_coordinate))
							game.tile_generator.create_tile(debris_tile_id, coordinate[0], coordinate[1])
							spawned_coords.add(coordinate)
						
						debris_amount += 1

			except KeyError:
				pass

class aura(object):
	def __init__(self, glow_color, glow_range, glow_str, glow_color_str):
		self.glow_color = glow_color
		self.glow_range = glow_range
		self.glow_str = glow_str
		self.glow_color_str = glow_color_str

		self.visible_tiles = []
		self.glow_aff_tile_coords = []
		self.glow_aff_tiles = {}

	def _init(self, worldmap, aura_group, glow_coords, FOV): # initialize
		self.worldmap = worldmap
		self.aura_group = aura_group # {(mapy, mapx) : [aura1, aura2, ... ]}

		# libraries of tiles affected by light

		self.glow_coords_group = glow_coords    # object with distinct coords
		self.glow_coords = glow_coords.distinct      # { (coords) : [ [color, emit strength(0-1000), color strength (0-1000)], ... }
		self.blockable_data = {}    # dict with {  (coords with blockable tile)  :  {1:True, 2:True, 3:False, ... }  }

		self.FOV = FOV

	def _spawn(self, y, x):
		self._add(y, x)
		self._recalc_distance_map()
		self._cast_light()
		self._add_effect()

	def _remove(self):
		self.aura_group[(self.mapy, self.mapx)].remove(self)


	def _add(self, y, x):
		self.y = y
		self.x = x
		self.mapy = self.worldmap.get_mapy(self.y)
		self.mapx = self.worldmap.get_mapx(self.x)

		try:
			self.aura_group[(self.mapy, self.mapx)].append(self)
		except KeyError:
			self.aura_group[(self.mapy, self.mapx)] = []
			self.aura_group[(self.mapy, self.mapx)].append(self)

	def _remove_effect(self):
		self.blockable_data = {}
		for glow_aff_tile_coord in self.glow_aff_tiles_coords:

			self.glow_coords[glow_aff_tile_coord].remove(self)
			
	def _add_effect(self):
		for glow_aff_tile_coord in self.glow_aff_tiles_coords:
			
			try:
				self.glow_coords[glow_aff_tile_coord].append(self)
			except KeyError:
				self.glow_coords[glow_aff_tile_coord] = [self]

			if glow_aff_tile_coord in self.worldmap.sight_blockable_coordinates:
				data = {}
				for i in range(16):
					data[i] = False # not illuminated

				# calculate octant in which aura lies relative to object
				octant = self.worldmap.get_octant(glow_aff_tile_coord, (self.y, self.x))
				data[octant] = True
				for n in (1, -1):
					for i in range(1,8): # loop around counter-clockwise first 1, 2, 3, ... , 7
						check_octant = (octant + n*i) % 16
						if check_octant % 2 == 0:
							y_fac = self.worldmap.octant_coords[check_octant][0]
							x_fac = self.worldmap.octant_coords[check_octant][1]
							if (glow_aff_tile_coord[0] + y_fac, glow_aff_tile_coord[1] + x_fac) in self.worldmap.sight_blockable_coordinates:
								break
							else:
								data[check_octant] = True
						else:
							data[check_octant] = True

				self.blockable_data[glow_aff_tile_coord] = data

	def _recalc_distance_map(self):
		self.g_distance_map = bresenham.get_distance_map(self.y, self.x, self.glow_range)

	def _cast_light(self): # use when opaque tile moves; must use _recalc_distance_map when source moves as well
		self.glow_aff_tiles_coords = self.FOV.Calculate_Sight(self.worldmap.sight_blockable_coordinates, self.y, self.x, self.glow_range, self.g_distance_map)

	def _move(self, y, x):
		self._remove_effect()
		self._remove()

		self._add(y, x)
		self._recalc_distance_map()
		self._cast_light()
		self._add_effect()

	def _recast(self):
		self._remove_effect()
		self._cast_light()
		self._add_effect()

	def _update(self, time):
		pass

class glow_aff_dict(object):
	def __init__(self, worldmap):
		self.distinct = {} # { (coords) : [ source1, source2, ... ] }
		self.worldmap = worldmap

	def _recast(self, coords):   # due to change in opaque block
		if coords in self.distinct:
			sources_copy = copy.copy(self.distinct[coords])
			for source in sources_copy:
				source._recast()

	def _reblend(self, coords, amb_color, amb_color_str, amb_glow_str, total_glow_str, tile_color, view_y, view_x):
		color_strength = amb_color_str

		colors = [amb_color]
		strengths = [amb_color_str*amb_glow_str]
		blend_tile_color_strength = total_glow_str - amb_color_str*amb_glow_str
		
		if coords in self.distinct:

			distinct_values = self.distinct[coords]

			for currentsource in distinct_values:
				if (coords not in currentsource.blockable_data) or ((coords in currentsource.blockable_data) and currentsource.blockable_data[coords][self.worldmap.get_octant(coords, (view_y, view_x))]):

					glow_distance = currentsource.g_distance_map[coords]
					# linear glow strength from max to 0
					currentsource_color_str_ratio = currentsource.glow_color_str - glow_distance*(currentsource.glow_color_str / currentsource.glow_range)

					currentsource_glow_str = currentsource.glow_str - glow_distance*(currentsource.glow_str / currentsource.glow_range)

					currentsource_color_str = currentsource_color_str_ratio*currentsource.glow_str

					color_strength += currentsource_color_str
					blend_tile_color_strength -= currentsource_color_str

					colors.append(currentsource.glow_color)
					strengths.append(currentsource_color_str)

		if len(tile_color) == 4:
			colors.append((tile_color[1], tile_color[2], tile_color[3]))
		else:
			colors.append(tile_color)

		strengths.append(blend_tile_color_strength)

		new_color = gradient.blend(colors, strengths)
		
		# add dark
		dark_factor = min(1, float(total_glow_str)/1000)

		for i in range(3):
			new_color[i] = int(new_color[i] * dark_factor)

		if len(tile_color) == 4:
			new_color.insert(0, tile_color[0])

		return new_color

	def _get_glow_str(self, coords, amb_glow_str, detect_glow_str, view_y, view_x):
		glow_str = amb_glow_str + detect_glow_str
		distinct_values = self.distinct[coords]
		for currentsource in distinct_values:
			if (coords not in currentsource.blockable_data) or ((coords in currentsource.blockable_data) and currentsource.blockable_data[coords][self.worldmap.get_octant(coords, (view_y, view_x))]):
				glow_distance = currentsource.g_distance_map[coords]
				glow_str += currentsource.glow_str - glow_distance*(currentsource.glow_str / currentsource.glow_range)
		return glow_str


#Misc
# move player to a separate json file
# player = light_tile('@', [71, 71, 71], True, False, 'You.', True, 10, [0,0,0], 500, 0, world_layer='terrain')

#Worldmap Chunk tiles
class chunktile(object):
	def __init__(self, icon, color, desc):
		self.icon = icon
		self.color = color
		self.desc = desc

w_void = chunktile(u'█', [102, 51, 0], 'Empty void.')
w_low_height = chunktile(u'█', [117, 10, 10], 'low height')
w_low_med_height = chunktile(u'█', [145, 13, 13], 'low med height')
w_med_height = chunktile(u'█', [178, 16, 16], 'med height')
w_med_high_height = chunktile(u'█', [197, 68, 68], 'med high height')
w_high_height = chunktile(u'█', [208, 103, 103], 'high height')
w_peaks = chunktile(u'█', [208, 103, 103], 'peaks')
w_rivers = chunktile(u'█', [154, 9, 9], 'rivers')

#Difficulty tiles
class difftile(object):
	def __init__(self, icon):
		self.icon = icon
		self.color = [255,50,205,50]

d0 = difftile(0)
d1 = difftile(1)
d2 = difftile(2)
d3 = difftile(3)
d4 = difftile(4)
d5 = difftile(5)
d6 = difftile(6)
d7 = difftile(7)
d8 = difftile(8)
d9 = difftile(9)
d10 = difftile('D')
