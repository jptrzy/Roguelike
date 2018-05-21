# -*- coding: utf-8 -*- 

class Action(object):
	def __init__(self, cast_time, recover_time):

		self.cast_time = cast_time
		self.recover_time = recover_time

	def _calc_prep_time(self, speed):
		return float(self.cast_time) / (float(speed) / 100)

	def _calc_recover_time(self, speed):
		return float(self.recover_time) / (float(speed) / 100)

	def prep(self, mob, current_time):
		mob.next_update_time = current_time + self._calc_prep_time(mob.speed.value)
		mob.current_action = self
		mob.update_stage = 1

class Movement_Action(Action):
	def __init__(self, cast_time, recover_time, stamina_cost):
		Action.__init__(self, cast_time, recover_time)
		self.stamina_cost = stamina_cost

	def do(self, game, mob, y, x):
		mob.move_to_cord(y, x)
		mob.stamina.alter(-self.stamina_cost)
		mob.update_stage = 2
		mob.next_update_time = game.timer.time + self._calc_recover_time(mob.speed.value)

class Idle_Action(Action):
	def __init__(self):
		Action.__init__(self, 50, 50)

	def do(self, game, mob):
		mob.update_stage = 2
		mob.next_update_time = game.timer.time + self._calc_recover_time(mob.speed.value)

class Attack(Action):
	def __init__(self, cast_time, recover_time, stamina_cost, damage):
		Action.__init__(self, cast_time, recover_time)
		self.stamina_cost = stamina_cost
		self.damage = damage

	def do(self, game, mob, attack_y, attack_x, mob_dictionary):
		successful = True
		try:
			attack_this_mob = mob_dictionary[(attack_y, attack_x)]
			attack_this_mob.health.alter(-self.damage)
			if attack_this_mob.health.value == 0:
				attack_this_mob.die(game)

		except KeyError:
			successful = False # -----------------------------------------------        

		mob.update_stage = 2
		mob.next_update_time = game.timer.time + self._calc_recover_time(mob.speed.value)

		game.update_screen()

		return successful

a_Walk = Movement_Action(0.1, 1, 0.2)
a_Sprint = Movement_Action(0.1, 0.5, 3)

a_Idle = Idle_Action()

a_testAttack = Attack(0.1, 2, 5, 10)
a_smite = Attack(cast_time=0.1, recover_time=2, stamina_cost=5, damage=10000000)