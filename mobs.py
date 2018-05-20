# -*- coding: utf-8 -*- 
import tiles
import math
import bresenham
import a_star
import gradient
import random
import randomGen

import action

from windowmod import *

class stat(object):
	def __init__(self, max_amt, buffs=[], multipliers=[]):
		self.raw_max = max_amt
		self.buffs = buffs
		self.multipliers = multipliers

		self.recalc_max()


	def recalc_max(self):
		self.max = self.raw_max

		for add in self.buffs:
			self.max += add 

		for multiplier in self.multipliers:
			self.max = self.max * self.multipliers

		self.max = int(math.floor(self.max))

class dynamic_stat(stat):
	def __init__(self, max_amt, color_info, regen_rate=1, buffs=[], multipliers=[]):
		stat.__init__(self, max_amt, buffs, multipliers)
		self.color_info = color_info
		# initially start at max
		self.value = self.max

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
	def __init__(self, name, tile, health, speed, sight_range, stamina, hunger, thirst, mana, emit=False, go_thru_walls=False, sight_border_requirement=500, detect_glow_str=100, detect_glow_range=20):
		self.name = name
		self.tile = tile
		self.desc = self.tile.examine
		self.speed = stat(speed)
		self.sight_range = stat(sight_range)
		self.sight_border_requirement = sight_border_requirement
		self.detect_glow_str = detect_glow_str
		self.detect_glow_range = detect_glow_range
		
		# dynamic stats
		self.health = dynamic_stat(health, ([255, 0, 0], [255, 91, 91], [35, 0, 0]))
		self.mana = dynamic_stat(mana, ([43, 131, 255], [84, 175, 255], [0, 34, 89]))
		self.stamina = dynamic_stat(stamina, ([0, 175, 0], [73, 255, 73], [0, 50, 0]))
		self.hunger = dynamic_stat(hunger, ([255, 165, 0], [255, 199, 0], [33, 22, 0]))
		self.thirst = dynamic_stat(thirst, ([0, 216, 255], [142, 249, 255], [0, 55, 58]))

		self.dynam_stats = [self.health, self.mana, self.stamina, self.hunger, self.thirst]

		self.emit = emit
		self.go_thru_walls = go_thru_walls

		for dynam_stat in self.dynam_stats:
			for n in range(3):
				for i in range(3):
					dynam_stat.color_info[n][i] = int(0.7*dynam_stat.color_info[n][i])

	def move_to_cord(self, y, x):
		if not (y, x) in self.group.mob_lib:
			if (self.go_thru_walls) or ((not self.go_thru_walls) and (self.worldmap.check_passable(y, x))):
				self.remove()
				self.add(y, x)
				if self.emit:
					self.aura._move(y, x)

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
			if (self.go_thru_walls) or ((not self.go_thru_walls) and (self.worldmap.check_passable(y, x))):
				if self.emit:
					self.aura = self.tile.aura_maker.create_aura(self.worldmap, self.worldmap.aura_group, self.worldmap.glow_coords, self.FOV)
					self.aura._spawn(y, x)
				
				self.add(y, x)

				return True

		return False

	def get_sight_requirement(self, distance_from_mob):
		return float(self.sight_border_requirement/self.sight_range.max)*distance_from_mob

	def get_detect_glow_str(self, distance_from_mob):
		if distance_from_mob > self.detect_glow_range:
			return 0
		return -(float(self.detect_glow_str)/self.detect_glow_range)*distance_from_mob + self.detect_glow_str

class mob(living):
	def __init__(self, name, tile, health, speed, sight_range, stamina, hunger, thirst, mana, hostile, sense, determined, emit=False, pathfinding=True):
		living.__init__(self, name, tile, health, speed, sight_range, stamina, hunger, thirst, mana, emit)
		self.hostile = hostile
		self.sense = sense
		self.determined = determined # max number of checks in pathfinding
		self.pathfinding = pathfinding
		self.can_move = True

		self.noise_gen = randomGen.randomGenerator(scale=20)

		self.update_stage = 0

		self.actions = set([action.a_Walk, action.a_Sprint])

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

			if (d_from_player <= self.sense) or (d_from_player <= self.sight_range and bresenham.check_line((self.y, self.x), (game.me.y, game.me.x), game.world.blockable_coordinates)):
				if d_from_player <= 1.5:
					action.a_testAttack.prep(self, game.timer.time)
					self.action_args = (self, game.me.y, game.me.x, self.mob_group.mob_lib)

					return
				else:	
					if self.pathfinding:
						self.path = a_star.pathfind.find_path((self.y, self.x), (game.me.y, game.me.x), game.world, self.determined)
						if self.path:
							self.action_args = (self, self.path[1][0], self.path[1][1]) # replace y, x
							action.a_Walk.prep(self, game.timer.time)

							return

		# wander
		wander_direction = self.noise_gen.get_closest_direction(self.y, self.x)
		self.action_args = (self, wander_direction[0], wander_direction[1])

		action.a_Walk.prep(self, game.timer.time)

	def mob_spawn(self, y, x, worldmap, FOV, mob_group, time):
		if self.spawn(y, x, worldmap, FOV, mob_group):

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

	def re_add_chunk_group(self):
		self.mapy = self.worldmap.get_mapy(self.y)
		self.mapx = self.worldmap.get_mapx(self.x)
		
		try:
			self.mob_group.mobs[(self.mapy, self.mapx)].append(self)
		except KeyError:
			self.mob_group.mobs[(self.mapy, self.mapx)] = []
			self.mob_group.mobs[(self.mapy, self.mapx)].append(self)

	def move_to_cord(self, y, x):
		update_chunk = False
		if self.mapy != self.worldmap.get_mapy(y) or self.mapx != self.worldmap.get_mapx(x):
			self.mob_group.mobs[(self.mapy, self.mapx)].remove(self)
			update_chunk = True

		super(mob, self).move_to_cord(y, x) # changes mapy and mapx here
		if update_chunk:
			self.re_add_chunk_group()

	def die(self, game):
		self.remove()

		self.mob_group.mobs[(self.mapy, self.mapx)].remove(self)
		if self.emit:
			self.aura._remove_effect()
			self.aura._remove()
		self.mob_group.update(game)

