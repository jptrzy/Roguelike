#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from bearlibterminal import terminal
from window import windows
import os

class preferences(object):
	def __init__(self, w_ylen=40, w_xlen=65): # ylenn 40 xlen 65
		self.w_ylen = w_ylen
		self.w_xlen = w_xlen

	def load(self):
		pass # later, replace __init__ with load

class choice(windows.window):
	def __init__(self, text, y, x, layer):
		windows.window.__init__(self, 3, len(text)+2, y, x, layer=layer)
		self.text = text
	def print_text(self):
		self.wprint(1, 1, self.text)

class main_menu(object):
	def __init__(self):
		pass

	def load_game(self, game):
		# takes a game object and "initializes" it with save data.
		pass

	def run_menu(self, preferences):
		self.preferences = preferences
		title = "Untitled Roguelike V.0.1"
		title_window = windows.window(1, len(title), preferences.w_ylen/4, preferences.w_xlen/2-len(title)/2)
		title_window.wprint(0, 0, title)

		self.active_popups = 0 # keeps track of popup layers so they don't interfere

		new_game_option = choice('New Game', int(float(preferences.w_ylen)/3*2), 0, layer=199)
		load_game_option = choice('Load Game', int(float(preferences.w_ylen)/3*2), 0, layer=199)
		quit_option = choice('Quit Game', int(float(preferences.w_ylen)/3*2), 0, layer=199)

		self.choices = [new_game_option, load_game_option, quit_option]
		self.choice = 0 # 0 is new_game_option, 1 is load_game_option

		self.recalc_option_positions()

		self.refresh_options()
		terminal.refresh()

		start_game = False

		while not start_game:
			proceed = True
			while proceed:
				while terminal.has_input() and proceed:
					uinput = terminal.read()
					if uinput == terminal.TK_LEFT:
						self.choice -= 1
						if self.choice < 0:
							self.choice = len(self.choices)-1
					elif uinput == terminal.TK_RIGHT:
						self.choice = (self.choice+1)%len(self.choices)
					elif uinput == terminal.TK_ENTER:
						proceed = False

					self.refresh_options()
					terminal.refresh()

			# process user choice

			# list of all save filenames with most recent first
			os.chdir('.\saves')
			saves = filter(os.path.isfile, os.listdir('.'))
			saves.sort(key=lambda x: os.path.getmtime(x))
			saves = saves[::-1]
			os.chdir('..')
			
			if self.choices[self.choice] == new_game_option:
				prompt_new_save_name = windows.text_input_popup("Enter a file name: ", preferences.w_ylen, preferences.w_xlen, activepopups=self.active_popups)
				new_save_file_name = prompt_new_save_name.init()
				if new_save_file_name:
					if new_save_file_name in saves:
						confirm_overwrite_window = windows.yes_or_no_popup("Save file exists. Overwrite? (y/n)", preferences.w_ylen, preferences.w_xlen, activepopups=self.active_popups)
						confirm_overwrite = confirm_overwrite_window.init()

						if confirm_overwrite:
							start_game = True
							start_game_inputs = ("New", new_save_file_name)
					else:
						start_game = True
						start_game_inputs = ("New", new_save_file_name)


			elif self.choices[self.choice] == load_game_option:
				num_loads = len(saves)
				if num_loads == 0:
					windows.pure_text_popup(["Error: No file exists.", [255,0,0]], preferences.w_ylen, preferences.w_xlen, activepopups=self.active_popups)
				else:
					load_file_name_prompt = windows.scroll_selection_popup("Select save file:", saves, preferences.w_ylen, preferences.w_xlen, activepopups=self.active_popups)
					load_file_name = load_file_name_prompt.init()
					if load_file_name != None:
						start_game = True
						start_game_inputs = ("Load", load_file_name)

			elif self.choices[self.choice] == quit_option:
				start_game = True
				start_game_inputs = ("Quit", None)

		terminal.refresh()
		title_window.clear()
		self.clear_options()
		return start_game_inputs

	def refresh_options(self):
		for choice in self.choices:
			choice.clear()
			if choice == self.choices[self.choice]:
				choice.fill(color=[100,100,100])
			choice.print_border()
			choice.print_text()

	def clear_options(self):
		for choice in self.choices:
			choice.clear()

	def recalc_option_positions(self):
		total_length = 0
		for choice in self.choices:
			total_length += len(choice.text) + 2

		remaining_spaces = self.preferences.w_xlen - total_length
		spacing_per_option = int(float(remaining_spaces) / (len(self.choices)+1))

		x_counter = spacing_per_option

		for choice in self.choices:
			choice.x = x_counter
			x_counter += spacing_per_option + len(choice.text) + 2
