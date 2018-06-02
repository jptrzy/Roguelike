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

	def add_item(self, item):
		successful = True
		message = None
		# check if space is available and mob is able to carry
		duplicate = False
		for check_item in self.items:
			if check_item == item:
				self.items[check_item] += 1
				duplicate = True

		if not duplicate:
			self.items[item] = 1

		return successful, message

	def check_del_item_conditions(self, item):
		successful = True
		message = None
		try:
			self.items[item]
		except KeyError:
			message = "Item not found!"
			successful = False

		return successful, message

	def del_item(self, item):
		self.items[item] -= 1
		if self.items[item] < 1:
			del self.items[item]

	def drop_item(self, item, y, x, game):
		# deletes the item from inventory and drops it onto the world
		successful, message = self.check_del_item_conditions(item)

		if successful:
			tile = game.tile_generator.create_item_drop_tile(item, y, x)
			if not game.world.layers.check_add_tile_conditions(y, x, tile):
				successful = False
				message = "There's not enough space to drop the item!"
			else:
				self.del_item(item)
				game.world.layers.add_tile(y, x, tile)

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
					self.mob.stat_ids[buff_stat].buffs.append(item.buffs[buff_stat])
					self.mob.stat_ids[buff_stat].recalc_max()

				for multiplier_stat in item.multipliers:
					self.mob.stat_ids[multiplier_stat].multipliers.append(item.multipliers[multiplier_stat])
					self.mob.stat_ids[buff_stat].recalc_max()

		return successful, message

	def unequip_item(self, item):
		successful = True
		message = None

		if self.equipped_items[item.slot] is not None:
			if self.equipped_items[item.slot] == item:		
				self.equipped_items[item.slot] = None

				# remove actions
				for action in item.actions:
					if action in self.mob.actions:
						self.mob.actions.remove(action)

				# remove buffs and multipliers to mob's stats
				for buff_stat in item.buffs:
					try:
						self.mob.stat_ids[buff_stat].buffs.remove(item.buffs[buff_stat])
					except ValueError:
						pass
					self.mob.stat_ids[buff_stat].recalc_max()

				for multiplier_stat in item.multipliers:
					try:
						self.mob.stat_ids[multiplier_stat].multipliers.remove(item.multipliers[multiplier_stat])
					except ValueError:
						pass
					self.mob.stat_ids[buff_stat].recalc_max()
			else:
				successful = False
				message = "That item is not equipped."
		else:
			successful = False
			message = "There is nothing to unequip in that slot."

		return successful, message
