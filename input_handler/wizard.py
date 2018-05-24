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
		self.prev_request = 'help'

	def process_request(self, request, game):
		request = request.split()

		if request[0] == '\\':
			request = self.prev_request

		if request[0] == 'help':
			pass

		if request[0] == 'wait':
			try:
				time_advance = int(request[1])
				game.update(game.timer.time+time_advance)
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

		if request[0] == 'destroy':
			try:
				y, x = int(request[1]), int(request[2])
			except:
				y, x = self.prompt_coordinates(game)
			destructable_tiles = game.world.layers.get_destructable_tiles(game.me.y+y, game.me.x+x)

			if len(destructable_tiles) == 0:
				windows.pure_text_popup(("No destructable tiles found.", [255,0,0]), game=game)
			else:
				options = []

				for tile in destructable_tiles:
					options.append(tile.name)

				destroy_prompt = windows.scroll_selection_popup("Destroy which tile?", options, game=game)
				destroy_tile_name = destroy_prompt.init()

				if destroy_tile_name is not None:
					destroy_tile = next((tile for tile in destructable_tiles if tile.name == destroy_tile_name), None)

				game.world.layers.delete_tile(game.me.y+y, game.me.x+x, destroy_tile)
				game.update_screen()

		self.prev_request = request

	def prompt_coordinates(self, game):
		while True:
			prompt_coordinates = windows.text_input_popup("Enter relative y and x coordinates (separate by space):", game=game, only_ascii=False)
			coordinates = prompt_coordinates.init().split()

			try:
				y, x = int(coordinates[0]), int(coordinates[1])
				break
			except:
				windows.pure_text_popup(("Please enter two valid numerical coordinates.", (255,0,0)),game=game)

		return y, x

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
			y, x = self.prompt_coordinates(game)

		return id_, y, x
		
