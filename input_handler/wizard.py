# -*- coding: utf-8 -*- 
import weather
from tiles_data import tiles
import time
import math
import wizard

from bearlibterminal import terminal

from mobs import mobs
import action
from window import windows

class wizard_commands(object):
	def __init__(self):
		pass

	def process_request(self, request, game):
		request = request.split()

		if request[0] == 'help':
			pass

		if request[0] == 'wait':
			try:
				time_advance = int(request[1])
				game.update(time_advance)
				game.update_screen()
				game.message_panel.add_phrase('Time advanced by ' + str(time_advance))
				game.message_panel.print_messages()	
			except IndexError:
				windows.pure_text_popup(("Please enter a time increment.", (255,0,0)), game=game)

		if request[0] == 'spawn':
			mob_id, y, x = self.create_obj(game, request, game.mob_generator)
			game.mob_generator.create_mob(mob_id, game.me.y+y, game.me.x+x)
			game.update_screen()

		if request[0] == 'construct':
			tile_id, y, x = self.create_obj(game, request, game.tile_generator)
			game.tile_generator.create_tile(tile_id, game.me.y+y, game.me.x+x)
			game.update_screen()

	def create_obj(self, game, request, generator):
		# "spawn", "spawn id_ y x", "spawn id_"
		id_ = ''

		if len(request) > 1:
			id_ = request[1]

		if id_ not in generator.data.keys():
			create_id_prompt = windows.scroll_selection_popup("Create what? (select by id):", generator.data.keys(), game)
			id_ = create_id_prompt.init()

		try:
			y, x = int(request[2]), int(request[3])
		except:
			while True:
				prompt_coordinates = windows.text_input_popup("Enter relative y and x coordinates (separate by space):", game=game)
				coordinates = prompt_coordinates.init().split()

				try:
					y, x = int(coordinates[0]), int(coordinates[1])
					break
				except:
					windows.pure_text_popup(("Please enter two valid numerical coordinates.", (255,0,0)),game=game)

		return id_, y, x
		
