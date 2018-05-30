# -*- coding: utf-8 -*- 
from bearlibterminal import terminal
from window import windows
from window import message
import math

### inventory
"""
slots:
primary weapon
"""

class inventory_window(windows.popup):
	def __init__(self, inventory, game):
		"""
				╔════════════════════════════════════════════════════════════════════════════════════╗
				║TITLE MESSAGE (inventory)                                                           ║
				║════════════════════════════════════════════════════════════════════════════════════║
				║Weapons:                                       ^   Equipped:                        ║
				║Option 17 Option 17 Option 17 Option 17 Option ▒   Primary weapon:                  ║
				║17  Option 17 Option 17  (highlighted)         ▒   sword                            ║
				║Option 18                                      ▒                                    ║
				║Armor:                                         █                                    ║
				║Option 20                                      ˅                                    ║
				╚════════════════════════════════════════════════════════════════════════════════════╝
		"""		
		self.inventory = inventory

		self.game_y_len = game.preferences.w_ylen
		self.game_x_len = game.preferences.w_xlen

		self.selection_column = "items" # "items" or "equipped"

		self.row_width = 30
		self.max_rows = 7

		self.items_large_window = False
		self.equipped_items_large_window = False

		self.activepopups = game.activepopups

	class item_option(object):
		def __init__(self, item, count):
			self.item = item
			self.count = count
			
			if self.count == 1:
				self.string = self.item.name
			else:
				self.string = self.item.plural + " (" + str(self.count) + ")"
			
			self.start_row = 0
			self.end_row = 0

	def init(self):
		self.item_option_index = 0
		self.equipped_option_index = 0

		self.initialize_window()
		self.prepare_window()
		self.refresh_window()

		terminal.refresh()

		self.proceed = True

		while self.proceed:
			while terminal.has_input() and self.proceed:
				self.get_next_char()

		# finished response
		self.close()
		terminal.refresh()

		if self.item_option_index is None or self.equipped_option_index is None:
			return None
		else:
			if self.selection_column == "items":
				if self.no_items:
					return None
				return self.item_options[self.item_option_index]
			else:
				if self.no_equipped_items:
					return None
				return self.equipped_items_options[self.equipped_option_index]

	def get_next_char(self):
		char = terminal.read()

		if char in [terminal.TK_UP, terminal.TK_DOWN]:
			if char == terminal.TK_DOWN:
				if self.selection_column == "items":
					if self.item_option_index + 1 < len(self.item_options):
						self.item_option_index += 1
						self.recalc_min_max_rows()
				else:
					if self.equipped_option_index + 1 < len(self.equipped_items_options):
						self.equipped_option_index += 1
						self.recalc_min_max_rows()
			else:
				if self.selection_column == "items":
					if self.item_option_index - 1 >= 0:
						self.item_option_index -= 1
						self.recalc_min_max_rows()
				else:
					if self.equipped_option_index - 1 >= 0:
						self.equipped_option_index -= 1
						self.recalc_min_max_rows()
		elif char in [terminal.TK_TAB, terminal.TK_LEFT, terminal.TK_RIGHT]:
			if self.selection_column == "items":
				self.selection_column = "equipped"
			else:
				self.selection_column = "items"

		elif char == terminal.TK_ENTER:
			self.proceed = False
			return

		elif char == terminal.TK_ESCAPE:
			self.item_option_index = None
			self.equipped_option_index  = None
			self.proceed = False
			return

		self.refresh_window()
		terminal.refresh()

	def recalc_min_max_rows(self):
		if self.selection_column == "items":
			selected_option = self.item_options[self.item_option_index]

			if selected_option.end_row < self.body_row_display_length:
				self.items_min_row = 0
				self.items_max_row = min(self.item_row_length - 1, self.body_row_display_length - 1)
			else:
				self.items_max_row = selected_option.end_row
				self.items_min_row = self.items_max_row - self.body_row_display_length + 1
		else:
			selected_option = self.equipped_items_options[self.equipped_option_index]

			if selected_option.end_row < self.body_row_display_length:
				self.equipped_items_min_row = 0
				self.equipped_items_max_row = min(self.equipped_items_row_length - 1, self.body_row_display_length - 1)
			else:
				self.equipped_items_max_row = selected_option.end_row
				self.equipped_items_min_row = self.equipped_items_max_row - self.body_row_display_length + 1

	def initialize_window(self):
		# add title
		self.title_row_length = 0
		self.title_row_list = []

		self.title = "Inventory: " + str(self.inventory.weight) + "/" + str(self.inventory.mob.carry_weight) +"  "+ str(self.inventory.volume) + "/" + str(self.inventory.mob.carry_volume)
		message.s_add_message(message.convert_phrase_to_list(self.title), self.row_width*2+2, self.add_new_title_row)

		# add item options
		item_options_unordered = []

		for item in self.inventory.items:
			item_options_unordered.append(self.item_option(item, self.inventory.items[item]))

		## group items together by type
		item_options_grouped = {}

		for option in item_options_unordered:
			try:
				item_options_grouped[option.item.type].append(option)
			except KeyError:
				item_options_grouped[option.item.type] = [option]

		## merge options into list ordered by item type
		self.item_options = []

		for option_type, option_list in item_options_grouped.iteritems():
			self.item_options += option_list

		## add item option rows
		self.item_row_length = 0
		self.items_row_list = []

		current_item_type = ''
		for option in self.item_options:
			# check if new type
			if option.item.type != current_item_type:
				message.s_add_message(message.convert_phrase_to_list(option.item.type), self.row_width, self.add_new_item_row)
				current_item_type = option.item.type

			option.start_row = self.item_row_length
			message.s_add_message(message.convert_phrase_to_list(option.string), self.row_width, self.add_new_item_row)
			option.end_row = self.item_row_length - 1

		self.no_items = (len(self.item_options) == 0)

		# add equipped items
		self.equipped_items_row_length = 0
		self.equipped_items_row_list = []
		self.equipped_items_options = []

		for equipment_slot in self.inventory.equipped_items:
			equipped_item = self.inventory.equipped_items[equipment_slot]
			if equipped_item is not None:
				message.s_add_message(message.convert_phrase_to_list(equipment_slot), self.row_width, self.add_new_equipped_item_row)
				equipped_item_option = self.item_option(equipped_item, 1)
				equipped_item_option.start_row = self.equipped_items_row_length
				message.s_add_message(message.convert_phrase_to_list(equipped_item_option.item.name), self.row_width, self.add_new_equipped_item_row)
				equipped_item_option.end_row = self.equipped_items_row_length - 1
				self.equipped_items_options.append(equipped_item_option)

		self.no_equipped_items = (len(self.equipped_items_options) == 0)

	def add_new_title_row(self, row):
		self.title_row_list.append(row)
		self.title_row_length += 1

	def add_new_item_row(self, row):
		self.items_row_list.append(row)
		self.item_row_length += 1

		if self.item_row_length + self.title_row_length > self.max_rows:
			self.items_large_window = True

	def add_new_equipped_item_row(self, row):
		self.equipped_items_row_list.append(row)
		self.equipped_items_row_length += 1

		if self.equipped_items_row_length + self.title_row_length > self.max_rows:
			self.equipped_items_large_window = True

	def prepare_window(self):
		self.body_row_display_length = self.max_rows-self.title_row_length

		self.items_min_row = 0
		self.items_max_row = min(self.item_row_length - 1, self.body_row_display_length - 1)

		self.equipped_items_min_row = 0
		self.equipped_items_max_row = min(self.equipped_items_row_length - 1, self.body_row_display_length - 1)

		windows.popup.__init__(self, self.body_row_display_length+2+self.title_row_length, self.row_width*2+2+2, self.game_y_len/2-(self.body_row_display_length+self.title_row_length+2)/2, self.game_x_len/2-(self.row_width*2+2+2)/2, self.activepopups)

	def refresh_window(self):
		self.window.clear()
		self.window.fill(color=(230,0,0,0))
		self.window.print_border()

		self.print_highlight()
		self.print_body()
		self.print_title()

	def print_highlight(self, color=(230,0, 83, 216)):
		if self.selection_column == "items":
			if not self.no_items:
				selection_option = self.item_options[self.item_option_index]
				highlight_min_row = selection_option.start_row
				highlight_max_row = selection_option.end_row
				for i in range(highlight_max_row - highlight_min_row + 1):
					y_index = i+1+self.title_row_length+highlight_min_row-self.items_min_row
					self.window.w_clear(y_index, 1, self.row_width, 1)
					self.window.wprint(y_index, 1, u'█'*self.row_width, color)
		else:
			if not self.no_equipped_items:
				selection_option = self.equipped_items_options[self.equipped_option_index]
				highlight_min_row = selection_option.start_row
				highlight_max_row = selection_option.end_row
				for i in range(highlight_max_row - highlight_min_row + 1):
					y_index = i+1+self.title_row_length+highlight_min_row-self.equipped_items_min_row
					self.window.w_clear(y_index, self.row_width+3, self.row_width, 1)
					self.window.wprint(y_index, self.row_width+3, u'█'*self.row_width, color)

	def print_row(self, row, y_index, x_index):
		for data_pair in row:
			char = data_pair[0]
			color = data_pair[1]
			self.window.put(y_index, x_index, char, color)
			x_index += 1

	def print_title(self):
		for i in range(self.title_row_length):
			row = self.title_row_list[i]
			self.print_row(row, i+1, 1)

	def print_body(self):
		if not self.no_items:
			for i in range(self.items_max_row - self.items_min_row + 1):
				row = self.items_row_list[self.items_min_row+i]
				self.print_row(row, i+1+self.title_row_length, 1)

			if self.items_large_window:
				self.items_print_scroll()

		if not self.no_equipped_items:
			for i in range(self.equipped_items_max_row - self.equipped_items_min_row + 1):
				row = self.equipped_items_row_list[self.equipped_items_min_row+i]
				self.print_row(row, i+1+self.title_row_length, 1+self.row_width+2)

			if self.equipped_items_large_window:
				self.equipped_items_print_scroll()

	def items_print_scroll(self):
		bar_length = self.body_row_display_length-2
		scroll_bar_length = int(round((float(bar_length) / self.item_row_length)*bar_length))+1

		self.window.put(1+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))
		self.window.put(1+self.title_row_length, self.row_width+1, '^')
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width+1, u'˅')

		for i in range(bar_length):
			self.window.w_clear(2+i+self.title_row_length, self.row_width+1)
			self.window.put(2+i+self.title_row_length, self.row_width+1, u'█', color=(230,0,0,0))

		start_scroll_bar_index = int(math.ceil((float(self.items_min_row) / self.item_row_length)*bar_length))

		if start_scroll_bar_index + scroll_bar_length > bar_length:
			start_scroll_bar_index -= 1

		for i in range(scroll_bar_length):
			self.window.put(start_scroll_bar_index+i+2+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))

	def equipped_items_print_scroll(self):
		bar_length = self.body_row_display_length-2
		scroll_bar_length = int(round((float(bar_length) / self.equipped_items_row_length)*bar_length))+1

		self.window.put(1+self.title_row_length, self.row_width*2+2, u'█', color=(100,100,100))
		self.window.put(1+self.title_row_length, self.row_width*2+2, '^')
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width*2+2, u'█', color=(100,100,100))
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width*2+2, u'˅')

		for i in range(bar_length):
			self.window.w_clear(2+i+self.title_row_length, self.row_width*2+2)
			self.window.put(2+i+self.title_row_length, self.row_width*2+2, u'█', color=(230,0,0,0))

		start_scroll_bar_index = int(math.ceil((float(self.equipped_items_min_row) / self.equipped_item_row_length)*bar_length))

		if start_scroll_bar_index + scroll_bar_length > bar_length:
			start_scroll_bar_index -= 1

		for i in range(scroll_bar_length):
			self.window.put(start_scroll_bar_index+i+2+self.title_row_length, self.row_width*2+2, u'█', color=(100,100,100))

	def close(self):
		self.window.clear()
		self.activepopups -= 1

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