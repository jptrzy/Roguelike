# -*- coding: utf-8 -*- 

class Action(object):
	def __init__(self, id_, name, cast_time, recover_time, stamina_cost):
		self.id_ = id_
		self.name = name
		self.cast_time = cast_time
		self.recover_time = recover_time
		self.stamina_cost = stamina_cost

	def _calc_prep_time(self, speed):
		return float(self.cast_time) / (float(speed) / 100)

	def _calc_recover_time(self, speed):
		return float(self.recover_time) / (float(speed) / 100)

	def prep(self, mob, current_time):
		mob.next_update_time = current_time + self._calc_prep_time(mob.speed)
		mob.current_action = self
		mob.update_stage = 1

class Movement_Action(Action):
	def __init__(self, id_, name, cast_time, recover_time, stamina_cost, range):
		Action.__init__(self, id_, name, cast_time, recover_time, stamina_cost)
		self.range = range

	def do(self, game, mob, y, x):
		successful = False
		return_message = None

		if mob.stamina - self.stamina_cost > 0:
			if mob.move_to_cord(y, x):
				successful = True
				mob.stamina_stat.alter(-self.stamina_cost)
			else:
				return_message = "Something blocked your path!"
		else:
			return_message = "Not enough stamina!"
		
		mob.update_stage = 2

		# might want to change this to something different if not successful (ex. only half the recover time?)
		mob.next_update_time = game.timer.time + self._calc_recover_time(mob.speed)

		return successful, return_message

class Melee_Attack(Action):
	def __init__(self, id_, name, cast_time, recover_time, stamina_cost, damage):
		Action.__init__(self, id_, name, cast_time, recover_time, stamina_cost)
		self.damage = damage

	def do(self, game, mob, attack_y, attack_x, mob_dictionary):
		successful = True
		return_message = None

		if self not in mob.actions:
			successful = False
			return_message = "You lack the equipment or knowledge required to perform the attack!"
		else:
			if mob.stamina - self.stamina_cost > 0:
				try:
					attack_this_mob = mob_dictionary[(attack_y, attack_x)]
					attack_this_mob.health_stat.alter(-self.damage)
					if attack_this_mob.health == 0:
						attack_this_mob.die(game)

				except KeyError:
					successful = False
					return_message = "You don't hit anything!"

				mob.stamina_stat.alter(-self.stamina_cost)

			else:
				successful = False
				return_message = "Not enough stamina!"

		mob.update_stage = 2

		# might want to change this to something different if not successful (ex. only half the recover time?)
		mob.next_update_time = game.timer.time + self._calc_recover_time(mob.speed)

		return successful, return_message