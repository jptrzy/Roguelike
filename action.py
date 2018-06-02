# -*- coding: utf-8 -*- 

class Action(object):
	def __init__(self, id_, name, cast_time, recover_time, cost):
		self.id_ = id_
		self.name = name
		self.cast_time = cast_time
		self.recover_time = recover_time
		self.cost = cost

	def _calc_prep_time(self, speed):
		return float(self.cast_time) / (float(speed) / 100)

	def _calc_recover_time(self, speed):
		return float(self.recover_time) / (float(speed) / 100)

	def prep(self, mob, current_time):
		mob.next_update_time = current_time + self._calc_prep_time(mob.speed)
		mob.current_action = self
		mob.update_stage = 1

	@staticmethod
	def get_stat_lookup(mob, stat_id):
		stat_ids = {
			"stamina" : mob.stamina_stat,
			"carry weight" : mob.carry_weight_stat,
			"carry volume" : mob.carry_volume_stat,
			"speed" : mob.speed_stat,
			"sight range" : mob.sight_range_stat,
			"sight border requirement" : mob.sight_border_requirement_stat,
			"detect glow str" : mob.detect_glow_str_stat,
			"detect glow range" : mob.detect_glow_range_stat,
			"health" : mob.health_stat,
			"mana" : mob.mana_stat,
			"stamina" : mob.stamina_stat,
			"hunger" : mob.hunger_stat,
			"thirst" : mob.thirst_stat
		}

		return stat_ids[stat_id] 

class Item_Action(Action):
	def __init__(self, id_, name, cast_time, recover_time, cost):
		Action.__init__(self, id_, name, cast_time, recover_time, cost)

	def prep(self, mob, current_time, item):
		mob.next_update_time = current_time + float(self.cast_time) / (float(mob.speed) / 100) # make something to do with item weight here
		mob.current_action = self
		mob.update_stage = 1

	def _calc_recover_time(self, speed, item):
		return float(self.cast_time) / (float(speed) / 100) # make something to do with item weight here

	def _calc_stamina_cost(self, mob, item, prompt_char):
		return 10 # make something to do with item weight

	def do(self, game, mob, item, prompt_char): # type can be "equip", "unequip", "drop", etc., anything that has to do with moving items around in the mob's inventory
		if mob.stamina - self._calc_stamina_cost(mob, item) < 0:
			return_message = "Not enough stamina!"
			successful = False
		else:
			successful, return_message = item.do_modification(prompt_char, mob.inventory, mob, game)

		mob.update_stage = 2
		mob.next_update_time = game.timer.time + self._calc_recover_time(mob.speed, item, prompt_char)

		return successful, return_message

class Movement_Action(Action):
	def __init__(self, id_, name, cast_time, recover_time, cost, range):
		Action.__init__(self, id_, name, cast_time, recover_time, cost)
		self.range = range

	def do(self, game, mob, y, x):
		successful = True
		return_message = None

		for stat_id in self.cost:
			if self.get_stat_lookup(mob, stat_id).value - self.cost[stat_id] < 0:
				return_message = "Not enough " + str(stat_id) + "!"
				successful = False
				break

		if successful:
			if not mob.move_to_cord(y, x):
				successful = False
				return_message = "Something blocked your path!"
			else:
				for stat_id in self.cost:
					self.get_stat_lookup(mob, stat_id).alter(-self.cost[stat_id])
		
		mob.update_stage = 2

		# might want to change this to something different if not successful (ex. only half the recover time?)
		mob.next_update_time = game.timer.time + self._calc_recover_time(mob.speed)

		return successful, return_message

class Melee_Attack(Action):
	def __init__(self, id_, name, cast_time, recover_time, cost, damage):
		Action.__init__(self, id_, name, cast_time, recover_time, cost)
		self.damage = damage

	def do(self, game, mob, attack_y, attack_x, mob_dictionary):
		successful = True
		return_message = None

		if self not in mob.actions:
			successful = False
			return_message = "You lack the equipment or knowledge required to perform the attack!"
		else:
			for stat_id in self.cost:
				if self.get_stat_lookup(mob, stat_id).value - self.cost[stat_id] < 0:
					return_message = "Not enough " + str(stat_id) + "!"
					successful = False
					break

			if successful:
				try:
					attack_this_mob = mob_dictionary[(attack_y, attack_x)]
					attack_this_mob.health_stat.alter(-self.damage)
					if attack_this_mob.health == 0:
						attack_this_mob.die(game)

				except KeyError:
					successful = False
					return_message = "You don't hit anything!"


				for stat_id in self.cost:
					self.get_stat_lookup(mob, stat_id).alter(-self.cost[stat_id])

		mob.update_stage = 2

		# might want to change this to something different if not successful (ex. only half the recover time?)
		mob.next_update_time = game.timer.time + self._calc_recover_time(mob.speed)

		return successful, return_message