class mob_maker(mob):
	def __init__(self, name, tile, health, speed, sight_range, stamina, hunger, thirst, mana, hostile, sense, determined, emit=False, pathfinding=True):
		mob.__init__(self, name, tile, health, speed, sight_range, stamina, hunger, thirst, mana, hostile, sense, determined, emit, pathfinding)

	def create(self, y, x, worldmap, FOV, mob_group, time):
		new_mob = mob(self.name, self.tile, self.health.max, self.speed.max, self.sight_range.max, self.stamina.max, self.hunger.max, self.thirst.max, self.mana.max, self.hostile, self.sense, self.determined, self.emit, self.pathfinding)
		new_mob.mob_spawn(y, x, worldmap, FOV, mob_group, time)
		return new_mob

class mob_group(object):
	def __init__(self):
		self.mobs = {}
		self.mob_set = set()
		self.mob_lib = {}

		self.check_coords = [(0,0),(0,1),(1,0),(1,1),(0,-1),(-1,0),(-1,-1),(1,-1),(-1,1)]

	def init_window(self, game_y_len, game_x_len):
		self.window = window(game_y_len - 27, 14, 1, game_x_len - 15)

	def recalc_win(self, game_y_len, game_x_len):
		self.window.resize(game_y_len - 27, 14)
		self.window.move(1, game_x_len - 15)

	def recalc_visible_mobs(self, game):
		self.visible_mobs = []

		for coord_check in self.check_coords:
			try:
				for mob in self.mobs[game.me.mapy + coord_check[0], game.me.mapx + coord_check[1]]:
					if (mob.y, mob.x) in game.world.visible_coords:
						mob.distance_from_player = game.world.distance_map[(mob.y, mob.x)]
						if game.world.get_glow_str(game, (mob.y, mob.x), game.timer.day_night_emit_str(), mob.distance_from_player, game.me) >= game.me.get_sight_requirement(mob.distance_from_player):
							self.visible_mobs.append(mob)
			except KeyError:
				pass

		self.visible_mobs.sort(key = lambda x: x.distance_from_player)

	def print_mob_data(self, game):
		self.window.clear()

		for i in range(min(len(self.visible_mobs), self.window.ylen)):
			current_mob = self.visible_mobs[i]
			health_bar = current_mob.health.get_stat_bar(self.window.xlen - 2)
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

#name, tile, health, speed, sight_range, stamina, hunger, thirst, mana, hostile, sense, emit=False, pathfinding=True
test_mob_tile = tiles.tile(u'T', [255,99,71], False, False, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus varius pharetra finibus. Fusce ac vehicula massa, eu dapibus leo. Praesent viverra, urna vitae tempus mattis, nisi felis venenatis ligula, ac tempus eros mi at orci. Aenean luctus auctor erat, non ornare elit mattis quis. Quisque eget mi in ligula consequat mattis. Sed tempor faucibus risus vitae ultricies. Integer at mauris ex. Praesent in nisl orci. Vivamus in placerat risus, vitae elementum neque. Nunc porta sapien sit amet orci efficitur, feugiat luctus felis vestibulum. Morbi viverra ante sed lectus imperdiet, at ornare ipsum mattis. Ut metus sapien, convallis eu porta et, volutpat a tellus. Suspendisse justo tortor, interdum quis elit eget, dictum consectetur felis. Ut vestibulum ultricies tortor. Nunc vitae neque bibendum, dignissim nulla egestas, consequat orci.', world_layer = 'mobs')
test_mob = mob_maker(name='a test mob', tile=test_mob_tile, health=100, speed=100, sight_range=20, stamina=100, hunger=100, thirst=100, mana=100, hostile=True, sense=10, determined=300)

test_light_mob_tile = tiles.light_tile(u'L', [0,0,0], False, False, 'a test light mob', True, 3, [249, 173, 34], 500, 0.5, world_layer='mobs')
test_light_mob = mob_maker(name='testlightmob1', tile=test_light_mob_tile, health=100, speed=100, sight_range=20, stamina=100, hunger=100, thirst=100, mana=100, hostile=True, sense=10, determined=300, emit=True)

test_speed_mob_tile = tiles.tile(u'ጿ', [142, 185, 255], False, False, 'a test speed mob', world_layer='mobs')
test_speed_mob = mob_maker(name='test speed mob', tile=test_speed_mob_tile, health=100, speed=200, sight_range=20, stamina=100, hunger=100, thirst=100, mana=100, hostile=True, sense=10, determined=300)

blind_mob_tile = tiles.tile('B', [142, 185, 255], False, False, 'a blind mob', world_layer = 'mobs')
test_blind_mob = mob_maker(name='blind test mob', tile=blind_mob_tile, health=100, speed=50, sight_range=3, stamina=100, hunger=100, thirst=100, mana=100, hostile=True, sense=5, determined=100)

determined_mob_tile = tiles.tile("D", [255, 0, 0], False, False, 'a determined mob', world_layer = 'mobs')
test_determined_mob = mob_maker(name='determined mob', tile=determined_mob_tile, health=100,speed=100,sight_range=100,stamina=100,hunger=100,thirst=100,mana=100,hostile=True,sense=100, determined=10000)