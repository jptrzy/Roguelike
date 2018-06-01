#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from gamehandler import *
from mainmenu import *
from bearlibterminal import terminal
from window import windows
import gzip, cPickle
import os

if __name__ == '__main__':
	os.chdir('.')
	os.sys.path.append('.')

	# initialize screen
	terminal.open()
	terminal.set("window: title = 'Roguelike Pre-Alpha 0.01', resizeable=true; font: DejaVuSansMono-Bold.ttf, size=15x20")
	terminal.set("output.vsync=false")
	terminal.composition(terminal.TK_ON)
	
	Preferences = preferences('.\data\preferences.json')
	Preferences.recalc()

	Main_menu = main_menu()

	# first refresh
	terminal.refresh()

	while True:
		start_game_mode, start_game_file = Main_menu.run_menu(Preferences)

		if start_game_mode == 'New':
			game = Game()
			game.gen_new_game(Preferences)
		elif start_game_mode == 'Load':
			load_save = gzip.open(".\saves\\"+start_game_file+".dat", 'rb')
			game = cPickle.load(load_save)
			load_save.close()
		elif start_game_mode == 'Quit':
			break

		survived = game.start_game(Preferences)

		if survived:
			# ask to save game or not
			ask_save_game_window = windows.yes_or_no_popup('Save game? (y/n)', w_ylen=Preferences.w_ylen, w_xlen=Preferences.w_xlen, activepopups=Main_menu.active_popups)
			ask_save_game = ask_save_game_window.init()
			if ask_save_game:
				save_game = gzip.open(".\saves\\"+start_game_file+".dat", 'wb')
				cPickle.dump(game, save_game)
				save_game.close()
		else:
			# delete game file
			if os.path.isfile(".\saves\\"+start_game_file+".dat"):
				os.remove(".\saves\\"+start_game_file+".dat")

		terminal.clear()

	terminal.close()