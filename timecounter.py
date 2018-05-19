### time counter
from bearlibterminal import terminal
from windowmod import *

import gradient

import math

class timer(object):
	def __init__(self, hours):
		self.maxhours = hours
		self.last_updated_time = 0
		self.time = 0
		self.hours = 0
		self.days = 0
		self.daynight = 'day'

		self.hour_interval = float(self.maxhours) / 24

		# init colors
		count = 0
		self.c_dawn = gradient.linear_gradient([23,0,150], [255,204,0], int(self.hour_interval * 3))
		count += int(self.hour_interval * 3)
		self.c_day  = gradient.linear_gradient([255,204,0], [254, 255, 212], int(self.hour_interval * 4))
		count += int(self.hour_interval * 4)
		self.c_day2 = gradient.linear_gradient([254, 255, 212], [255,190,77], int(self.hour_interval * 5))
		count += int(self.hour_interval * 5)
		self.c_evening = gradient.linear_gradient([255,190,77], [23,0,150], int(self.hour_interval * 3))
		count += int(self.hour_interval * 3)
		self.c_night = gradient.linear_gradient([23,0,150], [12,0,77], int(self.hour_interval * 4))
		count += int(self.hour_interval * 4)
		self.c_night2 = gradient.linear_gradient([12,0,77], [23,0,150], self.maxhours - count)

		self.colorofday = tuple(self.c_dawn + self.c_day + self.c_day2 + self.c_evening + self.c_night + self.c_night2)


	def cursinit(self, game_w_ylen, game_w_xlen):
		self.window = window(1, 50, 50, 0, layer=200)

	def change_time(self, changed_time, game):
		self.time = float(changed_time)
		time_elapsed = self.time - self.last_updated_time

		# update
		for mob in game.all_mobs.mob_set | set([game.me]):
			for dynam_stat in mob.dynam_stats:
				dynam_stat.alter(dynam_stat.regen_rate*time_elapsed)


		self.hours = int(self.time)

		if self.hours >= self.maxhours:
			magnitude = self.hours // self.maxhours
			self.hours = self.hours - self.maxhours * magnitude
			self.days += magnitude


		self.last_updated_time = self.time

		#timerp print "> time updated to: " + str(self.time)

		#self.hours = 0 #unshade for always night


	def day_night_color(self):
		return self.colorofday[self.hours]

	def day_night_dark(self):
		return [0,0,0]

	def day_night_emit_str(self):
		check = float(self.hours)/self.hour_interval
		if 0 <= check <= 3:
			return int(200 + (check)*(1800/3))
		elif check <= 12:
			return 2000
		elif check <= 15:
			return int(2000 - (check - 12)*(1800/3))
		else:
			return 200
		
		
	def day_night_color_str(self):
		check = float(self.hours)/self.hour_interval
		#0 - 23
		if 0 <= check <= 3:
			#'morning'
			return 0.6 - (check)*(0.5/3)
		elif check <= 12:	#2 hour morning
			#'day'
			return 0.1
		elif check <= 15: # 2 hour evening
			#'evening'
			return 0.1 + (check - 12)*(0.5/3)
		else:
			#'night'
			return 0.6

	def vprint(self):
		self.window.clear()
		self.window.put(0, 0, 'Hours: '+str(self.hours)+', Days: '+str(self.days)+'. It is '+self.daynight+'.', self.day_night_color())