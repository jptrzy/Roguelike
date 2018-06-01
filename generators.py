import json
from tiles_data import tiles
from mobs import mobs
from window import windows
import items
import action



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
		self.tiles = {} # dictionary of non-dynamic tiles: { tile_id : tile_obj }

	def re_path(self, path_to_tile_data):
		with open(path_to_tile_data) as file:
			self.data = json.load(file)

	def create_tile_from_data(self, tile_data, tile_id):
		# flags
		tile_flags = tile_data["flags"]
		tile_dynamic = "DYNAMIC" in tile_flags

		if not tile_dynamic:
			if tile_id in self.tiles:
				return self.tiles[tile_id]

		tile_blocks_sight = "BLOCKS_SIGHT" in tile_flags
		tile_blocks_path = "BLOCKS_PATH" in tile_flags
		tile_ethereal = "ETHEREAL" in tile_flags

		# standard data
		tile_name = tile_data["name"]
		tile_plural = tile_data["plural"]
		tile_icon = tile_data["icon"]
		tile_description = tile_data["description"]
		try:
			tile_description_long = tile_data["description long"]
		except KeyError:
			tile_description_long = None
		tile_color = tile_data["color"]
		tile_world_layer_id = tile_data["world layer id"]

		# debris
		try:
			debris_data = tile_data["debris"]
		except KeyError:
			debris_data = None

		tile_obj = tiles.tile(id_=tile_id, name=tile_name, plural=tile_plural, icon=tile_icon, description=tile_description, description_long=tile_description_long, color=tile_color, world_layer_id=tile_world_layer_id, blocks_sight=tile_blocks_sight, blocks_path=tile_blocks_path, ethereal=tile_ethereal, aura=None, debris_data=debris_data)

		if not tile_dynamic:
			self.tiles[tile_id] = tile_obj

		return tile_obj

	def create_tile_from_id(self, tile_id):
		try:
			tile_data = self.data[tile_id]
		except KeyError:
			return False

		if tile_id in self.tiles:
			tile_obj = self.tiles[tile_id]
		else:
			tile_obj = self.create_tile_from_data(tile_data, tile_id)

		# aura
		try:
			aura_data = tile_data["aura"]
			tile_aura = self.game.aura_generator.create_aura_from_data(aura_data)
		except KeyError:
			tile_aura = None

		return (tile_obj, tile_aura)

	def create_tile(self, tile_id, y, x):
		tile_obj, tile_aura = self.create_tile_from_id(tile_id)

		# attempt to add tile
		successful = self.game.world.layers.add_tile(y, x, tile_obj)

		# if successful, add aura if tile has one
		if successful:
			if tile_aura is not None:
				tile_obj.aura = tile_aura
				tile_aura._init(self.game.world, self.game.world.aura_group, self.game.world.glow_coords, self.game.FOV)
				tile_aura._spawn(y, x)

		return successful

class mob_generator(object):
	def __init__(self, game):
		self.game = game

	def re_path(self, path_to_mob_data):
		with open(path_to_mob_data) as file:
			self.data = json.load(file)

	def create_mob_from_id(self, mob_id):
		try:
			mob_data = self.data[mob_id]
		except KeyError:
			return False

		mob_name = mob_data["name"]
		mob_plural = mob_data["plural"]
		mob_description = mob_data["description"]
		try:
			mob_description_long = mob_data["description long"]
		except KeyError:
			mob_description_long = None
		mob_health = mob_data["health"]
		mob_speed = mob_data["speed"]
		mob_carry_weight = mob_data["carry weight"]
		mob_carry_volume = mob_data["carry volume"]
		mob_sight_range = mob_data["sight range"]
		mob_stamina = mob_data["stamina"]
		mob_hunger = mob_data["hunger"]
		mob_thirst = mob_data["thirst"]
		mob_mana = mob_data["mana"]
		mob_sense_range = mob_data["sense range"]
		mob_determined = mob_data["determined"]
		mob_actions = mob_data["actions"]
		# convert actions to objects
		for i, action_id in enumerate(mob_actions):
			mob_actions[i] = self.game.action_generator.get_action_from_id(action_id)

		# flags
		mob_flags = mob_data["flags"]
		mob_pathfinding = "NO_PATHFINDING" not in mob_flags
		mob_hostile = "NOT_HOSTILE" not in mob_flags
		mob_ethereal = "ETHEREAL" in mob_flags

		# tile
		mob_tile_data = mob_data["tile"]

		mob_tile_data["id_"] = mob_id
		mob_tile_data["name"] = mob_name
		mob_tile_data["plural"] = mob_plural
		mob_tile_data["description"] = mob_description
		mob_tile_description_long = mob_description_long
		mob_tile_data["world layer id"] = "mobs"

		if not mob_ethereal:
			mob_tile_data["flags"].append("BLOCKS_PATH")

		mob_tile_data["flags"].append("DYNAMIC")

		# aura
		try:
			aura_data = mob_data["aura"]
			mob_aura = self.game.aura_generator.create_aura_from_data(aura_data)
			mob_emit = True
		except KeyError:
			mob_aura = None
			mob_emit = False

		mob_tile = self.game.tile_generator.create_tile_from_data(mob_tile_data, mob_id)
		
		mob_obj = mobs.mob(id_=mob_id, name=mob_name, plural=mob_plural, description=mob_description, description_long=mob_description_long, health=mob_health, speed=mob_speed, carry_weight=mob_carry_weight, carry_volume=mob_carry_volume, sight_range=mob_sight_range, stamina=mob_stamina, hunger=mob_hunger, thirst=mob_thirst, mana=mob_mana, sense_range=mob_sense_range, determined=mob_determined, pathfinding=mob_pathfinding, hostile=mob_hostile, ethereal=mob_ethereal, tile=mob_tile, aura=mob_aura, emit=mob_emit, sight_border_requirement=500, detect_glow_str=100, detect_glow_range=20, actions=mob_actions)

		return (mob_obj, mob_aura)

	def create_mob(self, mob_id, y, x):
		mob_obj, mob_aura = self.create_mob_from_id(mob_id)

		successful = mob_obj.spawn(y, x, self.game.world, self.game.FOV, self.game.all_mobs, self.game.timer.time)
		
		return successful

