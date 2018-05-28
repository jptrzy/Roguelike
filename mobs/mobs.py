# -*- coding: utf-8 -*- 
from tiles_data import tiles
import math
from include import bresenham
from include import a_star
from include import gradient
import random
from include import randomGen

import action

from window import windows
import json
import items

class stat(object):
	def __init__(self, max_amt, buffs=[], multipliers=[]):
		# initially start at max
		self.value = max_amt
		self.raw_max = max_amt
		self.max = max_amt
		self.buffs = buffs
		self.multipliers = multipliers

		self.recalc_max()

	def recalc_max(self):
		self.max = self.raw_max

		for buff in self.buffs:
			self.max += buff 

		for multiplier in self.multipliers:
			self.max = self.max * multiplier

		self.value = min(self.value, self.max)

class dynamic_stat(stat):
	def __init__(self, max_amt, color_info, regen_rate=0.1, buffs=[], multipliers=[]):
		stat.__init__(self, max_amt, buffs, multipliers)
		self.color_info = color_info
		self.regen_rate = regen_rate

	def alter(self, amount):
		self.value = min(max(0, self.value + amount), self.max)

	def get_stat_bar(self, length):
		bar_info = [] # return [color1, color2, ... ]
		info_1 = gradient.linear_gradient(self.color_info[0], self.color_info[1], length // 2)
		for i in range(length // 2):
			bar_info.append(info_1[i])
		if length % 2 == 1:
			bar_info.append(info_1[-1])
		info_1 = info_1[::-1]
		for i in range(length // 2):
			bar_info.append(info_1[i])
		
		color_length = int(math.floor((float(self.value) / self.max) * length))
		
		for n in range(length-color_length):
			bar_info[n+color_length] = self.color_info[2]

		return bar_info


class living(object):
	def __init__(self, id_, name, plural, description, description_long, health, speed, carry_weight, carry_volume, sight_range, stamina, hunger, thirst, mana, ethereal, tile, aura, emit, sight_border_requirement, detect_glow_str, detect_glow_range, actions):
		self.id_ = id_
		self.name = name
		self.plural = plural
		self.description = description
		self.description_long = description_long
		
		self.tile = tile
		self.aura = aura
		self.emit = emit

		# minimum amount of lighting required to see at sight range of mob
		self.sight_border_requirement_stat = stat(sight_border_requirement)
		# pseudo glow from mob based on how far they can see into the dark
		self.detect_glow_str_stat = stat(detect_glow_str) 
		# maximum distance where pseudo glow will still be considered
		self.detect_glow_range_stat = stat(detect_glow_range)

		# stats
		self.speed_stat = stat(speed)
		self.sight_range_stat = stat(sight_range)
		self.carry_weight_stat = stat(carry_weight)
		self.carry_volume_stat = stat(carry_volume)

		# dynamic stats
		self.health_stat = dynamic_stat(health, ([255, 0, 0], [255, 91, 91], [35, 0, 0]))
		self.mana_stat = dynamic_stat(mana, ([43, 131, 255], [84, 175, 255], [0, 34, 89]))
		self.stamina_stat = dynamic_stat(stamina, ([0, 175, 0], [73, 255, 73], [0, 50, 0]))
		self.hunger_stat = dynamic_stat(hunger, ([255, 165, 0], [255, 199, 0], [33, 22, 0]))
		self.thirst_stat = dynamic_stat(thirst, ([0, 216, 255], [142, 249, 255], [0, 55, 58]))

		self.dynam_stats = [self.health_stat, self.mana_stat, self.stamina_stat, self.hunger_stat, self.thirst_stat]

		self.emit = emit
		self.ethereal = ethereal

		for dynam_stat in self.dynam_stats:
			for n in range(3):
				for i in range(3):
					dynam_stat.color_info[n][i] = int(0.7*dynam_stat.color_info[n][i])

		# inventory
		self.inventory = items.inventory(self)

		# actions
		self.actions = actions
	@property
	def carry_weight(self):
		return self.carry_weight_stat.value
	
	@property
	def carry_volume(self):
		return self.carry_volume_stat.value
	

	@property
	def speed(self):
		return self.speed_stat.value

	@property
	def sight_range(self):
		return self.sight_range_stat.value
	
	@property
	def sight_border_requirement(self):
		return self.sight_border_requirement_stat.value

	@property
	def detect_glow_str(self):
		return self.detect_glow_str_stat.value

	@property
	def detect_glow_range(self):
		return self.detect_glow_range_stat.value
	
	@property
	def health(self):
		return self.health_stat.value

	@property
	def mana(self):
		return self.mana_stat.value

	@property
	def stamina(self):
		return self.stamina_stat.value

	@property
	def hunger(self):
		return self.hunger_stat.value

	@property
	def thirst(self):
		return self.thirst_stat.value

	def add_item(self, item_id, game):
		new_item = game.item_generator.create_item_from_id(item_id)
		successful, message = self.inventory.add_item(new_item)

		return successful, message

	def equip_item(self, item):
		successful, message = self.inventory.equip_item(item)

	def move_to_cord(self, y, x):
		successful = False
		if not (y, x) in self.group.mob_lib:
			if (self.ethereal) or ((not self.ethereal) and (self.worldmap.check_passable(y, x))):
				old_mapy = self.mapy
				old_mapx = self.mapx
				self.remove()
				self.add(y, x)
				self.re_calculate_chunk_info(old_mapy, old_mapx)
				if self.emit:
					self.aura._move(y, x)
				successful = True

		return successful

	def remove(self):
		self.worldmap.layers.delete_tile(self.y, self.x, self.tile)
		del self.group.mob_lib[(self.y, self.x)]

	def add(self, y, x):
		self.y = y
		self.x = x

		self.mapy = self.worldmap.get_mapy(y)
		self.mapx = self.worldmap.get_mapx(x)

		self.worldmap.layers.add_tile(self.y, self.x, self.tile)
		self.group.mob_lib[(y, x)] = self

	def spawn(self, y, x, worldmap, FOV, group):
		self.group = group
		self.worldmap = worldmap
		self.FOV = FOV
		#check if place is spawnable
		if not (y, x) in self.group.mob_lib:
			if (self.ethereal) or ((not self.ethereal) and (self.worldmap.check_passable(y, x))):
				if self.emit:
					self.aura._init(worldmap, worldmap.aura_group, worldmap.glow_coords, FOV)
					self.aura._spawn(y, x)
				
				self.add(y, x)

				return True

		return False

	def get_sight_requirement(self, distance_from_mob):
		# requirement to see
		return float(self.sight_border_requirement/self.sight_range)*distance_from_mob

	def get_detect_glow_str(self, distance_from_mob):
		if distance_from_mob > self.detect_glow_range:
			return 0
		return -(float(self.detect_glow_str)/self.detect_glow_range)*distance_from_mob + self.detect_glow_str

class mob(living):
	def __init__(self, id_, name, plural, description, description_long, health, speed, carry_weight, carry_volume,sight_range, stamina, hunger, thirst, mana, sense_range, determined, pathfinding, hostile, ethereal, tile, aura, emit, sight_border_requirement, detect_glow_str, detect_glow_range, actions):
		living.__init__(self, id_, name, plural, description, description_long, health, speed, carry_weight, carry_volume, sight_range, stamina, hunger, thirst, mana, ethereal, tile, aura, emit, sight_border_requirement, detect_glow_str, detect_glow_range, actions)

		self.sense_range = stat(sense_range)
		self.determined = stat(determined) # max number of checks in pathfinding
		self.pathfinding = pathfinding
		self.hostile = hostile

		self.can_move = True

		self.noise_gen = randomGen.randomGenerator(scale=20)

		self.update_stage = 0

		self.current_action = None

	def check_update_time(self, next_update_time):
		if next_update_time >= self.next_update_time:
			return True
		else:
			return False

	def update(self, game):
		#timerp print "mob at update stage " + str(self.update_stage)
		game.timer.change_time(self.next_update_time, game)

		if self.update_stage == 0:
			self.prepare_update(game)
			return

		# advance action
		elif self.update_stage == 1:
			self.current_action.do(game, *self.action_args)
			#timerp print "mob did action. next mob update time is " + str(self.next_update_time)
			#timerp print "-----"

		elif self.update_stage == 2: # just finished action
			# get new action
			self.prepare_update(game)
			#timerp print "mob got new action. next mob update time is " + str(self.next_update_time)

	def prepare_update(self, game):
		# prepare new action

		if self.can_move:
			d_from_player = math.floor(((self.y - game.me.y)**2 + (self.x - game.me.x)**2)**0.5)

			if (d_from_player <= self.sense_range) or (d_from_player <= self.sight_range and bresenham.check_line((self.y, self.x), (game.me.y, game.me.x), game.world.sight_blockable_coordinates)):
				if game.world.check_enough_light((self.y, self.x), d_from_player, self):			
					if d_from_player <= 1.5:
						action = game.action_generator.get_action_from_id("punch")
						action.prep(self, game.timer.time)
						self.action_args = (self, game.me.y, game.me.x, self.mob_group.mob_lib)

						return
					else:	
						if self.pathfinding:
							self.path = a_star.pathfind.find_path((self.y, self.x), (game.me.y, game.me.x), game.world, self.determined)
							if self.path:
								self.action_args = (self, self.path[1][0], self.path[1][1]) # replace y, x
								action = game.action_generator.get_action_from_id("walk")
								action.prep(self, game.timer.time)

								return

		# wander
		wander_direction = self.noise_gen.get_closest_direction(self.y, self.x)
		self.action_args = (self, wander_direction[0], wander_direction[1])

		action = game.action_generator.get_action_from_id("walk")
		action.prep(self, game.timer.time)

	def spawn(self, y, x, worldmap, FOV, mob_group, time):
		if super(mob, self).spawn(y, x, worldmap, FOV, mob_group):

			self.mob_group = mob_group

			self.mapy = self.worldmap.get_mapy(self.y)
			self.mapx = self.worldmap.get_mapx(self.x)

			try:
				self.mob_group.mobs[(self.mapy, self.mapx)].append(self)
			except KeyError:
				self.mob_group.mobs[(self.mapy, self.mapx)] = []
				self.mob_group.mobs[(self.mapy, self.mapx)].append(self)

			self.mob_group.mob_set.add(self)

			self.next_update_time = time

			return True

		return False

	def re_add_chunk_group(self):
		self.mapy = self.worldmap.get_mapy(self.y)
		self.mapx = self.worldmap.get_mapx(self.x)
		
		try:
			self.mob_group.mobs[(self.mapy, self.mapx)].append(self)
		except KeyError:
			self.mob_group.mobs[(self.mapy, self.mapx)] = []
			self.mob_group.mobs[(self.mapy, self.mapx)].append(self)

	def re_calculate_chunk_info(self, old_mapy, old_mapx):
		if old_mapy != self.worldmap.get_mapy(self.y) or old_mapx != self.worldmap.get_mapx(self.x):
			self.mob_group.mobs[(old_mapy, old_mapx)].remove(self)
			self.re_add_chunk_group()

	def die(self, game):
		self.remove()

		self.mob_group.mobs[(self.mapy, self.mapx)].remove(self)
		if self.emit:
			self.aura._remove_effect()
			self.aura._remove()
		self.mob_group.update(game)

class mob_group(object):
	def __init__(self):
		self.mobs = {}
		self.mob_set = set()
		self.mob_lib = {}

		self.check_coords = [(0,0),(0,1),(1,0),(1,1),(0,-1),(-1,0),(-1,-1),(1,-1),(-1,1)]

	def init_window(self, y_len, x_len, y, x):
		self.window = windows.window(y_len, x_len, y, x)

	def recalc_win(self, y_len, x_len, y, x):
		self.window.resize(y_len, x_len)
		self.window.move(y, x)

	def recalc_visible_mobs(self, game):
		self.visible_mobs = []

		for coord_check in self.check_coords:
			try:
				for mob in self.mobs[game.me.mapy + coord_check[0], game.me.mapx + coord_check[1]]:
					if (mob.y, mob.x) in game.world.visible_coords:
						mob.distance_from_player = game.world.distance_map[(mob.y, mob.x)]
						if game.world.get_glow_str((mob.y, mob.x), mob.distance_from_player, game.me) >= game.me.get_sight_requirement(mob.distance_from_player):
							self.visible_mobs.append(mob)
			except KeyError:
				pass

		self.visible_mobs.sort(key = lambda x: x.distance_from_player)

	def print_mob_data(self, game):
		self.window.clear()

		for i in range(min(len(self.visible_mobs), self.window.ylen)):
			current_mob = self.visible_mobs[i]
			health_bar = current_mob.health_stat.get_stat_bar(self.window.xlen - 2)
			for n in range(self.window.xlen - 2):
				self.window.put(i, n+2, u'█', health_bar[n])

			self.window.put(i, 0, current_mob.tile.icon, current_mob.tile.color)
			self.window.put(i, 1, ':')
			if len(current_mob.name) <= self.window.xlen - 2:
				self.window.wprint(i, 2, current_mob.name)
			else:
				for n in range(self.window.xlen - 4):
					self.window.put(i, 2+n, current_mob.name[n])
				self.window.wprint(i, 2+self.window.xlen - 4, '..')

	def expand_mob_info(self, game):
		pass

	def update(self, game):
		while self.refresh_actives(game) > 0:
			if not game.proceed:
				return
			self.active_mobs.sort(key = lambda x: x.next_update_time)
			if self.active_mobs[0].check_update_time(game.next_update_time):
				self.active_mobs[0].update(game)
			else:
				return

	def refresh_actives(self, game):
		self.active_mobs = []  # list of mobs updated before player input

		for coord_check in self.check_coords:
			try:
				chunk = self.mobs[(game.me.mapy + coord_check[0], game.me.mapx + coord_check[1])]
				for mob in chunk:
					if mob.check_update_time(game.next_update_time):
						self.active_mobs.append(mob)
			except KeyError:
				pass

		return len(self.active_mobs)