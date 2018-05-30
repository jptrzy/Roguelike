# -*- coding: utf-8 -*- 

### items
class item(object):
	def __init__(self, type, id_, name, plural, slot, icon, color, description, description_long,  weight, volume, buffs, multipliers):
		self.type = type
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
	def __init__(self, type, id_, name, plural, slot, icon, color, description, description_long,  weight, volume, buffs, multipliers, base_damage, actions):
		item.__init__(self, type, id_, name, plural, slot, icon, color, description, description_long, weight, volume, buffs, multipliers)

		self.base_damage = base_damage
		self.actions = actions