class action_generator(object):
	def __init__(self, game):
		self.game = game
		self.actions = {} # dictionary: { action id : action obj }

	def re_path(self, path_to_action_data):
		with open(path_to_action_data) as file:
			self.data = json.load(file)

	def get_action_from_id(self, id_):
		if id_ in self.actions:
			return self.actions[id_]
		try:
			action_data = self.data[id_]
		except KeyError:
			return False

		action_type = action_data["type"]
		action_name = action_data["name"] 
		action_description = action_data["description"]
		action_cast_time = action_data["cast_time"] 
		action_recover_time = action_data["recover_time"]
		action_cost = action_data["cost"]

		action_flags = action_data["flags"]

		if action_type == "movement":
			action_range = action_data["range"]
			action_obj = action.Movement_Action(id_=id_, name=action_name, cast_time=action_cast_time, recover_time=action_recover_time, cost=action_cost, range=action_range)

		elif action_type == "melee attack":
			action_damage = action_data["damage"]
			action_obj = action.Melee_Attack(id_=id_, name=action_name, cast_time=action_cast_time, recover_time=action_recover_time, cost=action_cost, damage=action_damage)

		self.actions[id_] = action_obj
		return action_obj

class item_generator(object):
	def __init__(self, game):
		self.game = game
		self.items = {} # dictionary: { non-dynamic item id : item obj }

	def re_path(self, path_to_item_data):
		with open(path_to_item_data) as file:
			self.data = json.load(file)

	def create_item_from_id(self, id_):
		try:
			item_data = self.data[id_]
		except KeyError:
			return False

		# flags
		item_flags = item_data["flags"]
		item_dynamic = "DYNAMIC" in item_flags

		if not item_dynamic:
			if id_ in self.items:
				return self.items[id_]

		# create new instance of item plural, icon, color, description, description_long,  weight, volume
		item_type = item_data["type"]

		item_name = item_data["name"]
		item_plural = item_data["plural"]
		item_slot = item_data["slot"]
		if item_slot == "None":
			item_slot = None
		item_icon = item_data["icon"]
		item_color = item_data["color"]
		item_description = item_data["description"]
		try:
			item_description_long = item_data["description long"]
		except KeyError:
			item_description_long = None
		item_weight = item_data["weight"]
		item_volume = item_data["volume"]

		try:
			item_buffs = item_data["buffs"]
		except KeyError:
			item_buffs = {}

		try:
			item_multipliers = item_data["multipliers"]
		except KeyError:
			item_multipliers = {}

		if item_type == "standard":
			item_obj = items.item(type=item_type, id_=id_, name=item_name, plural=item_plural, slot=item_slot, icon=item_plural, color=item_color, description=item_description, description_long=item_description_long,  weight=item_weight, volume=item_volume, buffs=item_buffs, multipliers=item_multipliers)

		elif item_type == "melee weapon":
			item_base_damage = item_data["base damage"]
			item_actions_ids = item_data["actions"]

			item_actions = []

			# convert action ids into objects
			for action_id in item_actions_ids:
				item_actions.append(self.game.action_generator.get_action_from_id(action_id))

			item_obj = items.melee_weapon(type=item_type, id_=id_, name=item_name, plural=item_plural, slot=item_slot, icon=item_plural, color=item_color, description=item_description, description_long=item_description_long,  weight=item_weight, volume=item_volume, buffs=item_buffs, multipliers=item_multipliers, base_damage=item_base_damage, actions=item_actions)

		if not item_dynamic:
			self.items[id_] = item_obj

		return item_obj