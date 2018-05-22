# -*- coding: utf-8 -*- 
### character
from window import windows
from mobs import *
from tiles_data import tiles
from include import gradient
import string
import math

class inv(object):
	def __init__(self, space=100, items = []):
		self.space = space
		self.items = items

class character(living):
	def __init__(self, id_, name, plural, description, description_long, health, speed, sight_range, stamina,hunger, thirst, mana, ethereal, tile, aura, emit, sight_border_requirement=500, detect_glow_str=100,detect_glow_range=20):
		living.__init__(self, id_, name, plural, description, description_long, health, speed, sight_range, stamina, hunger, thirst, mana, ethereal, tile, aura, emit, sight_border_requirement, detect_glow_str, detect_glow_range)

		self.inv = inv()

	def window_init(self, game_y_len, game_x_len):
		self.window = windows.window(6, 14, 1, 1)  # health, mana, stamina, hunger+thirst

	def recalc_win(self, game_y_len, game_x_len):
		self.window.move(1, 1)
		self.printstats()

	def printstats(self):
		self.window.clear()
		# print name
		self.window.wprint(0, 6-len(self.name)/2, str(self.name))
		# print stats
		for i in range(len(self.dynam_stats)):
			dynam_stat = self.dynam_stats[i]
			stat_bar = dynam_stat.get_stat_bar(self.window.xlen)
			for n in range(self.window.xlen):
				self.window.put(1+i, n, u'█', stat_bar[n])

			stat_amt = str(dynam_stat.value) + '/' + str(dynam_stat.max)

			self.window.wprint(1+i, self.window.xlen // 2 -len(stat_amt)/2, stat_amt)

	def die(self, game):
		print "RIP"
		game.proceed = False