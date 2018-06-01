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

	def get_keybind_display_info(self, inventory):
		self.keybinds = {}

		self.keybinds['d'] = ["drop", (255,255,255)]

		self.keybinds['e'] = ["equip", (100,100,100)]
		self.keybinds['u'] = ["unequip", (100,100,100)]

		if self.slot is not None:
			if inventory.equipped_items[self.slot] is None:
				self.keybinds['e'][1] = (255,255,255)
			else:
				if inventory.equipped_items[self.slot] == self:
					self.keybinds['u'][1] = (255,255,255)
					self.keybinds['d'][1] = (100,100,100)

		return self.keybinds

	def process_modification(self, prompt_char, inventory):
		successful = True
		message = None

		if prompt_char == 'd':
			if self.slot is None or inventory.equipped_items[self.slot] != self:
				inventory.del_item(self)
			else:
				successful = False
				message = "You must unequip the item before dropping it!"

		if prompt_char == 'e':
			successful, message = inventory.equip_item(self)

		if prompt_char == 'u':
			successful, message = inventory.unequip_item(self)

		return successful, message


class melee_weapon(item):
	def __init__(self, type, id_, name, plural, slot, icon, color, description, description_long,  weight, volume, buffs, multipliers, base_damage, actions):
		item.__init__(self, type, id_, name, plural, slot, icon, color, description, description_long, weight, volume, buffs, multipliers)

		self.base_damage = base_damage
		self.actions = actions

	def process_modification(self, prompt_char, inventory):
		successful, message = super(melee_weapon, self).process_modification(prompt_char, inventory)

		return successful, message