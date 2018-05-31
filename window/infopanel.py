# -*- coding: utf-8 -*- 
import math

from bearlibterminal import terminal
from windows import *
from message import *

class info_panel(object):
	def __init__(self, game):
		self.game = game
		self.window = window(game.preferences.w_ylen-2, 30-1, 1, game.preferences.w_xlen - 30, layer=180)

		self.line = ''
		for i in range(self.window.xlen):
			self.line += u'═'

		self.display_type = 'manual'

	def recalc_win(self, y_len, x_len, y, x):
		self.window.resize(y_len, x_len)
		self.window.move(y, x)
		self.line = ''
		for i in range(self.window.xlen):
			self.line += u'═'

	def recalc_info(self):
		distance = "%.2f" % math.hypot(self.game.me.y - self.check_y, self.game.me.x - self.check_x)
		s_add_message(convert_phrase_to_list('Distance: ' + str(distance)), self.window.xlen, self.add_new_title_row)
		if self.display_type == 'manual':
			self.visible = False
			if (self.check_y, self.check_x) in self.game.world.visible_coords:
				self.reset_print_info()
				distance_from_player = self.game.world.distance_map[(self.check_y, self.check_x)]
				if self.game.world.check_enough_light((self.check_y, self.check_x), distance_from_player, self.game.me):
					# print info
					self.prepare_tile_info()
					self.visible = True

			if not self.visible:
				s_add_message(convert_phrase_to_list('You cannot see this place.', [150,150,150]), self.window.xlen-1, self.add_new_row)
		else:
			if len(self.game.all_mobs.visible_mobs) > 0:
				self.reset_print_info()
				self.prepare_mob_info(self.check_mob)
			else:
				s_add_message(convert_phrase_to_list('You do not see any entities.',[150,150,150]), self.window.xlen-1, self.add_new_row)


		self.output_length = self.title_length + self.body_length

		if self.output_length <= self.window.ylen:
			self.scroll_input = False
		else:			
			if self.title_length <= self.window.ylen:
				self.scroll_input = True
			else:
				self.scroll_input = False

	def move_camera(self):
		self.prep_window()

		if self.display_type == 'auto':
			if len(self.game.all_mobs.visible_mobs) > 0:
				current_mob = self.game.all_mobs.visible_mobs[self.view_index]
				self.visible = True
				self.check_y = current_mob.y
				self.check_x = current_mob.x
				self.check_mob = current_mob
			else:
				pass

		self.recalc_info()

	def prompt(self, check_y, check_x):
		self.view_index = 0

		self.check_y = check_y
		self.check_x = check_x

		self.move_camera()
		self._print()

		proceed = True

		while proceed:
			while terminal.has_input() and proceed:
				self.dir = terminal.read()
				if terminal.check(terminal.TK_SHIFT):
					self.dir_shift = True
				else:
					self.dir_shift = False

				if not self.advance_input():
					proceed = False

	def advance_input(self):
		if self.dir in self.game.commandframe.move:
			if self.dir in [terminal.TK_UP, terminal.TK_DOWN] and self.scroll_input:
				# advance scroll
				self.use_scroll_input()
				terminal.refresh()
			else:
				if self.display_type == 'manual':
					self.check_y += self.game.commandframe.move[self.dir][0]
					self.check_x += self.game.commandframe.move[self.dir][1]
					self.move_camera()
					self._print()

		elif self.dir == terminal.TK_TAB:
			if self.display_type == 'manual':
				self.display_type = 'auto'
			else:
				self.display_type = 'manual'
			self.move_camera()
			self._print()

		elif self.dir in [terminal.TK_COMMA, terminal.TK_PERIOD] and self.dir_shift:
			if self.display_type == 'auto':
				if self.dir == terminal.TK_COMMA:
					self.view_index -= 1
				else:
					self.view_index += 1

				self.view_index = self.view_index % len(self.game.all_mobs.visible_mobs)
				self.move_camera()
				self._print()

		elif self.dir == terminal.TK_X:
			if self.visible:
				self.print_expanded_tile_info()


		elif self.dir == terminal.TK_ESCAPE:
			return False

		return True

	def reset_print_info(self):
		tiles = self.game.world.layers.get_tiles(self.check_y, self.check_x)
		self.print_info = {} # dictionary: { layer name : { tileid : [tileobj, count] , ... }, ... }

		for tile in tiles:
			if tile.worldlayer.name not in self.print_info:
				self.print_info[tile.worldlayer.name] = {tile.id_ : [tile, 1]}
			else:
				if tile.id_ in self.print_info[tile.worldlayer.name]:
					self.print_info[tile.worldlayer.name][tile.id_][1] += 1
				else:
					self.print_info[tile.worldlayer.name][tile.id_] = [tile, 1]

	def prepare_tile_info(self):
		for print_layer in self.print_info:
			print_message = [(print_layer+":", (255,255,255))]
			for tile_id in self.print_info[print_layer]:
				tile = self.print_info[print_layer][tile_id][0]
				tile_count = self.print_info[print_layer][tile_id][1]

				if tile_count > 1:
					print_message.append((tile.plural, (255,255,255)))
					print_message.append(("("+str(tile_count)+")", (255,255,255)))
				else:
					print_message.append((tile.name, (255,255,255)))

			s_add_message(custom_convert_phrase_to_list(print_message), self.window.xlen-1, self.add_new_row)

	def prepare_mob_info(self, mob):
		# set up print
		health_bar_color = mob.health_stat.get_stat_bar(self.window.xlen-1)
		health_bar = []
		for i in range(len(health_bar_color)):
			health_bar.append([u'█', health_bar_color[i]])

		s_add_message(convert_phrase_to_list(mob.name, mob.tile.color), self.window.xlen-1, self.add_new_title_row)
		s_add_message(health_bar, self.window.xlen-1, self.add_new_title_row)
		s_add_message(convert_phrase_to_list(self.line), self.window.xlen, self.add_new_title_row)

		s_add_message(convert_phrase_to_list(mob.description), self.window.xlen-1, self.add_new_row)

		self.output_length = self.title_length + self.body_length

	def print_expanded_tile_info(self):
		print_message = []
		for print_layer in self.print_info:
			print_message.append((print_layer+": \\n", (255,255,255)))
			for tile_id in self.print_info[print_layer]:
				tile = self.print_info[print_layer][tile_id][0]
				tile_count = self.print_info[print_layer][tile_id][1]
				if tile_count > 1:
					print_message.append((tile.plural, (175,175,175)))
					print_message.append(("("+str(tile_count)+")", (175,175,175)))
				else:
					print_message.append((tile.name, (175,175,175)))
				print_message.append(("\\n", (255,255,255)))
				print_message.append((tile.description,  (100,100,100)))
				if tile.description_long is not None:
					print_message.append((tile.description_long, (100,100,100)))

				print_message.append(("\\n", (255,255,255)))

		expanded_tile_info = pure_text_popup(print_message, game=self.game, title="Enter/Esc to close.", exit=None)
		expanded_tile_info.init()


	def _print(self):
		self.game.world.view_move(self.check_y, self.check_x)
		self.game.world.print_indicator(self.check_y, self.check_x)

		if not self.scroll_input:
			self.print_title()
			self.print_body(0, self.body_length-1)
		else:
			self.min_row = 0
			self.max_row = self.window.ylen - self.title_length - 1
			self.print_scroll_input()

		terminal.refresh()

	def prep_window(self):
		self.window.clear()
		self.window.fill()
		self.title_row_list = []
		self.row_list = []
		self.body_length = 0
		self.title_length = 0

		self.scroll_input = False

	def open(self, panel):
		self.prep_window()
		panel.add_win(self.window)
		panel.recalc_borders()
		panel.print_borders()


	def exit(self, panel):
		self.window.clear()
		panel.remove_win(self.window)
		panel.recalc_borders()
		panel.print_borders()

	def print_body(self, min_row, max_row):
		body_length = max_row - min_row + 1
		for i in range(body_length):
			row = self.row_list[min_row + i]
			self.print_row(row, self.title_length+i)

	def print_scroll(self, min_row, max_row):
		body_length = max_row - min_row + 1
		self.window.put(self.title_length, self.window.xlen-1, u'█', color=(100,100,100))
		self.window.put(self.title_length+body_length-1, self.window.xlen-1, u'█', color=(100,100,100))

		self.window.put(self.title_length, self.window.xlen-1, u'˄')
		self.window.put(self.title_length+body_length-1, self.window.xlen-1, u'˅')

		bar_length = body_length - 2
		scroll_bar_length = int(round((float(body_length) / self.body_length)*bar_length))

		for i in range(bar_length):
			self.window.put(self.title_length+1+i, self.window.xlen-1, u'▒', color=(100,100,100))

		start_scroll_bar_index = int(round((float(min_row) / self.body_length)*bar_length))

		if start_scroll_bar_index + scroll_bar_length > bar_length:
			start_scroll_bar_index -= 1

		for i in range(scroll_bar_length):
			self.window.put(self.title_length+1+i+start_scroll_bar_index, self.window.xlen-1, u'█')

		######################
		#					  -----------
		#
		#-------------------------------- index: title_length
		#
		#
		#
		#					  ----------- index: title_length + body_length 
		######################

	def use_scroll_input(self):
		if self.dir == terminal.TK_UP:
			if self.min_row - 1 >= 0:
				self.min_row -= 1
				self.max_row -= 1
		elif self.dir == terminal.TK_DOWN:
			if self.max_row + 1 <= self.body_length - 1:
				self.min_row += 1
				self.max_row += 1

		self.print_scroll_input()

	def print_scroll_input(self):

		self.window.clear()
		self.window.fill()
		self.print_title()

		self.print_body(self.min_row, self.max_row)
		self.print_scroll(self.min_row, self.max_row)

	def print_title(self):
		for i in range(self.title_length):
			row = self.title_row_list[i]
			self.print_row(row, i)

	def print_row(self, row, y_index):
		for n in range(self.window.xlen):
			try:
				self.window.put(y_index, n, '[font=message]'+row[n][0]+'[/font]', row[n][1])
			except IndexError:
				pass

	def add_new_row(self, row):
		self.row_list.append(row)
		self.body_length += 1

	def add_new_title_row(self, row):
		self.title_row_list.append(row)
		self.title_length += 1