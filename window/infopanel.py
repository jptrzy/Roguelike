# -*- coding: utf-8 -*- 
import math

from bearlibterminal import terminal
from windows import *
from message import *

class info_panel(object):
	def __init__(self, game_y_len, game_x_len):
		self.window = window(game_y_len-2, 14, 1, game_x_len - 15, layer=180)

		self.line = ''
		for i in range(self.window.xlen):
			self.line += u'═'

		self.display_type = 'manual'

	def recalc_win(self, game_y_len, game_x_len):
		self.window.resize(game_y_len-2, 14)
		self.window.move(1, game_x_len - 15)
		self.line = ''
		for i in range(self.window.xlen):
			self.line += u'═'

	def recalc_info(self, y, x, game):
		distance = "%.2f" % math.hypot(game.me.y - y, game.me.x - x)
		s_add_message(convert_phrase_to_list('Distance: ' + str(distance)), self.window.xlen, self.add_new_title_row)
		if self.display_type == 'manual':
			visible = False
			if (y, x) in game.world.visible_coords:
				distance_from_player = game.world.distance_map[(y, x)]
				if game.world.check_enough_light((y, x), distance_from_player, game.me):
					# print info
					self.prepare_tile_info(y, x, game.world)

					# check for entities
					for visible_mob in game.all_mobs.visible_mobs:
						if y == visible_mob.y and x == visible_mob.x:
							s_add_message(custom_convert_phrase_to_list([('entities:', [255,255,255]), (visible_mob.name+'^',visible_mob.tile.color)]), self.window.xlen-1, self.add_new_row)

					visible = True

			if not visible:
				s_add_message(convert_phrase_to_list('You cannot see this place.', [150,150,150]), self.window.xlen-1, self.add_new_row)
		else:
			if len(game.all_mobs.visible_mobs) > 0:
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


	def move_camera(self, game):
		self.prep_window()

		if self.display_type == 'auto':
			if len(game.all_mobs.visible_mobs) > 0:
				current_mob = game.all_mobs.visible_mobs[self.view_index]
				self.check_y = current_mob.y
				self.check_x = current_mob.x
				self.check_mob = current_mob
			else:
				pass

		self.recalc_info(self.check_y, self.check_x, game)

	def prompt(self, game, check_y, check_x):
		self.view_index = 0

		self.check_y = check_y
		self.check_x = check_x

		self.move_camera(game)
		self._print(game)

		proceed = True

		while proceed:
			while terminal.has_input() and proceed:
				self.dir = terminal.read()
				if terminal.check(terminal.TK_SHIFT):
					self.dir_shift = True
				else:
					self.dir_shift = False

				if not self.advance_input(game):
					proceed = False

	def advance_input(self, game):
		if self.dir in game.commandframe.move:
			if self.dir in [terminal.TK_UP, terminal.TK_DOWN] and self.scroll_input:
				# advance scroll
				self.use_scroll_input()
				terminal.refresh()
			else:
				if self.display_type == 'manual':
					self.check_y += game.commandframe.move[self.dir][0]
					self.check_x += game.commandframe.move[self.dir][1]
					self.move_camera(game)
					self._print(game)

		elif self.dir == terminal.TK_TAB:
			if self.display_type == 'manual':
				self.display_type = 'auto'
			else:
				self.display_type = 'manual'
			self.move_camera(game)
			self._print(game)

		elif self.dir in [terminal.TK_COMMA, terminal.TK_PERIOD] and self.dir_shift:
			if self.display_type == 'auto':
				if self.dir == terminal.TK_COMMA:
					self.view_index -= 1
				else:
					self.view_index += 1

				self.view_index = self.view_index % len(game.all_mobs.visible_mobs)
				self.move_camera(game)
				self._print(game)


		elif self.dir == terminal.TK_ESCAPE:
			return False

		return True

	def prepare_tile_info(self, y, x, worldmap):
		tiles = worldmap.layers.get_tiles(y, x)
		print_info = {} # dictionary: { layer name : [tile1, ... ], ... }

		for tile in tiles:
			if tile.worldlayer.name != 'mobs':
				if tile.worldlayer.name not in print_info:
					print_info[tile.worldlayer.name] = [tile]
				else:
					print_info[tile.worldlayer.name].append(tile)

		for print_layer in print_info:
			print_message = [(print_layer+":", (255,255,255))]
			for tile in print_info[print_layer]:
				print_message.append((tile.description, tile.color))

			s_add_message(custom_convert_phrase_to_list(print_message), self.window.xlen-1, self.add_new_row)

	def prepare_mob_info(self, mob):
		# set up print
		health_bar_color = mob.health.get_stat_bar(self.window.xlen-1)
		health_bar = []
		for i in range(len(health_bar_color)):
			health_bar.append([u'█', health_bar_color[i]])

		s_add_message(convert_phrase_to_list(mob.name, mob.tile.color), self.window.xlen-1, self.add_new_title_row)
		s_add_message(health_bar, self.window.xlen-1, self.add_new_title_row)
		s_add_message(convert_phrase_to_list(self.line), self.window.xlen, self.add_new_title_row)

		s_add_message(convert_phrase_to_list(mob.description), self.window.xlen-1, self.add_new_row)

		self.output_length = self.title_length + self.body_length

	def _print(self, game):
		game.world.view_move(self.check_y, self.check_x)
		game.world.print_indicator(self.check_y, self.check_x)

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