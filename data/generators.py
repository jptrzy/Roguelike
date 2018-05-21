import json
from tiles_data import tiles
from mobs import mobs



class aura_generator(object):
	def __init__(self, game):
		self.game = game

	def create_aura_from_data(self, aura_data):
		aura_glow_color = aura_data["glow_color"]
		aura_glow_range = aura_data["glow_range"]
		aura_glow_strength = aura_data["glow_strength"]
		aura_glow_color_strength = aura_data["glow_color_strength"]

		return tiles.aura(aura_glow_color, aura_glow_range, aura_glow_strength, aura_glow_color_strength)


class tile_generator(object):
	def __init__(self, game):
		self.game = game

	def re_path(self, path_to_tile_data):
		with open(path_to_tile_data) as file:
			self.tiles_data = json.load(file)

	def create_tile_from_id(self, tile_id):
		try:
			tile_data = self.tiles_data[tile_id]
		except KeyError:
			tile_data = self.tiles_data["error tile"]

		tile_name = tile_data["name"]
		tile_plural = tile_data["plural"]
		tile_icon = tile_data["icon"]
		tile_description = tile_data["description"]
		tile_color = tile_data["color"]
		tile_world_layer = tile_data["world layer"]

		# aura
		try:
			aura_data = tile_data["aura"]
			tile_aura = self.game.aura_generator.create_aura(aura_data)
		except KeyError:
			tile_aura = None

		# flags
		tile_flags = tile_data["flags"]		
		tile_blocks_sight = "BLOCKS_SIGHT" in tile_flags
		tile_blocks_path = "BLOCKS_PATH" in tile_flags
		tile_ethereal = "ETHEREAL" in tile_flags

		tile_obj = tiles.tile(name=tile_name, plural=tile_plural, icon=tile_icon, description=tile_description, color=tile_color, 
		                      world_layer=tile_world_layer, blocks_sight=tile_blocks_sight, blocks_path=tile_blocks_path, ethereal=tile_ethereal)

		return (tile_obj, tile_aura)

	def create_tile(self, tile_id, y, x):
		tile_obj, tile_aura = self.create_tile_from_id(tile_id)

		# attempt to add tile
		successful = self.game.world.layers.add_tile(y, x, tile_obj)

		# if successful, add aura if tile has one
		if successful:
			if tile_aura is not None:
				tile_aura._init(self.game.world, self.game.world.aura_group, self.game.world.glow_coords, self.game.FOV)
				tile_aura._spawn(y, x)

		return successful

class mob_generator(object):
	def __init__(self, game):
		self.game = game

	def re_path(self, path_to_tile_data):
		with open(path_to_tile_data) as file:
			self.mobs_data = json.load(file)

	def create_mob_from_id(self, mob_id):
		try:
			mob_data = self.mobs_data[mob_id]
		except KeyError:
			mob_data = self.mobs_data["test mob"]

		mob_name = mob_data["name"]
		mob_plural = mob_data["plural"]
		mob_description = mob_data["description"]
		mob_health = mob_data["health"]
		mob_speed = mob_data["speed"]
		mob_sight_range = mob_data["sight range"]
		mob_stamina = mob_data["stamina"]
		mob_hunger = mob_data["hunger"]
		mob_thirst = mob_data["thirst"]
		mob_mana = mob_data["mana"]
		mob_sense_range = mob_data["sense range"]
		mob_determined = mob_data["determined"]

		# flags
		mob_flags = mob_data["flags"]
		mob_pathfinding = "NO_PATHFINDING" not in mob_flags
		mob_hostile = "NOT_HOSTILE" not in mob_flags
		mob_ethereal = "ETHEREAL" in mob_flags

		# tile
		mob_tile_data = mob_data["tile"]
		tile_icon = mob_tile_data["icon"]
		tile_color = mob_tile_data["color"]

		tile_flags = mob_tile_data["flags"]
		tile_blocks_sight = "BLOCKS_SIGHT" in tile_flags

		# aura
		try:
			aura_data = mob_data["aura"]
			mob_aura = self.game.aura_generator.create_aura_from_data(aura_data)
			mob_emit = True
		except KeyError:
			mob_aura = None
			mob_emit = False

		mob_tile = tiles.tile(name=mob_name, plural=mob_plural, icon=tile_icon, description=mob_description, color=tile_color, 
		                      world_layer="mobs", blocks_sight=tile_blocks_sight, blocks_path=(not mob_ethereal), ethereal=mob_ethereal)
		
		mob_obj = mobs.mob(name=mob_name, plural=mob_plural, description=mob_description, health=mob_health, speed=mob_speed, sight_range=mob_sight_range, 
	                       stamina=mob_stamina, hunger=mob_hunger, thirst=mob_thirst, mana=mob_mana, sense_range=mob_sense_range, 
		                   determined=mob_determined, pathfinding=mob_pathfinding, hostile=mob_hostile, ethereal=mob_ethereal, tile=mob_tile, aura=mob_aura, emit=mob_emit,
		                   sight_border_requirement=500, detect_glow_str=100, detect_glow_range=20)

		return (mob_obj, mob_aura)

	def create_mob(self, mob_id, y, x):
		mob_obj, mob_aura = self.create_mob_from_id(mob_id)

		successful = mob_obj.spawn(y, x, self.game.world, self.game.FOV, self.game.all_mobs, self.game.timer.time)
		
		return successful