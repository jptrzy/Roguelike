from bearlibterminal import terminal
from window import windows

### inventory
"""
slots:
primary weapon
"""
class inventory(object):
	def __init__(self, mob):
		self.mob = mob
		self.items = [] # list of all item objects, equipped and unequipped
		self.equipped_items = {
		# dictionary of currently equipped item objects with format
		# slot : item (None if nothing equipped)
		"primary weapon" : None
		}

		# lookup table for converting stat id to stat object
		self.stat_ids = {
			"stamina" : mob.stamina_stat,
			"carry weight" : mob.carry_weight_stat,
			"carry volume" : mob.carry_volume_stat,
			"speed" : mob.speed_stat,
			"sight range" : mob.sight_range_stat,
			"sight border requirement" : mob.sight_border_requirement_stat,
			"detect glow str" : mob.detect_glow_str_stat,
			"detect glow range" : mob.detect_glow_range_stat,
			"health" : mob.health_stat,
			"mana" : mob.mana_stat,
			"stamina" : mob.stamina_stat,
			"hunger" : mob.hunger_stat,
			"thirst" : mob.hunger_stat
		}

	def add_item(self, item):
		successful = True
		# check if space is available and mob is able to carry
		self.items.append(item)

		return successful, message

	def equip_item(self, item):
		if self.equipped_items[item.slot] is not None:
			return False, "You already have something equipped in that slot."

		# equip item
		self.equipped_items[item.slot] = item

		# add actions to mob's list of actions
		for action in item.actions:
			if action not in mob.actions:
				mob.actions.append(action)

		# add buffs and multipliers to mob's stats
		for buff_stat in item.buffs:
			self.stat_id[buff_stat].buffs.append(item.buffs[buff_stat])
			self.stat_id[buff_stat].recalc_max()

		for multiplier_stat in item.multipliers:
			self.stat_id[multiplier_stat].multipliers.append(item.multipliers[multiplier_stat])
			self.stat_id[buff_stat].recalc_max()

	def unequip_item(self, item):
		self.equipped_items[item.slot] = None

		# remove actions
		for action in item.actions:
			if action in mob.actions:
				mob.actions.remove(action)

		# remove buffs and multipliers to mob's stats
		for buff_stat in item.buffs:
			try:
				self.stat_id[buff_stat].buffs.remove(item.buffs[buff_stat])
			except ValueError:
				pass
			self.stat_id[buff_stat].recalc_max()

		for multiplier_stat in item.multipliers:
			try:
				self.stat_id[multiplier_stat].multipliers.remove(item.multipliers[multiplier_stat])
			except ValueError:
				pass
			self.stat_id[buff_stat].recalc_max()

### items
class item(object):
	def __init__(self, id_, name, plural, slot, icon, color, description, description_long,  weight, volume, buffs, multipliers):
		self.id_ = id_
		self.name = name
		self.plural = plural
		self.slot = slot
		self.icon = icon
		self.color = color
		self.description = description
		self.description_long = description_long
		self.weight = weight
		self.volume = volume
		self.buffs = buffs
		self.multipliers = multipliers

class melee_weapon(item):
	def __init__(self, id_, name, plural, slot, icon, color, description, description_long,  weight, volume, buffs, multipliers, base_damage, actions):
		item.__init__(self, id_, name, plural, slot, icon, color, description, description_long, weight, volume, buffs, multipliers)

		self.base_damage = base_damage
		self.actions = actions