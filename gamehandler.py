#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#main game file
from tiles_data import tiles
import time
import chunk
import weather
from input_handler import command
from include import rpas

from bearlibterminal import terminal

from mobs import character
from mobs import mobs
from timecounter import *
from window import messagepanel
from animation import *
from window import infopanel
from window import windows
import generators

import shelve


class Game(object):
	def __init__(self):
		pass

	def mainloop(self):
		self.proceed = True
		# start printing screen
		self.all_mobs.print_mob_data(self)
		self.me.printstats()
		self.world.view()

		self.bg_windows.recalc_borders()
		self.bg_windows.print_borders()
		
		terminal.refresh()

		# initial message
		self.message_panel.custom_add_phrase([('Welcome to this', [255,255,255]), ('roguelike^', [255,255,255]), ('!^', [178,34,34])])
		self.message_panel.add_phrase('Version 0.01 Pre-Alpha Unreleased Testing.', [150,150,150])
		self.message_panel.custom_add_phrase([('Press', [150,150,150]), ('\\', [255,255,255]), ('to input', [150,150,150]), ('wizard', [112, 45, 206]), ('commands.^', [150,150,150])])
		self.message_panel.print_messages()

		self.world.view()
		
#		while True:
#			if terminal.has_input():
#				self.commandframe.command(terminal.read(), self)
#			self.anim.anim_loop(self)

		while self.proceed:
			#p total_time = time.clock()
			while self.proceed and terminal.has_input():
				uinput = terminal.read()
				self.commandframe.command(uinput, self)
			#p print("total time: --- %s seconds ---" % (time.clock() - total_time))

		return not self.die

	def game_over(self):
		self.die = True
		self.proceed = False
		windows.pure_text_popup("Rest in peace.", self.preferences.w_ylen, self.preferences.w_xlen, activepopups=self.activepopups)

	def start_game(self, preferences):
		self.die = False
		self.preferences = preferences
		# assume game has already loaded/created

		# initialize windows
		left_display_panel_length = 22
		right_display_panel_length = 22
		message_panel_length = 10
		"""
		main windows: 
			world display (layers 0 to 100):

			message window (layer 0):

			left info panel (layer 0):

			right info panel:

			main display panel: layer 150


		overlayed info panel (layer 180):

		borders: layer 200

		popup windows: layer 201+

		"""
		self.all_mobs.recalc_visible_mobs(self)
		self.info_panel = infopanel.info_panel(self)
		self.bg_windows = windows.panel_windows()

		self.world.recalc_win(self.preferences.w_ylen-message_panel_length-3, self.preferences.w_xlen-left_display_panel_length-1-right_display_panel_length-1, 1, left_display_panel_length+1)
		self.me.window_init(6, left_display_panel_length-1, 1, 1)  # health, mana, stamina, hunger+thirst
		self.all_mobs.init_window(self.preferences.w_ylen-27, right_display_panel_length-1, 1, self.preferences.w_xlen-right_display_panel_length)
		self.message_panel.curs_init(message_panel_length, self.preferences.w_xlen-left_display_panel_length-1-right_display_panel_length-1, self.preferences.w_ylen-message_panel_length-1, left_display_panel_length+1)
		self.bg_windows.recalc_win(self.preferences.w_ylen, self.preferences.w_xlen, 0, 0, 150)
		self.info_panel.recalc_win(self.preferences.w_ylen-2, right_display_panel_length-1, 1, self.preferences.w_xlen - right_display_panel_length)
		
		self.bg_windows.add_win(self.me.window)
		self.bg_windows.add_win(self.all_mobs.window)
		self.bg_windows.add_win(self.world.layers.windows)
		self.bg_windows.add_win(self.message_panel.window)

		self.left_panel = windows.panel_windows()
		self.right_panel = windows.panel_windows()

		self.left_panel.add_win(self.me.window)
		self.right_panel.add_win(self.all_mobs.window)

		self.activepopups = 0

		return self.mainloop()

	def gen_new_game(self, preferences):
		terminal.clear()
		terminal.refresh()

		self.preferences = preferences

		# initialize object generators
		self.tile_generator = generators.tile_generator(self)
		self.aura_generator = generators.aura_generator(self)
		self.mob_generator = generators.mob_generator(self)
		self.tile_generator.re_path("./data/tiles.json")
		self.mob_generator.re_path("./data/mobs.json")

		### generate new world
		self.world = chunk.worldmap(self, 100, 100, 'World')
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
		self.all_mobs = mobs.mob_group()

		while True:
			player_name_prompt = windows.text_input_popup("Enter your name:", preferences.w_ylen, preferences.w_xlen)
			player_name = player_name_prompt.init()
			if player_name:
				break

		player_tile = tiles.tile(id_='player',name=player_name, plural=player_name, icon='@', description='This is you.', description_long=None, color=[200,200,200], world_layer='mobs', blocks_sight=False, blocks_path=True, ethereal=False)
		self.me = character.character(id_='player',name=player_name, plural='Players', description='This is you.', description_long='This is you', health=100, speed=100, sight_range=30, stamina=100, hunger=100, thirst=100, mana=100, ethereal=False, tile=player_tile, aura=None, emit=False, sight_border_requirement=500, detect_glow_str=50, detect_glow_range=20)

		self.me.mapy = self.world.get_mapy(5000)
		self.me.mapx = self.world.get_mapx(5000)
		
		self.world.recalcloc(self.me.mapy, self.me.mapx)
		
		self.me.spawn(5000, 5000, self.world, self.FOV, self.all_mobs)

		### init command, time
		self.commandframe = command.commands_handler()

		### init message scrn
		self.message_panel = messagepanel.message_panel()

	def update_view(self):
		if self.proceed:
			self.world.view()
			self.all_mobs.print_mob_data(self)

	def recalc_input(self, time_amount):
		self.timer.recalc(time_amount, self)
		self.all_mobs.update(self)

	def update_screen(self):
		if self.proceed:
			#p self.world.start_time = time.clock()
			#p total_view_time_start = time.clock()
			#p FOV_time, render_time, print_time = self.world.view(self)
			self.world.view()
			#p total_render_time = FOV_time+render_time+print_time
			self.all_mobs.recalc_visible_mobs(self)
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