#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#main game file
from map import *
import tiles
import time
import chunk
import weather
from command import *
import rpas

from bearlibterminal import terminal

from character import *
from timecounter import *
from messagewindow import *
from animation import *
from infopanel import *
from windowmod import *

import shelve


class Game(object):
	def __init__(self):
		pass

	def mainloop(self):
		self.proceed = True
		# start printing screen
		self.me.printstats()
		self.world.view(self)

		self.bg_windows.recalc_borders()
		self.bg_windows.print_borders()
		
		terminal.refresh()

		# initial message
		self.message_panel.custom_add_phrase([('Welcome to this', [255,255,255]), ('roguelike^', [255,255,255]), ('!^', [178,34,34])])
		self.message_panel.add_phrase('Version 0.01 Pre-Alpha Unreleased Testing.', [150,150,150])
		self.message_panel.custom_add_phrase([('Press', [150,150,150]), ('\\', [255,255,255]), ('to input', [150,150,150]), ('wizard', [112, 45, 206]), ('commands.^', [150,150,150])])
		self.message_panel.print_messages()

		self.world.view(self)
		
#		while True:
#			if terminal.has_input():
#				self.commandframe.command(terminal.read(), self)
#			self.anim.anim_loop(self)

		while self.proceed:
			total_time = time.clock()
			while self.proceed and terminal.has_input():
				uinput = terminal.read()
				self.commandframe.command(uinput, self)
			#p print("total time: --- %s seconds ---" % (time.clock() - total_time))

		self.close()

	def close(self):
		pass

	def start_game(self, preferences):
		self.preferences = preferences
		# assume game has already loaded/created
		self.world.recalc_win(self.preferences.w_ylen, self.preferences.w_xlen)
		self.me.window_init(self.preferences.w_ylen, self.preferences.w_xlen)
		self.all_mobs.recalc_visible_mobs(self)
		self.all_mobs.init_window(self.preferences.w_ylen, self.preferences.w_xlen)
		self.all_mobs.print_mob_data(self)
		self.message_panel.curs_init(self.preferences.w_ylen, self.preferences.w_xlen)
		self.info_panel = info_panel(self.preferences.w_ylen, self.preferences.w_xlen)

		self.bg_windows = panel_windows()
		self.bg_windows.recalc_win(self.preferences.w_ylen, self.preferences.w_xlen, 0, 0, 150)
		self.bg_windows.add_win(self.me.window)
		self.bg_windows.add_win(self.all_mobs.window)
		self.bg_windows.add_win(self.world.windows)
		self.bg_windows.add_win(self.message_panel.window)

		self.left_panel = panel_windows()
		self.right_panel = panel_windows()

		self.left_panel.add_win(self.me.window)
		self.right_panel.add_win(self.all_mobs.window)

		self.activepopups = 0

		self.mainloop()

	def gen_new_game(self):
		### generate new world
		self.world = chunk.worldmap(100, 100, 'World')
		self.world.initworld()

		### init FOV handler
		self.FOV = rpas.FOV_handler()

		#--------------------------------Convention: timer(1000)---------------------------------
		self.timer = timer(10000)
		# -----------------------------------------------------------------------------------------------------------------------finish
		self.timer.cursinit(0,0)
#		weather.currentweather = weather.rain
#		self.anim = anim_handler()

		### create new character
		self.all_mobs = mob_group()

		player_tile = tiles.tile('[font=entity]@[/font]', [200, 200, 200], True, False, 'This is you.')
		self.me = character('bobb', player_tile, 100, 100, 30, 100, 100, 100, 100, False)

		self.me.mapy = self.world.get_mapy(5000)
		self.me.mapx = self.world.get_mapx(5000)
		
		self.world.recalcloc(self.me.mapy, self.me.mapx)
		
		self.me.spawn(5000, 5000, self.world, self.FOV, self.all_mobs)

		### init command, time
		self.commandframe = commands()

		### init message scrn
		self.message_panel = message_panel()

	def update_view(self):
		self.world.view(self)
		self.all_mobs.print_mob_data(self)

	def recalc_input(self, time_amount):
		self.timer.recalc(time_amount, self)
		self.all_mobs.update(self)

	def update_screen(self):
		self.world.view(self)
		self.all_mobs.print_mob_data(self)
		self.timer.vprint()
		self.me.printstats()

		terminal.refresh()

	def update(self, time_increase=0):
		# only use this function when advancing time for player.

		self.next_update_time = self.timer.time + time_increase
		#timerp print "======================"
		#timerp print ">> current time: " + str(self.timer.time)+". next update time at: " + str(self.next_update_time)
		self.all_mobs.update(self)
		
		self.all_mobs.recalc_visible_mobs(self)
		self.timer.change_time(self.next_update_time, self)
		#timerp print "======================"

	def refresh(self, time_increase=0):
		pass
