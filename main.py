#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from gamehandler import *
from mainmenu import *
from bearlibterminal import terminal
from windowmod import *
import os

if __name__ == '__main__':
	os.chdir('.')
	
	Preferences = preferences()
	Preferences.load()

	Main_menu = main_menu()

	# initialize screen
	terminal.open()

	terminal.set("window: title = 'Roguelike Pre-Alpha 0.01', fullscreen=false, resizeable=true; font: FSEX300.ttf, size=16x16")
	terminal.set("window: size="+str(Preferences.w_xlen)+'x'+str(Preferences.w_ylen))
	terminal.set("output.vsync=false")

	terminal.set("entity font: FSEX300.ttf, size=16x16")
	terminal.set("message font: FSEX300.ttf, size=16x16")

	terminal.composition(terminal.TK_ON)

	# first refresh
	terminal.refresh()

	while True:
		start_game_mode, start_game_file = Main_menu.run_menu(Preferences)

		if start_game_mode == 'New':
			game = Game()
			game.gen_new_game()
		elif start_game_mode == 'Load':
			load_save = shelve.open(".\saves\\"+start_game_file, 'r')
			game = load_save['game']
			load_save.close()
		elif start_game_mode == 'Quit':
			break

		game.start_game(Preferences)
		# ask to save game or not
		ask_save_game_window = yes_or_no_popup('Save game? (y/n)', Preferences.w_ylen, Preferences.w_xlen)
		ask_save_game = ask_save_game_window.init()
		if ask_save_game:
			save_game = shelve.open(".\saves\\"+start_game_file, 'n')
			save_game['game'] = game
			save_game.close()

		terminal.clear()

	terminal.close()