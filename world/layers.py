from window import windows
import json

"""
World layers (from lowest to highest):
- terrain
- constructs
- mobs

- items
"""

class worldlayer(object):
	def __init__(self, worldmap, id_, name, max_objects, destructable):
		self.worldmap = worldmap
		self.id_ = id_
		self.name = name
		self.max_objects = max_objects # max number of objects that can occupy a coordinate space in the layer
		self.destructable = destructable # player is able to destroy objects within this layer

		self.tiles = {} # dictionary: { (y, x) : number of objects }
		self.layer_group = self.worldmap.layers

	def check_add_tile_conditions(self, y, x):
		try:
			if self.tiles[(y, x)] + 1 > self.max_objects:
				return False
			else:
				return True
		except KeyError:
			return True

	def add_tile(self, y, x): # MUST CHECK WITH check_add_tile_conditions() BEFORE CALLING!
		try:
			self.tiles[(y, x)] += 1
		except KeyError:
			self.tiles[(y, x)] = 1

	def delete_tile(self, y, x):
		try:
			self.tiles[(y, x)] -= 1
		except KeyError:
			return

class layer_tracker(object):
	def __init__(self, worldmap, game):
		self.worldmap = worldmap
		self.game = game

		self.worldlayers_count = 0

		self.worldlayers = {}     # dictionary: { "world layer name" : world layer object, ... }
		self.tiles = {}           # dictionary: { (y, x) : [tile1, tile2, tile3, ... ], ... }

		self.visible_tiles_info = {} # dictionary of tile data as specified in worldmap.recalc_view

		self.windows = windows.panel(self.worldmap.w_ylen, self.worldmap.w_xlen, 1, 10)

		self.windows.add_win(self.worldlayers_count+1, "top")

	def re_path(self, path_to_tile_data):
		with open(path_to_tile_data) as file:
			self.data = json.load(file)

	def init_layers(self):
		ordered_layers = self.data["order"]
		for layer_id in ordered_layers:
			layer = self.data[layer_id]
			layer_name = layer["name"]
			layer_max_objects = layer["max objects"]
			layer_destructable = layer["destructable"]

			self.add_layer(layer_id, layer_name, layer_max_objects, layer_destructable)

	def add_layer(self, id_, name, max_objects, destructable):
		new_worldlayer = worldlayer(self.worldmap, id_, name, max_objects, destructable)
		self.worldlayers[new_worldlayer.id_] = new_worldlayer
		self.worldlayers_count += 1
		new_worldlayer.window = self.windows.add_win(self.worldlayers_count, new_worldlayer.id_)

		self.recalc_top_window()

	def recalc_top_window(self):
		self.windows.del_win("top")
		self.windows.add_win(self.worldlayers_count+1, "top")

	def check_add_tile_conditions(self, y, x, tile):
		if not tile.worldlayer.check_add_tile_conditions(y, x):
			return False
		else:
			# worldlayer able to store object, now check other conditions
			if (not tile.ethereal) and (not self.worldmap.check_passable(y, x)):
				return False

		return True

	def add_tile(self, y, x, tile): # MUST CHECK WITH check_add_tile_conditions() BEFORE CALLING!
		tile.worldlayer.add_tile(y, x)
		try:
			self.tiles[(y, x)].append(tile)
		except KeyError:
			self.tiles[(y, x)] = [tile]

		self.recalculate_space(y, x)

	def delete_tile(self, y, x, tile):
		try:
			self.tiles[(y, x)].remove(tile)
			tile.worldlayer.delete_tile(y, x)
			successful = True
		except KeyError:
			successful = False

		if successful:
			self.recalculate_space(y, x)
			tile.remove(y, x, self.worldmap, self.game)
			self.recalculate_space(y, x)

		return successful

	def get_destructable_tiles(self, y, x):
		destructable_tiles = []

		for tile in self.tiles[(y, x)]:
			if tile.worldlayer.destructable:
				destructable_tiles.append(tile)

		return destructable_tiles

	def recalculate_space(self, y, x):
		self.worldmap.recalc_blockable(y, x)


	def get_tiles(self, y, x):
		# returns a list of all tiles within the space
		try:
			return self.tiles[(y, x)]
		except KeyError:
			return None