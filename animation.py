# handles animations

from bearlibterminal import terminal

import weather
import random

class anim_handler(object):
	def __init__(self):
		self.weather_delay = 0

	def anim_loop(self, game):
	#	weather
		if weather.currentweather == weather.rain:
			if self.weather_delay == 10:
				self.weather_loop(game)
			else:
				self.weather_delay += 1

	def weather_loop(self, game):
		return
		game.world.printview(game)
		return
		map = game.world
		window_top_y = game.me.y - map.w_ylen
		window_top_x = game.me.x - map.w_xlen
		map.printview(game)
		self.weather_delay = 0
		for tilecoord in map.visible_tiles:
			window_y = tilecoord[0] - window_top_y
			window_x = tilecoord[1] - window_top_x
			if (window_y >= 0 and window_x >= 0) and (window_y <= map.w_ylen and window_x <= map.w_xlen):
				terrain_tile = map.visible_tiles[tilecoord][0][0]
				if terrain_tile.weather_sens:
					if random.randint(0, 6) == 0:
						map.wterrain.put(window_y, window_x, terrain_tile.icon, [127,255,212])