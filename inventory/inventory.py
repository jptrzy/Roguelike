# -*- coding: utf-8 -*- 

### inventory
"""
slots:
primary weapon
"""

class inventory(object):
	def __init__(self, mob):
		self.mob = mob
		self.weight = 0
		self.volume = 0
		self.items = {} # dictionary : { item_obj : count } (equipped and unequipped)
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
			"thirst" : mob.thirst_stat
		}

	def add_item(self, item):
		successful = True
		message = None
		# check if space is available and mob is able to carry
		duplicate = False
		for check_item in self.items:
			if check_item.id_ == item.id_:
				self.items[check_item] += 1
				duplicate = True

		if not duplicate:
			self.items[item] = 1

		return successful, message

	def del_item(self, item):
		successful = True
		message = None

		try:
			self.items[item] -= 1
			if self.items[item] < 1:
				del self.items[item]

		except KeyError:
			message = "Item not found!"
			successful = False

		return successful, message

	def equip_item(self, item):
		successful = True
		message = None
		if item.slot is None:
			successful = False
			message = "You cannot equip this item."
		else:
			if self.equipped_items[item.slot] is not None:
				successful = False 
				message = "You already have something equipped in that slot."
			else:
				# equip item
				self.equipped_items[item.slot] = item

				# add actions to mob's list of actions
				for action in item.actions:
					if action not in self.mob.actions:
						self.mob.actions.append(action)

				# add buffs and multipliers to mob's stats
				for buff_stat in item.buffs:
					self.stat_ids[buff_stat].buffs.append(item.buffs[buff_stat])
					self.stat_ids[buff_stat].recalc_max()

				for multiplier_stat in item.multipliers:
					self.stat_ids[multiplier_stat].multipliers.append(item.multipliers[multiplier_stat])
					self.stat_ids[buff_stat].recalc_max()

		return successful, message

	def unequip_item(self, item):
		self.equipped_items[item.slot] = None

		# remove actions
		for action in item.actions:
			if action in self.mob.actions:
				self.mob.actions.remove(action)

		# remove buffs and multipliers to mob's stats
		for buff_stat in item.buffs:
			try:
				self.stat_ids[buff_stat].buffs.remove(item.buffs[buff_stat])
			except ValueError:
				pass
			self.stat_ids[buff_stat].recalc_max()

		for multiplier_stat in item.multipliers:
			try:
				self.stat_ids[multiplier_stat].multipliers.remove(item.multipliers[multiplier_stat])
			except ValueError:
				pass
			self.stat_ids[buff_stat].recalc_max()